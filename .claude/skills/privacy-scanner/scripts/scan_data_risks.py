#!/usr/bin/env python3
"""
scan_data_risks.py — 检测危险数据处理模式

检测：
1. 敏感数据明文写入日志（console.log、print、logger 等）
2. 弱加密/哈希算法（MD5、SHA1 用于密码、Base64 当加密）
3. HTTP 明文传输（非 HTTPS 的 API 调用）
4. 敏感数据存入 localStorage / cookie（前端）
5. 数据库查询未过滤直接日志输出
6. 明文存储密码（不加盐不哈希）
"""

import os
import re
import json
import argparse
from pathlib import Path

# 危险数据处理规则
# 格式：(规则名, 正则, 风险等级, 描述, 修复建议)
DATA_RISK_PATTERNS = [
    # ---- 高风险：日志泄露 ----
    (
        '日志输出敏感字段',
        r'(?i)(?:console\.log|console\.error|print\(|logger\.\w+\(|log\.(?:info|warn|error|debug)\()[^)]*(?:password|passwd|pwd|secret|token|key|phone|mobile|id_card|credit_card|ssn)',
        'HIGH',
        '敏感字段（密码/Token/手机号等）可能被输出到日志',
        '移除日志中的敏感字段，或在输出前脱敏（如 mask_phone("138****1234")）',
    ),
    (
        '直接序列化用户对象到日志',
        r'(?i)(?:console\.log|print\(|logger\.\w+\()[^)]*(?:user|account|profile|member)\b',
        'MEDIUM',
        '用户对象被直接打印到日志，可能包含 PII',
        '使用白名单字段序列化用户对象，避免打印完整 user 对象',
    ),

    # ---- 高风险：弱加密/哈希 ----
    (
        'MD5 用于密码哈希',
        r'(?i)(?:md5|MD5)\s*\([^)]*(?:password|passwd|pwd)[^)]*\)',
        'HIGH',
        'MD5 用于密码哈希，已被证明不安全（可被彩虹表破解）',
        '改用 bcrypt、argon2 或 PBKDF2，并加随机 salt',
    ),
    (
        'SHA1 用于密码哈希',
        r'(?i)sha1\s*\([^)]*(?:password|passwd|pwd)[^)]*\)',
        'HIGH',
        'SHA1 用于密码哈希，已被证明不安全',
        '改用 bcrypt、argon2 或 PBKDF2，并加随机 salt',
    ),
    (
        'Base64 当加密使用',
        r'(?i)base64[._]?(?:encode|decode)\s*\([^)]*(?:password|passwd|pwd|secret|key)[^)]*\)',
        'HIGH',
        'Base64 是编码而非加密，不能用于保护敏感数据',
        '使用 AES-256-GCM 或其他对称加密算法',
    ),
    (
        '明文密码存储',
        r'(?i)(?:INSERT|UPDATE)\s+.*\b(?:password|passwd|pwd)\b\s*[=,]\s*["\'][^"\']+["\']',
        'HIGH',
        'SQL 语句中可能存在明文密码存储',
        '存储前使用 bcrypt/argon2 哈希处理',
    ),

    # ---- 高风险：HTTP 明文传输 ----
    (
        'HTTP 明文 API 调用',
        r'["\']http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)[^"\']+["\']',
        'MEDIUM',
        '代码中存在非 localhost 的 HTTP（非 HTTPS）URL，可能明文传输敏感数据',
        '生产环境所有 API 调用改用 HTTPS',
    ),

    # ---- 中风险：前端不安全存储 ----
    (
        'localStorage 存储敏感数据',
        r'localStorage\.setItem\s*\(\s*["\'][^"\']*(?:token|password|secret|key|user_id|phone)[^"\']*["\']',
        'MEDIUM',
        'localStorage 将数据存储在浏览器本地，XSS 攻击可读取',
        '敏感 Token 使用 httpOnly Cookie；用户偏好等非敏感数据才用 localStorage',
    ),
    (
        'sessionStorage 存储敏感数据',
        r'sessionStorage\.setItem\s*\(\s*["\'][^"\']*(?:token|password|secret|key)[^"\']*["\']',
        'MEDIUM',
        'sessionStorage 同样可被 XSS 读取',
        '使用 httpOnly Cookie 替代',
    ),
    (
        'Cookie 不安全设置',
        r'document\.cookie\s*=\s*["\'][^"\']*(?:token|session|auth)[^"\']*(?!httpOnly|Secure)',
        'MEDIUM',
        '通过 document.cookie 设置的 Cookie 缺少 httpOnly/Secure 标志',
        '使用服务端 Set-Cookie 并添加 HttpOnly; Secure; SameSite=Strict',
    ),

    # ---- 中风险：SQL 注入风险（数据泄露角度）----
    (
        'SQL 字符串拼接',
        r'(?i)(?:SELECT|INSERT|UPDATE|DELETE).*\+\s*(?:req\.|request\.|params\.|query\.|body\.|input)',
        'HIGH',
        'SQL 语句直接拼接用户输入，存在 SQL 注入风险（可导致数据泄露）',
        '使用参数化查询（Prepared Statements）或 ORM',
    ),

    # ---- 中风险：不安全的随机数 ----
    (
        '不安全随机数用于安全场景',
        r'(?i)Math\.random\(\)|random\.random\(\)|rand\(\)',
        'LOW',
        '伪随机数不适合用于 Token、验证码、密钥生成',
        '使用 crypto.randomBytes()（Node.js）或 secrets 模块（Python）',
    ),

    # ---- 低风险：调试代码遗留 ----
    (
        '调试代码遗留（TODO/FIXME 含敏感词）',
        r'(?i)(?:TODO|FIXME|HACK|XXX)[^\n]*(?:password|token|secret|key|auth)',
        'LOW',
        '代码注释中包含关于敏感数据处理的待办项，可能尚未完成安全修复',
        '清理注释并确认相关安全问题已解决',
    ),
]

SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.next', 'coverage'}
SCAN_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.php', '.go', '.java', '.rb',
    '.cs', '.vue', '.svelte', '.html', '.sql',
}


def scan_file(file_path: Path, target: Path) -> list:
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return []

    findings = []
    lines = content.splitlines()

    for rule_name, pattern, risk, description, recommendation in DATA_RISK_PATTERNS:
        compiled = re.compile(pattern, re.MULTILINE)
        matched_lines = []

        for i, line in enumerate(lines, 1):
            if compiled.search(line):
                matched_lines.append((i, line.strip()[:120]))
                if len(matched_lines) >= 5:
                    break

        if matched_lines:
            findings.append({
                'rule': rule_name,
                'risk': risk,
                'description': description,
                'recommendation': recommendation,
                'file': str(file_path.relative_to(target)),
                'matches': len(matched_lines),
                'locations': matched_lines,
            })

    return findings


def scan_directory(target_path: str) -> dict:
    target = Path(target_path)
    results = {
        'target': str(target.resolve()),
        'total_files_scanned': 0,
        'findings': [],
    }

    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            file_path = Path(root) / filename
            if file_path.suffix.lower() not in SCAN_EXTENSIONS:
                continue

            results['total_files_scanned'] += 1
            file_findings = scan_file(file_path, target)
            if file_findings:
                results['findings'].extend(file_findings)

    high = [f for f in results['findings'] if f['risk'] == 'HIGH']
    medium = [f for f in results['findings'] if f['risk'] == 'MEDIUM']
    low = [f for f in results['findings'] if f['risk'] == 'LOW']

    results['summary'] = {
        'files_scanned': results['total_files_scanned'],
        'total_findings': len(results['findings']),
        'high_risk': len(high),
        'medium_risk': len(medium),
        'low_risk': len(low),
    }

    return results


def main():
    parser = argparse.ArgumentParser(description='检测危险数据处理模式')
    parser.add_argument('target', help='扫描目标路径')
    parser.add_argument('--output', default='/tmp/data_risks_result.json', help='输出 JSON 文件路径')
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f'错误：路径不存在 {args.target}')
        exit(1)

    result = scan_directory(args.target)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    summary = result['summary']
    print(f"✅ 数据风险扫描完成：{summary['files_scanned']} 个文件")
    print(f"   🔴 高风险：{summary['high_risk']} 处")
    print(f"   🟡 中风险：{summary['medium_risk']} 处")
    print(f"   🟢 低风险：{summary['low_risk']} 处")
    print(f"📄 结果保存至：{args.output}")


if __name__ == '__main__':
    main()
