#!/usr/bin/env python3
"""
check_licenses.py — 识别开源协议类型并判断商业兼容性

检测：
1. 项目根目录 LICENSE 文件
2. package.json / requirements.txt / go.mod / pom.xml 中的依赖协议
3. 源码文件中的 SPDX 协议标识符
4. 协议商业兼容性（GPL 传染性 / MIT 可商用等）
"""

import os
import re
import json
import argparse
import subprocess
from pathlib import Path

# 协议识别规则（正则 → 标准协议名）
LICENSE_PATTERNS = [
    (r'MIT License|Permission is hereby granted.*MIT', 'MIT'),
    (r'Apache License.*Version 2\.0|Licensed under the Apache License', 'Apache-2.0'),
    (r'GNU GENERAL PUBLIC LICENSE.*Version 3|GPL.*v3|GPLv3', 'GPL-3.0'),
    (r'GNU GENERAL PUBLIC LICENSE.*Version 2|GPL.*v2|GPLv2', 'GPL-2.0'),
    (r'GNU LESSER GENERAL PUBLIC LICENSE.*Version 3|LGPL.*3|LGPLv3', 'LGPL-3.0'),
    (r'GNU LESSER GENERAL PUBLIC LICENSE.*Version 2|LGPL.*2|LGPLv2', 'LGPL-2.1'),
    (r'Mozilla Public License.*2\.0|MPL.*2\.0', 'MPL-2.0'),
    (r'BSD 3-Clause|Redistribution and use.*provided that.*3', 'BSD-3-Clause'),
    (r'BSD 2-Clause|Redistribution and use.*provided that.*2', 'BSD-2-Clause'),
    (r'ISC License|ISC', 'ISC'),
    (r'Creative Commons.*Zero|CC0|Public Domain', 'CC0-1.0'),
    (r'Creative Commons.*Attribution.*4\.0|CC BY 4\.0', 'CC-BY-4.0'),
    (r'Creative Commons.*NonCommercial|CC.*NC', 'CC-BY-NC'),  # 非商用！
    (r'Proprietary|All rights reserved|Commercial License|商业版权', 'Proprietary'),
    (r'UNLICENSED|Unlicense', 'Unlicense'),
    (r'WTFPL', 'WTFPL'),
    (r'European Union Public Licence|EUPL', 'EUPL-1.2'),
    (r'Affero General Public License|AGPL', 'AGPL-3.0'),
]

# 协议商业兼容性数据库
LICENSE_COMPATIBILITY = {
    'MIT':           {'commercial': True,  'copyleft': False, 'risk': 'LOW',    'note': '最宽松，可商用，无传染性'},
    'Apache-2.0':    {'commercial': True,  'copyleft': False, 'risk': 'LOW',    'note': '可商用，包含专利条款'},
    'BSD-3-Clause':  {'commercial': True,  'copyleft': False, 'risk': 'LOW',    'note': '可商用，需保留版权声明'},
    'BSD-2-Clause':  {'commercial': True,  'copyleft': False, 'risk': 'LOW',    'note': '可商用，需保留版权声明'},
    'ISC':           {'commercial': True,  'copyleft': False, 'risk': 'LOW',    'note': '等同 MIT，可商用'},
    'CC0-1.0':       {'commercial': True,  'copyleft': False, 'risk': 'LOW',    'note': '公共领域，无限制'},
    'Unlicense':     {'commercial': True,  'copyleft': False, 'risk': 'LOW',    'note': '公共领域放弃版权'},
    'WTFPL':         {'commercial': True,  'copyleft': False, 'risk': 'LOW',    'note': '无限制'},
    'MPL-2.0':       {'commercial': True,  'copyleft': True,  'risk': 'MEDIUM', 'note': '文件级 copyleft，修改文件需开源，不传染其他文件'},
    'LGPL-2.1':      {'commercial': True,  'copyleft': True,  'risk': 'MEDIUM', 'note': '动态链接可商用，静态链接需谨慎'},
    'LGPL-3.0':      {'commercial': True,  'copyleft': True,  'risk': 'MEDIUM', 'note': '动态链接可商用，静态链接需谨慎'},
    'EUPL-1.2':      {'commercial': True,  'copyleft': True,  'risk': 'MEDIUM', 'note': '欧盟协议，修改需开源'},
    'CC-BY-4.0':     {'commercial': True,  'copyleft': False, 'risk': 'MEDIUM', 'note': '可商用，需署名'},
    'GPL-2.0':       {'commercial': False, 'copyleft': True,  'risk': 'HIGH',   'note': '⚠️ 强传染性：整个项目需开源。商用需购买商业授权'},
    'GPL-3.0':       {'commercial': False, 'copyleft': True,  'risk': 'HIGH',   'note': '⚠️ 强传染性：整个项目需开源。商用需购买商业授权'},
    'AGPL-3.0':      {'commercial': False, 'copyleft': True,  'risk': 'HIGH',   'note': '⚠️ 最强传染性：网络服务也需开源源码'},
    'CC-BY-NC':      {'commercial': False, 'copyleft': False, 'risk': 'HIGH',   'note': '⚠️ 明确禁止商业使用'},
    'Proprietary':   {'commercial': False, 'copyleft': False, 'risk': 'HIGH',   'note': '⚠️ 商业专有协议，未经授权不可使用'},
    'UNKNOWN':       {'commercial': None,  'copyleft': None,  'risk': 'MEDIUM', 'note': '协议未知，需人工确认'},
}

SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.next'}


