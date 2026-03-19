#!/usr/bin/env python3
"""
scan_pii.py — 扫描源码中的 PII（个人身份信息）硬编码

检测：
1. 中国大陆手机号、身份证号、银行卡号
2. 邮箱地址（在赋值/硬编码上下文中）
3. 密码、API Key、Token 硬编码
4. 护照号、车牌号
"""

import os
import re
import json
import argparse
from pathlib import Path

# PII 正则规则库
# 格式：(规则名, 正则, 风险等级, 描述, 是否需要上下文确认)
PII_PATTERNS = [
    # ---- 高风险：直接标识符 ----
    (
        '中国大陆手机号',
        r'(?<![0-9])1[3-9]\d{9}(?![0-9])',
        'HIGH',
        '发现疑似中国大陆手机号',
        True,  # 需要上下文确认（避免误报版本号等）
    ),
    (
        '身份证号',
        r'(?<![0-9])[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx](?![0-9])',
        'HIGH',
        '发现疑似中国居民身份证号码',
        False,
    ),
    (
        '银行卡号',
        r'(?<![0-9])[3-6]\d{15,18}(?![0-9])',
        'HIGH',
        '发现疑似银行卡号（16-19位数字）',
        True,
    ),
    (
        '护照号',
        r'[EeGg][0-9]{8}',
        'HIGH',
        '发现疑似中国护照号',
        True,
    ),

    # ---- 高风险：凭据硬编码 ----
    (
        '密码硬编码',
        r'(?i)(?:password|passwd|pwd|secret)\s*[=:]\s*["\'][^"\']{6,}["\']',
        'HIGH',
        '发现硬编码密码',
        False,
    ),
    (
        'API Key 硬编码',
        r'(?i)(?:api[-_]?key|apikey|access[-_]?key|secret[-_]?key)\s*[=:]\s*["\'][A-Za-z0-9+/\-_]{16,}["\']',
        'HIGH',
        '发现硬编码 API Key',
        False,
    ),
    (
        'JWT Token 硬编码',
        r'eyJ[A-Za-z0-9+/\-_]{20,}\.[A-Za-z0-9+/\-_]{20,}\.[A-Za-z0-9+/\-_]{20,}',
        'HIGH',
        '发现硬编码 JWT Token',
        False,
    ),
    (
        'AWS 凭据',
        r'(?:AKIA|ASIA|AROA|AIDA)[A-Z0-9]{16}',
        'HIGH',
        '发现 AWS Access Key ID',
        False,
    ),
    (
        '私钥标志',
        r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----',
        'HIGH',
        '发现硬编码私钥',
        False,
    ),

    # ---- 中风险：间接标识符 ----
    (
        '邮箱硬编码',
        r'(?i)(?:email|mail|e-mail)\s*[=:]\s*["\'][A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}["\']',
        'MEDIUM',
        '发现硬编码邮箱地址',
        False,
    ),
    (
        '车牌号',
        r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤川青藏琼宁夏][A-Z][A-Z0-9]{5}',
        'MEDIUM',
        '发现疑似车牌号',
        True,
    ),
    (
        'IP 地址硬编码',
        r'(?<![0-9])(?:192\.168|10\.\d+|172\.(?:1[6-9]|2\d|3[01]))\.\d+\.\d+(?![0-9])',
        'LOW',
        '发现内网 IP 地址硬编码（可能暴露内部网络结构）',
        False,
    ),
]

# 上下文过滤：如果匹配内容周围包含这些词，降低可信度（减少误报）
CONTEXT_WHITELIST = [
    r'test|mock|example|sample|demo|fake|dummy|placeholder|xxx|000000|123456',
    r'//.*|#.*|/\*.*\*/',  # 注释行（简化判断）
]

SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.next', 'coverage'}
SCAN_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.php', '.go', '.java', '.rb',
    '.cs', '.vue', '.svelte', '.html', '.tpl', '.ejs', '.env', '.config',
    '.yml', '.yaml', '.json', '.toml', '.xml', '.sh', '.bash',
}


def is_likely_test_or_example(line: str) -> bool:
    """判断这行是否像测试/示例代码（降低误报）"""
    test_patterns = re.compile(
        r'test|mock|example|sample|demo|fake|dummy|placeholder|xxx+|000000|12345678|11111111',
        re.IGNORECASE
    )
    return bool(test_patterns.search(line))


def scan_file(file_path: Path, target: Path) -> list:
    """扫描单个文件，返回 PII 发现列表"""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return []

    findings = []
    lines = content.splitlines()

    for rule_name, pattern, risk, description, needs_context in PII_PATTERNS:
        compiled = re.compile(pattern)
        matched_lines = []

        for i, line in enumerate(lines, 1):
            if compiled.search(line):
                # 对需要上下文确认的规则，检查是否是测试代码
                if needs_context and is_likely_test_or_example(line):
                    continue
                matched_lines.append((i, line.strip()[:120]))
                if len(matched_lines) >= 5:
                    break

        if matched_lines:
            findings.append({
                'rule': rule_name,
                'risk': risk,
                'description': description,
                'file': str(file_path.relative_to(target)),
                'matches': len(matched_lines),
                'locations': matched_lines,
            })

    return findings


def scan_directory(target_path: str) -> dict:
    """扫描目录中的所有文件"""
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
            if file_path.suffix.lower() not in SCAN_EXTENSIONS and filename not in {'.env', '.env.local', '.env.production'}:
                continue

            results['total_files_scanned'] += 1
            file_findings = scan_file(file_path, target)

            if file_findings:
                results['findings'].extend(file_findings)

    # 统计
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
    parser = argparse.ArgumentParser(description='扫描源码中的 PII 硬编码')
    parser.add_argument('target', help='扫描目标路径')
    parser.add_argument('--output', default='/tmp/pii_result.json', help='输出 JSON 文件路径')
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
    print(f"✅ PII 扫描完成：{summary['files_scanned']} 个文件")
    print(f"   🔴 高风险（PII硬编码/凭据泄露）：{summary['high_risk']} 处")
    print(f"   🟡 中风险：{summary['medium_risk']} 处")
    print(f"   🟢 低风险：{summary['low_risk']} 处")
    print(f"📄 结果保存至：{args.output}")


if __name__ == '__main__':
    main()
