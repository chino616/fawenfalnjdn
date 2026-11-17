# CsI2021 r2 独立渲染预览

由 [validate_readability.mjs](../../validate_readability.mjs) 从同一版三份阅读文件生成。`detailed.html`、`summary.html`、`user_input.html` 为本地预览；对应的桌面、窄视口、章节和九条公式PNG用于人工目视核对。实际输入指纹、目录点击、链接和公式检查见 [READABILITY_CHECKS.json](../READABILITY_CHECKS.json)，目视结论见 [验收记录](../REVIEW_REPORT.md)。

预览依赖工作区独立验证环境中的KaTeX字体和样式，非可脱离该环境的正式发布文件。本次使用CommonMark/GFM、KaTeX与headless Edge，范围限于阅读性；不自动认证原文真实性或科学模型。

[上一级](../README.md)
