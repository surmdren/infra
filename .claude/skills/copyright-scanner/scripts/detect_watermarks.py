#!/usr/bin/env python3
"""
detect_watermarks.py — 检测商业软件特征码和水印

检测：
1. 国内常见商业系统特征字符串（微擎、CRMEB、FastAdmin 等）
2. 加密授权校验代码（License Key 验证逻辑）
3. 域名绑定/授权锁定代码
4. 混淆代码特征（eval + base64 常见于破解版）
"""

import os
import re
import json
import argparse
from pathlib import Path

# 商业软件特征库
# 格式：(软件名, 特征正则, 风险描述)
COMMERCIAL_SIGNATURES = [
    # 微擎
    ('微擎', r'WeEngine|we7|iphp|微擎|wengine', '检测到微擎商业框架特征'),
    ('微擎授权', r'check_auth\(\)|license_check|iphpKey', '微擎授权校验代码'),

    # CRMEB
    ('CRMEB', r'CRMEB|crmeb|crmeb\.com', '检测到 CRMEB 商业系统特征'),
    ('CRMEB授权', r'YansongdaSign|crmeb_sign|license\.crmeb', 'CRMEB 签名验证代码'),

    # FastAdmin
    ('FastAdmin', r'FastAdmin|fastadmin\.net|karsonzhang', '检测到 FastAdmin 商业框架特征'),

    # ThinkPHP 商业版
    ('ThinkPHP商业版', r'topthink\/think-auth|topthink\/framework.*license', 'ThinkPHP 商业版授权组件'),

    # Shopro / 商城系统
    ('Shopro', r'shopro|shop-pro\.cn', '检测到 Shopro 商城系统特征'),
    ('EasyShop', r'easyshop|easy-shop', '检测到 EasyShop 系统特征'),

    # 常见商业 CMS
    ('帝国CMS', r'EmpireCMS|empirecms', '检测到帝国 CMS 特征'),
    ('织梦CMS', r'DedeCMS|dedecms|dedeajax', '检测到织梦 CMS 特征（含商业版）'),
    ('PHPCMS', r'phpcms\.cn|PHPCMS V9', '检测到 PHPCMS 特征'),

    # SaaS 授权锁
    ('域名绑定授权', r'domain.*license|license.*domain|authorized_domain|bind_domain', '检测到域名绑定授权逻辑'),
    ('硬件指纹授权', r'machine_code|hardware_id|device_fingerprint.*license', '检测到硬件指纹授权逻辑'),

    # 加密/混淆特征（破解版常见）
    ('Base64混淆执行', r'eval\s*\(\s*base64_decode|eval\s*\(\s*gzinflate|eval\s*\(\s*str_rot13', '⚠️ 高危：eval+编码混淆，破解版常见手法'),
    ('JS混淆执行', r'eval\s*\(\s*atob\s*\(|new\s+Function\s*\(\s*atob', 'eval+atob JS 混淆执行'),

    # License Key 校验模式
    ('License校验', r'verify_license|check_license|validate_license|license_valid|license\.key', '许可证校验代码（可能是破解版残留）'),
    ('序列号校验', r'serial_number.*verify|verify.*serial_number|check_serial', '序列号验证逻辑'),

    # 版权水印字符串（常被破解版移除）
    ('版权声明锁', r'copyright.*cannot.*remove|不得删除.*版权|未经授权.*禁止', '含有不可删除版权声明的代码'),
]

# 加密文件特征（PHP 常见）
ENCRYPTED_FILE_PATTERNS = [
    r'^<\?php\s*\/\*[^*]*encoded[^*]*\*\/',  # Zend Guard 加密
    r'__halt_compiler\s*\(\)',  # ionCube 加密
    r'if\(!extension_loaded\(["\']ionCube',  # ionCube 检测
    r'sourceguardian',  # SourceGuardian
]

SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.next'}
SCAN_EXTENSIONS = {
    '.php', '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go',
    '.rb', '.cs', '.vue', '.svelte', '.html', '.tpl',
}


