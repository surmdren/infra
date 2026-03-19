#!/usr/bin/env python3
"""
scan_headers.py — 扫描源码文件的版权声明头

检测：
1. 缺少版权声明头的文件
2. 版权声明引用了第三方公司/个人（可能是盗用代码）
3. 版权声明被注释掉或删除的痕迹
"""

import os
import re
import json
import argparse
from pathlib import Path

# 支持扫描的源码文件类型
SOURCE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.php',
    '.rb', '.cs', '.cpp', '.c', '.h', '.swift', '.kt', '.rs',
    '.vue', '.svelte', '.scala', '.dart', '.lua',
}

# 版权声明模式
COPYRIGHT_PATTERNS = [
    r'copyright\s*[\(©]?\s*\d{4}',
    r'©\s*\d{4}',
    r'\(c\)\s*\d{4}',
    r'license[d]?\s+under',
    r'spdx-license-identifier',
    r'all rights reserved',
]

# 第三方公司/项目名称特征（可能表示代码来源于其他项目）
THIRD_PARTY_PATTERNS = [
    r'copyright.*微擎', r'copyright.*wengine',
    r'copyright.*crmeb', r'copyright.*fastadmin',
    r'copyright.*thinkphp', r'copyright.*shopro',
    r'copyright.*ecshop', r'copyright.*discuz',
    r'copyright.*dedecms', r'copyright.*wordpress',
    r'copyright.*laravel', r'copyright.*symfony',
    r'(c)\s+\d{4}\s+(?!your|company|author)',  # 通用第三方标记
]

# 被删除/注释掉版权声明的痕迹
REMOVED_COPYRIGHT_PATTERNS = [
    r'//\s*copyright\s+removed',
    r'#\s*copyright\s+removed',
    r'\/\*\s*copyright.*\*\/',  # 单行注释掉的版权声明
    r'license\s*=\s*["\']remove["\']',
    r'@license\s+none',
]

SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.next', 'vendor'}


def scan_file(file_path: Path) -> dict:
    """扫描单个文件的版权声明情况"""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return None

    # 只检查前 30 行（版权声明通常在文件头部）
    head = '\n'.join(content.splitlines()[:30]).lower()
    full_lower = content.lower()

    result = {
        'file': str(file_path),
        'has_copyright': False,
        'third_party_copyright': [],
        'removed_copyright': [],
        'copyright_text': None,
    }

    # 检查是否有版权声明
    for pattern in COPYRIGHT_PATTERNS:
        match = re.search(pattern, head, re.IGNORECASE)
        if match:
            result['has_copyright'] = True
            # 提取版权声明原文（所在行）
            for line in content.splitlines()[:30]:
                if re.search(pattern, line, re.IGNORECASE):
                    result['copyright_text'] = line.strip()
                    break
            break

    # 检查第三方版权
    if result['has_copyright']:
        for pattern in THIRD_PARTY_PATTERNS:
            match = re.search(pattern, head, re.IGNORECASE)
            if match:
                result['third_party_copyright'].append(match.group(0))

    # 检查被删除的版权痕迹
    for pattern in REMOVED_COPYRIGHT_PATTERNS:
        match = re.search(pattern, full_lower)
        if match:
            result['removed_copyright'].append(match.group(0))

    return result


def scan_directory(target_path: str) -> dict:
    """扫描目录中所有源码文件"""
    target = Path(target_path)
    results = {
        'target': str(target.resolve()),
        'total_files_scanned': 0,
        'missing_copyright': [],
        'third_party_copyright': [],
        'removed_copyright': [],
        'has_copyright': [],
    }

    for root, dirs, files in os.walk(target):
        # 跳过不需要扫描的目录
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            file_path = Path(root) / filename
            if file_path.suffix.lower() not in SOURCE_EXTENSIONS:
                continue

            results['total_files_scanned'] += 1
            scan_result = scan_file(file_path)
            if scan_result is None:
                continue

            rel_path = str(file_path.relative_to(target))

            if scan_result['removed_copyright']:
                results['removed_copyright'].append({
                    'file': rel_path,
                    'matches': scan_result['removed_copyright'],
                })

            if scan_result['third_party_copyright']:
                results['third_party_copyright'].append({
                    'file': rel_path,
                    'matches': scan_result['third_party_copyright'],
                    'copyright_text': scan_result['copyright_text'],
                })
            elif not scan_result['has_copyright']:
                results['missing_copyright'].append(rel_path)
            else:
                results['has_copyright'].append(rel_path)

    # 生成摘要
    results['summary'] = {
        'files_scanned': results['total_files_scanned'],
        'missing_copyright_count': len(results['missing_copyright']),
        'third_party_count': len(results['third_party_copyright']),
        'removed_copyright_count': len(results['removed_copyright']),
        'clean_count': len(results['has_copyright']),
    }

    return results


def main():
    parser = argparse.ArgumentParser(description='扫描源码版权声明头')
    parser.add_argument('target', help='扫描目标路径（文件或目录）')
    parser.add_argument('--output', default='/tmp/headers_result.json', help='输出 JSON 文件路径')
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f'错误：路径不存在 {args.target}')
        exit(1)

    if target.is_file():
        result = {'target': str(target), 'files': [scan_file(target)]}
    else:
        result = scan_directory(args.target)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    summary = result.get('summary', {})
    print(f"✅ 扫描完成：{summary.get('files_scanned', 1)} 个文件")
    print(f"   缺少版权声明：{summary.get('missing_copyright_count', 0)} 个")
    print(f"   第三方版权：{summary.get('third_party_count', 0)} 个")
    print(f"   疑似删除版权：{summary.get('removed_copyright_count', 0)} 个")
    print(f"📄 结果保存至：{args.output}")


if __name__ == '__main__':
    main()
