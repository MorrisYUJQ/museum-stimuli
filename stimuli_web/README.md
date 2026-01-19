# 实验刺激网页（静态站点）

本目录用于**阅读刺激材料**的在线展示，便于在问卷里提供链接给受试者点击阅读。

## 目录结构

- `original.html`: 原文（未改写）
- `dyslexia_helper.html`: Dyslexia Helper（one-step）改写版本
- `dftgen.html`: DFT-GEN 改写版本
- `selected_items.json`: 本次抽取的 5 条样本（含锚点、来源链接、长度等）
- `questions.csv`: 题库（每条 5 题；CSV 便于导入问卷系统）
- `questions_review.md`: 题库可读版（用于快速检查与人工微调）

> 注：如果 `questions.csv` 正被 Excel 等程序打开，Windows 会锁文件导致脚本无法覆盖。
> 脚本会自动改写为 `questions_v2.csv` / `questions_review_v2.md`。

## 生成方式

在项目根目录运行：

```bash
conda activate py310
python prepare_stimuli_web.py
```

生成输出会写入 `stimuli_web/`。

## 在问卷里怎么放链接（推荐）

每条藏品在页面里都有锚点，`selected_items.json` 里有 `anchor` 字段。

你可以在问卷某一题的“阅读材料”按钮里填：

- 原文页：`original.html#<anchor>`
- Dyslexia Helper 页：`dyslexia_helper.html#<anchor>`
- DFT-GEN 页：`dftgen.html#<anchor>`

这样受试者点击后会直接跳到该条目。

### 可选：加一个“返回问卷”链接

三页顶部都有“返回问卷”按钮。你可以在链接后面追加：

- `?back=<你的问卷URL>`

例如：`dftgen.html?back=<问卷链接>#<anchor>`

## 部署（无代码平台，拖拽即可）

### Netlify（最省事）

1. 打开 Netlify（使用网页端）
2. 选择“Deploy manually / Drag and Drop”
3. 把整个 `stimuli_web/` 文件夹拖进去

部署完成后，Netlify 会给你一个公开链接。

## 部署（GitHub Pages）

适合你们要长期保留链接、并且多人协作时使用。

建议把 `stimuli_web/` 作为发布根目录，并使用 `index.html` 作为入口页（已生成）。

### 方式 A：直接把 `stimuli_web/` 内容作为仓库根目录

1. 新建一个 GitHub 仓库（例如 `museum-stimuli`）
2. 把 `stimuli_web/` 里的文件复制到仓库根目录（根目录下直接看到 `original.html` 等）
3. 在 GitHub 仓库设置里打开 Pages：
   - Settings → Pages
   - Source 选 `Deploy from a branch`
   - Branch 选 `main`（或 `master`）+ `/ (root)`
4. 保存后等待 1–2 分钟，Pages 会给你一个链接

### 方式 B：用 `/docs` 目录

1. 在仓库根目录创建 `docs/`
2. 把 `stimuli_web/` 的文件复制到 `docs/`
3. Settings → Pages → Branch 选 `main` + `/docs`

部署后建议访问入口页：`index.html`
（例如：`https://<用户名>.github.io/<仓库名>/index.html`）

### 本地预览（检查排版）

在项目根目录运行：

```bash
python -m http.server 8000
```

然后浏览器打开 `http://localhost:8000/stimuli_web/original.html`。

