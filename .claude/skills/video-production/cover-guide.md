# YouTube 封面制作规范

> 参考风格：Nate Herk
> 参考实现：`assets/visuals/cover-v1.html`（DreamWise AI 001 期）
> 最后更新：2026-03-27

---

## 一、基本规格

| 属性 | 规范 |
|------|------|
| 尺寸 | 1280 × 720px（16:9）|
| 背景 | 纯黑 `#0d0d0f` + starfield 粒子点缀 |
| 字体 | Poppins 900（仅用一种字体）|
| 强调色 | Cyan `#00d4ff` 唯一强调色，禁止 Magenta |
| 最大元素数 | 4 个（标题 + 人物 + 图表/截图 + 频道名）|

---

## 二、布局结构（Nate Herk 风格）

```
┌─────────────────────────────────────────┐
│         BIG TITLE (top, full width)     │
│                                         │
│  [Person]     [Diagram / Screenshot]    │
│  bottom-left       center-right         │
│                                         │
│ • Channel Name                          │
└─────────────────────────────────────────┘
```

- **标题**：占满顶部，两行，字号 118px
- **人物**：左下角，底部对齐，融入深色背景
- **图表/截图**：右侧，与人物保持间距
- **频道名**：底部左下角，Cyan 圆点 + 大写小字

---

## 三、HTML 实现参数（已验证）

| 元素 | CSS 参数 |
|------|---------|
| 标题 | `font-size: 118px; font-weight: 900; top: 32px; text-align: center; padding: 0 48px` |
| 标题两行 | 用 `<br>` 手动换行，`white-space: normal` |
| Cyan 高亮 | `color: #00d4ff; text-shadow: 0 0 30px rgba(0,212,255,1), 0 0 60px rgba(0,212,255,0.6)` |
| 人物照片 | `position: absolute; bottom: 0; left: 10px; width: 560px; height: 580px` |
| 照片遮罩 | 四向渐变 mask（上下左右各方向淡出）|
| 图表位置 | `left: 720px; top: 260px`（与照片保持 ~160px 间距）|
| 频道标 | `bottom: 28px; left: 32px`，Cyan 8px 圆点 + 15px 大写字 |
| 背景 | starfield `radial-gradient` 粒子 + 右侧 Cyan 径向光晕 |

### 照片注意事项

- ❌ 不能用 `file://` 路径（浏览器安全策略阻止加载本地图片）
- ✅ 照片必须放在与 HTML 同目录，通过 HTTP server 以相对路径访问
- ✅ 统一命名为 `host-photo.png`，存放在 `assets/visuals/`
- 启动 HTTP server：`python3 -m http.server 8899`

### 缩放适配（必须加）

```html
<div class="scale-wrapper" id="scaleWrapper">
  <!-- 封面内容 -->
</div>
<script>
  function scaleToFit() {
    const wrapper = document.getElementById('scaleWrapper');
    const scale = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
    wrapper.style.transform = `scale(${scale})`;
  }
  scaleToFit();
  window.addEventListener('resize', scaleToFit);
</script>
```

`.scale-wrapper` CSS：
```css
.scale-wrapper {
  width: 1280px;
  height: 720px;
  transform-origin: center center;
}
```

---

## 四、导出为 PNG

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless=new \
  --screenshot=/path/to/cover-v1.png \
  --window-size=1280,720 \
  --hide-scrollbars \
  "http://localhost:8899/cover-v1.html"
```

输出：1280×720px，16:9，可直接上传 YouTube。

验证尺寸：
```bash
python3 -c "
import struct
with open('cover-v1.png','rb') as f:
    f.read(16)
    w = struct.unpack('>I', f.read(4))[0]
    h = struct.unpack('>I', f.read(4))[0]
    print(f'{w}x{h}')
"
```

---

## 五、颜色铁律

```
视觉层级：黑底 → 白色主标题 → Cyan 关键词高亮 → 真人照片
```

- ✅ 黑底 + 白字 + Cyan 高亮 = 对比度最强，移动端最抢眼
- ✅ Cyan 是品牌记忆点，每期封面统一使用
- ❌ 封面禁止 Magenta（Magenta 只在视频内部架构图使用）
- ❌ 不加装饰箭头（↷ 等符号在封面上显得杂乱）

---

## 六、A/B 测试建议

每期做两个版本，发布后 48 小时内切换测试：

| 版本 | 差异点 | 测试目标 |
|------|--------|---------|
| A | 问句标题（Does It Actually Learn?）| 悬念点击率 |
| B | 结论标题（The AI That Actually Learns）| 搜索点击率 |

---

## 七、制作流程

1. 确定标题（问句 > 结论 > 数字型）
2. 准备人物照片 → 存为 `host-photo.png` 放入 `assets/visuals/`
3. 启动 HTTP server：`python3 -m http.server 8899`
4. 复制 `cover-v1.html` 作为模板，修改标题和图表内容
5. 浏览器预览调整：http://localhost:8899/cover-vX.html
6. Chrome headless 导出 PNG
7. 验证尺寸 1280×720
