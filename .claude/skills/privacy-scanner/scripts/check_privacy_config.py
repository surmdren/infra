#!/usr/bin/env python3
"""
check_privacy_config.py — 检测配置文件中的隐私风险

检测：
1. .env 文件中的 PII 或弱密钥
2. Cookie 安全配置（HttpOnly、Secure、SameSite）
3. CORS 过度开放（Access-Control-Allow-Origin: *）
4. Session 配置（过期时间、安全标志）
5. JWT Secret 强度
6. 数据库连接字符串暴露
7. 日志级别配置（debug 模式泄露敏感数据）
"""

import os
import re
import json
import argparse
from pathlib import Path

CONFIG_RISK_RULES = [
    # ---- 高风险：凭据暴露 ----
    (
        '数据库密码明文配置',
        r'(?i)(?:DB_PASSWORD|DATABASE_PASSWORD|MYSQL_PASSWORD|POSTGRES_PASSWORD|MONGO_PASSWORD)\s*=\s*(?!your_|change_|placeholder|<|xxx|\$\{)[^\s#]{4,}',
        'HIGH',
        '配置文件中存在数据库密码明文',
        '使用 Secret 管理服务（AWS Secrets Manager / K8s Secret），不要在配置文件中存明文密码',
        ['.env', '.env.local', '.env.production', '.env.development', 'config.yml', 'config.yaml', 'application.yml', 'application.properties'],
    ),
    (
        'API Key 明文配置',
        r'(?i)(?:API_KEY|API_SECRET|ACCESS_KEY|SECRET_KEY|PRIVATE_KEY)\s*=\s*(?!your_|change_|placeholder|<|xxx|\$\{)[A-Za-z0-9+/\-_]{16,}',
        'HIGH',
        '配置文件中存在 API Key 明文',
        '使用环境变量注入，不要硬编码到配置文件中，并确保 .env 已加入 .gitignore',
        ['.env', '.env.local', '.env.production'],
    ),
    (
        'JWT Secret 过短或弱',
        r'(?i)JWT_SECRET\s*=\s*(?:secret|password|123456|jwt|test|dev)[^\s#]*',
        'HIGH',
        'JWT Secret 使用了弱密钥',
        '使用至少 32 字节的随机字符串作为 JWT Secret（可用 openssl rand -base64 32 生成）',
        ['.env', '.env.local', '.env.production', 'config.yml'],
    ),

    # ---- 高风险：CORS 过度开放 ----
    (
        'CORS 允许所有来源',
        r'(?i)(?:Access-Control-Allow-Origin|CORS_ORIGIN|cors.*origin)\s*[=:]\s*["\']?\*["\']?',
        'HIGH',
        'CORS 配置允许所有来源（*），可能导致 CSRF 和数据泄露',
        '将 CORS 来源限制为明确的域名列表，生产环境禁止使用 *',
        ['.env', '.env.production', 'config.yml', 'config.yaml', 'nginx.conf', '.htaccess'],
    ),

    # ---- 中风险：Cookie/Session 配置 ----
    (
        'Cookie 未设置 HttpOnly',
        r'(?i)(?:cookie|session).*(?:httponly|http_only)\s*[=:]\s*(?:false|0|no)',
        'MEDIUM',
        'Cookie 未设置 HttpOnly，JavaScript 可读取，存在 XSS 窃取风险',
        '所有认证相关 Cookie 必须设置 HttpOnly: true',
        ['config.yml', 'config.yaml', 'config.js', 'config.ts', 'settings.py', 'application.yml'],
    ),
    (
        'Cookie 未设置 Secure',
        r'(?i)(?:cookie|session).*(?:secure)\s*[=:]\s*(?:false|0|no)',
        'MEDIUM',
        'Cookie 未设置 Secure 标志，可能通过 HTTP 明文传输',
        '生产环境所有认证 Cookie 必须设置 Secure: true',
        ['config.yml', 'config.yaml', 'config.js', 'config.ts', 'settings.py'],
    ),
    (
        'Session 超时过长',
        r'(?i)(?:session.*(?:timeout|expire|ttl|max_age)|SESSION_TIMEOUT|SESSION_EXPIRE)\s*[=:]\s*(?:\d{7,}|[8-9]\d{5,})',
        'LOW',
        'Session 超时时间设置过长（超过 30 天），增加 Token 泄露风险',
        '建议 Session 超时不超过 7 天，敏感操作（支付、修改密码）使用更短的有效期',
        ['.env', 'config.yml', 'config.yaml'],
    ),

    # ---- 中风险：调试模式 ----
    (
        '生产环境开启 Debug 模式',
        r'(?i)(?:DEBUG|APP_DEBUG|NODE_ENV)\s*=\s*(?:true|1|development|debug)',
        'MEDIUM',
        'Debug 模式可能输出详细错误信息（含堆栈、SQL、配置），泄露系统细节',
        '生产环境设置 DEBUG=false 和 NODE_ENV=production',
        ['.env', '.env.production', 'config.yml'],
    ),
    (
        '日志级别过详细',
        r'(?i)(?:LOG_LEVEL|log.*level)\s*[=:]\s*["\']?(?:debug|trace|verbose)["\']?',
        'LOW',
        '日志级别设置为 debug/trace，可能记录大量含 PII 的调试信息',
        '生产环境日志级别设置为 info 或 warn',
        ['.env', '.env.production', 'config.yml', 'config.yaml', 'application.yml'],
    ),

    # ---- 中风险：数据库配置 ----
    (
        '数据库连接字符串含密码',
        r'(?i)(?:mongodb|mysql|postgres|redis|sqlite)(?:\+\w+)?://[^:]+:[^@]{4,}@',
        'HIGH',
        '数据库连接字符串中包含明文密码',
        '使用环境变量分离，不要在代码或配置中硬编码完整连接字符串',
        ['.env', '.env.local', '.env.production', 'config.yml', 'database.yml'],
    ),
]

SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.next'}


def scan_config_file(file_path: Path, target: Path) -> list:
    filename = file_path.name.lower()

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return []

    findings = []
    lines = content.splitlines()

    for rule_name, pattern, risk, description, recommendation, applicable_files in CONFIG_RISK_RULES:
        # 检查这个规则是否适用于当前文件类型
        if applicable_files and not any(filename.endswith(af.lstrip('.').lower()) or filename == af.lower().lstrip('./') for af in applicable_files):
            # 对通用配置文件也做检查
            if not any(ext in filename for ext in ['.env', '.yml', '.yaml', '.json', '.conf', '.ini', '.toml', '.properties']):
                continue

        compiled = re.compile(pattern, re.MULTILINE)
        matched_lines = []

        for i, line in enumerate(lines, 1):
            # 跳过注释行
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith(';'):
                continue
            if compiled.search(line):
                matched_lines.append((i, line.strip()[:120]))
                if len(matched_lines) >= 3:
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


def find_config_files(target: Path) -> list:
    """查找配置文件"""
    config_patterns = {
        '.env', '.env.local', '.env.production', '.env.development', '.env.staging',
        'config.yml', 'config.yaml', 'config.js', 'config.ts', 'config.json',
        'application.yml', 'application.properties', 'settings.py', 'database.yml',
        'nginx.conf', '.htaccess', 'docker-compose.yml', 'docker-compose.yaml',
    }
    config_extensions = {'.env', '.yml', '.yaml', '.conf', '.ini', '.toml', '.properties'}

    config_files = []
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            file_path = Path(root) / filename
            if filename.lower() in config_patterns or file_path.suffix.lower() in config_extensions or filename.startswith('.env'):
                config_files.append(file_path)

    return config_files


def check_gitignore(target: Path) -> list:
    """检查 .gitignore 是否忽略了敏感文件"""
    issues = []
    gitignore = target / '.gitignore'

    if not gitignore.exists():
        issues.append({
            'rule': '缺少 .gitignore',
            'risk': 'HIGH',
            'description': '项目根目录没有 .gitignore 文件，可能意外提交 .env 等敏感文件',
            'recommendation': '创建 .gitignore 并添加 .env、*.key、*.pem、secrets/ 等规则',
            'file': '.gitignore（缺失）',
            'matches': 1,
            'locations': [(0, '文件不存在')],
        })
        return issues

    content = gitignore.read_text(encoding='utf-8', errors='ignore')
    sensitive_patterns = ['.env', '*.pem', '*.key', 'secrets/']
    missing = [p for p in sensitive_patterns if p not in content]

    if missing:
        issues.append({
            'rule': '.gitignore 未覆盖敏感文件',
            'risk': 'MEDIUM',
            'description': f'.gitignore 中未包含以下敏感文件模式：{", ".join(missing)}',
            'recommendation': f'在 .gitignore 中添加：{chr(10).join(missing)}',
            'file': '.gitignore',
            'matches': len(missing),
            'locations': [(0, f'缺少规则: {", ".join(missing)}')],
        })

    return issues


def scan_directory(target_path: str) -> dict:
    target = Path(target_path)
    results = {
        'target': str(target.resolve()),
        'total_files_scanned': 0,
        'findings': [],
    }

    # 检查 .gitignore
    results['findings'].extend(check_gitignore(target))

    # 扫描配置文件
    config_files = find_config_files(target)
    for file_path in config_files:
        results['total_files_scanned'] += 1
        file_findings = scan_config_file(file_path, target)
        results['findings'].extend(file_findings)

    high = [f for f in results['findings'] if f['risk'] == 'HIGH']
    medium = [f for f in results['findings'] if f['risk'] == 'MEDIUM']
    low = [f for f in results['findings'] if f['risk'] == 'LOW']

    results['summary'] = {
        'config_files_scanned': results['total_files_scanned'],
        'total_findings': len(results['findings']),
        'high_risk': len(high),
        'medium_risk': len(medium),
        'low_risk': len(low),
    }

    return results


def main():
    parser = argparse.ArgumentParser(description='检测配置文件中的隐私风险')
    parser.add_argument('target', help='扫描目标路径')
    parser.add_argument('--output', default='/tmp/config_result.json', help='输出 JSON 文件路径')
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
    print(f"✅ 配置文件扫描完成：{summary['config_files_scanned']} 个配置文件")
    print(f"   🔴 高风险：{summary['high_risk']} 项")
    print(f"   🟡 中风险：{summary['medium_risk']} 项")
    print(f"   🟢 低风险：{summary['low_risk']} 项")
    print(f"📄 结果保存至：{args.output}")


if __name__ == '__main__':
    main()