def scan_file(file_path: Path) -> list:
    """扫描单个文件，返回发现的特征列表"""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return []

    findings = []

    # 检查商业软件特征
    for software_name, pattern, description in COMMERCIAL_SIGNATURES:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            # 找到匹配行号
            lines_found = []
            for i, line in enumerate(content.splitlines(), 1):
                if re.search(pattern, line, re.IGNORECASE):
                    lines_found.append((i, line.strip()[:100]))
                    if len(lines_found) >= 3:  # 每个特征最多记录3处
                        break

            findings.append({
                'type': 'commercial_software',
                'software': software_name,
                'description': description,
                'pattern': pattern,
                'occurrences': len(matches),
                'locations': lines_found,
                'risk': 'HIGH' if ('混淆' in description or '破解' in description or '⚠️' in description) else 'MEDIUM',
            })

    # 检查加密文件
    for pattern in ENCRYPTED_FILE_PATTERNS:
        if re.search(pattern, content[:500], re.IGNORECASE):
            findings.append({
                'type': 'encrypted_file',
                'software': '加密保护文件',
                'description': '文件经过商业加密保护（Zend/ionCube/SourceGuardian），可能是商业软件',
                'pattern': pattern,
                'occurrences': 1,
                'locations': [(1, content.splitlines()[0][:100] if content else '')],
                'risk': 'HIGH',
            })
            break

    return findings


def scan_directory(target_path: str) -> dict:
    """扫描目录"""
    target = Path(target_path)
    results = {
        'target': str(target.resolve()),
        'total_files_scanned': 0,
        'findings': [],
        'high_risk_files': [],
        'medium_risk_files': [],
    }

    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            file_path = Path(root) / filename
            if file_path.suffix.lower() not in SCAN_EXTENSIONS:
                continue

            results['total_files_scanned'] += 1
            file_findings = scan_file(file_path)

            if file_findings:
                rel_path = str(file_path.relative_to(target))
                has_high = any(f['risk'] == 'HIGH' for f in file_findings)

                entry = {
                    'file': rel_path,
                    'findings': file_findings,
                    'max_risk': 'HIGH' if has_high else 'MEDIUM',
                }
                results['findings'].append(entry)

                if has_high:
                    results['high_risk_files'].append(rel_path)
                else:
                    results['medium_risk_files'].append(rel_path)

    results['summary'] = {
        'files_scanned': results['total_files_scanned'],
        'files_with_findings': len(results['findings']),
        'high_risk_files': len(results['high_risk_files']),
        'medium_risk_files': len(results['medium_risk_files']),
        'clean_files': results['total_files_scanned'] - len(results['findings']),
    }

    return results


def main():
    parser = argparse.ArgumentParser(description='检测商业软件特征码和水印')
    parser.add_argument('target', help='扫描目标路径（文件或目录）')
    parser.add_argument('--output', default='/tmp/watermarks_result.json', help='输出 JSON 文件路径')
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f'错误：路径不存在 {args.target}')
        exit(1)

    if target.is_file():
        findings = scan_file(target)
        result = {
            'target': str(target),
            'findings': [{'file': str(target), 'findings': findings}] if findings else [],
            'summary': {
                'files_scanned': 1,
                'files_with_findings': 1 if findings else 0,
                'high_risk_files': sum(1 for f in findings if f.get('risk') == 'HIGH'),
                'medium_risk_files': sum(1 for f in findings if f.get('risk') == 'MEDIUM'),
            }
        }
    else:
        result = scan_directory(args.target)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    summary = result.get('summary', {})
    print(f"✅ 扫描完成：{summary.get('files_scanned', 1)} 个文件")
    print(f"   🔴 高风险：{summary.get('high_risk_files', 0)} 个文件")
    print(f"   🟡 中风险：{summary.get('medium_risk_files', 0)} 个文件")
    print(f"📄 结果保存至：{args.output}")


if __name__ == '__main__':
    main()