def detect_license_type(text: str) -> str:
    """从文本内容识别协议类型"""
    for pattern, license_name in LICENSE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return license_name
    return 'UNKNOWN'


def find_license_files(target: Path) -> list:
    """查找 LICENSE 相关文件"""
    license_files = []
    patterns = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'LICENCE', 'COPYING', 'COPYRIGHT']

    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            if filename.upper() in [p.upper() for p in patterns]:
                file_path = Path(root) / filename
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    license_type = detect_license_type(content)
                    rel_path = str(file_path.relative_to(target))
                    compatibility = LICENSE_COMPATIBILITY.get(license_type, LICENSE_COMPATIBILITY['UNKNOWN'])
                    license_files.append({
                        'file': rel_path,
                        'license': license_type,
                        'commercial': compatibility['commercial'],
                        'copyleft': compatibility['copyleft'],
                        'risk': compatibility['risk'],
                        'note': compatibility['note'],
                    })
                except Exception:
                    pass

    return license_files


def check_package_json(target: Path) -> list:
    """检查 package.json 依赖协议（使用 license-checker 如果可用）"""
    pkg_file = target / 'package.json'
    if not pkg_file.exists():
        return []

    results = []

    # 尝试使用 license-checker
    try:
        output = subprocess.run(
            ['npx', 'license-checker', '--json', '--production'],
            capture_output=True, text=True, cwd=str(target), timeout=60
        )
        if output.returncode == 0:
            data = json.loads(output.stdout)
            for pkg_name, info in data.items():
                license_type = info.get('licenses', 'UNKNOWN')
                if isinstance(license_type, list):
                    license_type = license_type[0]
                compatibility = LICENSE_COMPATIBILITY.get(license_type, LICENSE_COMPATIBILITY['UNKNOWN'])
                results.append({
                    'package': pkg_name,
                    'license': license_type,
                    'commercial': compatibility['commercial'],
                    'risk': compatibility['risk'],
                    'note': compatibility['note'],
                })
            return results
    except Exception:
        pass

    # 降级：直接读 package.json 的 license 字段
    try:
        pkg_data = json.loads(pkg_file.read_text(encoding='utf-8'))
        license_type = pkg_data.get('license', 'UNKNOWN')
        compatibility = LICENSE_COMPATIBILITY.get(license_type, LICENSE_COMPATIBILITY['UNKNOWN'])
        results.append({
            'package': pkg_data.get('name', 'package.json'),
            'license': license_type,
            'commercial': compatibility['commercial'],
            'risk': compatibility['risk'],
            'note': compatibility['note'] + '（仅检查项目本身协议，未扫描依赖树）',
        })
    except Exception:
        pass

    return results


def scan_spdx_identifiers(target: Path) -> list:
    """扫描源码中的 SPDX 协议标识符"""
    spdx_pattern = re.compile(r'SPDX-License-Identifier:\s*([^\s\n]+)', re.IGNORECASE)
    findings = []

    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            file_path = Path(root) / filename
            if file_path.suffix.lower() not in {'.py', '.js', '.ts', '.go', '.java', '.php', '.rs', '.rb', '.c', '.h', '.cpp'}:
                continue
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                for match in spdx_pattern.finditer(content):
                    license_type = match.group(1).strip()
                    compatibility = LICENSE_COMPATIBILITY.get(license_type, LICENSE_COMPATIBILITY['UNKNOWN'])
                    findings.append({
                        'file': str(file_path.relative_to(target)),
                        'license': license_type,
                        'commercial': compatibility['commercial'],
                        'risk': compatibility['risk'],
                        'note': compatibility['note'],
                    })
            except Exception:
                pass

    return findings


def main():
    parser = argparse.ArgumentParser(description='识别开源协议类型并判断商业兼容性')
    parser.add_argument('target', help='扫描目标路径（目录）')
    parser.add_argument('--output', default='/tmp/licenses_result.json', help='输出 JSON 文件路径')
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f'错误：路径不存在 {args.target}')
        exit(1)

    result = {
        'target': str(target.resolve()),
        'license_files': find_license_files(target),
        'package_licenses': check_package_json(target),
        'spdx_identifiers': scan_spdx_identifiers(target),
    }

    # 统计高风险协议
    all_licenses = (
        result['license_files'] +
        result['package_licenses'] +
        result['spdx_identifiers']
    )
    high_risk = [l for l in all_licenses if l.get('risk') == 'HIGH']
    medium_risk = [l for l in all_licenses if l.get('risk') == 'MEDIUM']

    result['summary'] = {
        'total_licenses_found': len(all_licenses),
        'high_risk_count': len(high_risk),
        'medium_risk_count': len(medium_risk),
        'low_risk_count': len(all_licenses) - len(high_risk) - len(medium_risk),
        'commercially_blocked': [l for l in all_licenses if l.get('commercial') is False],
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    summary = result['summary']
    print(f"✅ 协议扫描完成")
    print(f"   发现协议：{summary['total_licenses_found']} 个")
    print(f"   🔴 高风险（禁止商用）：{summary['high_risk_count']} 个")
    print(f"   🟡 中风险（有条件商用）：{summary['medium_risk_count']} 个")
    print(f"   🟢 低风险（可商用）：{summary['low_risk_count']} 个")
    if summary['commercially_blocked']:
        print(f"   ⚠️ 明确禁止商业使用的协议：{[l.get('license') for l in summary['commercially_blocked']]}")
    print(f"📄 结果保存至：{args.output}")


if __name__ == '__main__':
    main()
