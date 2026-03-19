# 国内商业软件特征码库

供 `detect_watermarks.py` 参考，也可用于人工核查。

---

## 微擎（WeEngine）

**特征字符串**：`WeEngine`、`we7`、`iphp`、`微擎`、`wengine`
**授权校验**：`check_auth()`、`license_check`、`iphpKey`
**识别方法**：
- 文件头部通常包含 `@copyright WeEngine` 或 `@link https://www.weengine.com`
- 核心目录结构：`/framework/`、`/source/`、`/addons/`
- 数据库表前缀通常为 `ims_`

**风险说明**：微擎是付费商业框架，破解版在国内流传广泛。使用破解版存在法律风险且无法获得官方支持。

---

## CRMEB

**特征字符串**：`CRMEB`、`crmeb`、`crmeb.com`
**授权校验**：`YansongdaSign`、`crmeb_sign`、`license.crmeb`
**识别方法**：
- Composer 包名包含 `crmeb/`
- 数据库表前缀 `eb_`
- 配置文件中 `crmeb_key`

**风险说明**：CRMEB 开源版（MIT）可免费使用，但商业版需购买授权。注意区分版本。

---

## FastAdmin

**特征字符串**：`FastAdmin`、`fastadmin.net`、`karsonzhang`
**识别方法**：
- `composer.json` 中 `"topthink/think-*"` 相关包
- 后台目录 `/public/assets/js/backend/`
- 头部注释 `@link https://www.fastadmin.net`

**风险说明**：FastAdmin 基础版开源，插件市场和部分高级功能为商业授权。

---

## ThinkPHP 商业版 / 扩展

**特征字符串**：`topthink/think-auth`（商业版鉴权组件）
**注意**：ThinkPHP 框架本身是 Apache-2.0 开源协议，但部分官方扩展为商业授权。

---

## Shopro 商城

**特征字符串**：`shopro`、`shop-pro.cn`
**识别方法**：
- 数据库表前缀 `shopro_`
- 目录结构包含 `/shopro/` 模块

---

## 帝国 CMS（EmpireCMS）

**特征字符串**：`EmpireCMS`、`empirecms`
**官方协议**：商业软件，非开源
**识别方法**：目录结构 `/e/`、数据库表前缀 `phome_`

---

## 织梦 CMS（DedeCMS）

**特征字符串**：`DedeCMS`、`dedecms`、`dedeajax`
**官方协议**：国内免费（商业使用需购买授权），海外使用需授权
**识别方法**：目录 `/dede/`、`/templets/`，数据库前缀 `dede_`

---

## ECShop

**特征字符串**：`ECShop`、`ecshop`
**官方协议**：已停止维护，存在大量安全漏洞
**风险说明**：不建议在新项目中使用

---

## 常见加密保护标志

| 加密方式 | 特征代码 | 说明 |
|----------|---------|------|
| Zend Guard | `<?php /*` + 乱码 | PHP 商业文件加密 |
| ionCube | `__halt_compiler()` | 另一种 PHP 加密 |
| SourceGuardian | `sourceguardian` | PHP 加密 |
| eval+base64 | `eval(base64_decode(` | 破解版常用混淆 |
| eval+gzinflate | `eval(gzinflate(` | 破解版常用混淆 |

---

## 如何人工确认

1. Google 搜索特征字符串 + "破解" / "crack" / "nulled"
2. 在 GitHub 搜索相同代码片段
3. 检查 `composer.json` / `package.json` 中的包名和版本
4. 对比官方代码仓库的 git history
