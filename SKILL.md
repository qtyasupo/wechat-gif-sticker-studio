---
name: wechat-gif-sticker-studio
description: 为中文聊天表情包设计统一角色和网页端原生GIF提示词，接收成品后检查动图、制作微信上架文案及五张配图、打包并归档。用于从角色主题做到表情专辑发布材料，也支持只写提示词或只整理已有GIF。
---

# 微信 GIF 表情包工作室

围绕同一套角色，完成「设定 → 单张GIF提示词 → 用户生成或直接制作 → 成品检查 → 微信发布材料 → 打包归档」。从用户当前阶段开始，复用已完成内容。

## 交付方式

- 用户说「提示词」「我去网页端生成」：交付逐条独立完整的提示词和文件，不擅自生图、调用API或改成帧图集合成。
- 用户要实际GIF：优先用用户选择且实际可调用的原生GIF入口。不要把当前工具接口的限制说成整个图片模型不支持动画。检查返回的真实格式和帧数，不把静态PNG或改扩展名的文件当成动图。
- 当前工具不能直接输出GIF时，说明已确认的接口限制，提出连续关键帧或现有素材合成路径。不要悄悄把肢体动作替换成整张图片摇晃。
- 用户提供成品目录：先只读清点、提取参考帧、看角色画风再做材料。文件名里有「九宫格」不代表实际画面是九宫格，必须看图。

沿用已确认的数量、风格、语言、署名、目录和平台。没有数量时可先建议8张，不把8张当永久平台规定。缺少角色细节时可合理补全，不重复询问已有信息。

## 角色与提示词

读 [references/prompting.md](references/prompting.md)。完整案例：[小橘](examples/xiaoju-prompts.md)、[青衫小剑客](examples/swordsman-prompts.md)。

- 固定脸、发型或毛色、服装、配饰、比例、线条和配色。
- 每张对应一种聊天用途、短台词、不同姿态以及准备、执行、回位的循环。不能只换文字。
- 每条可独立复制：重复关键角色设定，写明单张动态GIF、动作顺序、固定中文、循环与构图。
- 参考图用于稳定身份；能否带参考图直接输出GIF，以当前网页入口或工具能力为准。
- 纯白背景不等于透明。未验证支持时不许诺网页GIF真透明。文字漂移时可建议无字动图加固定配字。

## 成品检查与适配

媒体脚本需Python 3和Pillow，机械转码另需FFmpeg。缺失依赖时明确报告；只写提示词不需要安装媒体依赖。

```bash
python scripts/sticker_pack.py audit --manifest /path/to/album.json --report /path/to/report.json
python scripts/sticker_pack.py prepare --source /path/to/gifs --output /path/to/new-upload-folder --size 240
```

`audit`检查尺寸、帧数、不同动画帧、时长、循环、重复文件、透明度、字数和配图。`prepare`只对现有GIF等比缩放、补边和生成首帧缩略图，不产生新肢体动作；输出目录必须是新目录。白底素材仍是白底，透明素材保留透明填边。

程序不能证明中文正确、动作自然、角色一致或符合最新平台规则。逐张看图，抽看中间帧，核对中文、手指、道具、边距与接缝。平台尺寸另做副本，保留原GIF。

## 微信发布材料

读 [references/wechat-publishing.md](references/wechat-publishing.md)。用户截图和当前提交页优先；[wechat-profile.json](references/wechat-profile.json)是可修改的工作流配置，不是永久官方规范。

完成名称、介绍、版权和赞赏引导语，实际计数字符。署名来自用户或已确认资料，不把本仓库作者名自动写进别人的作品。

| 位置 | 默认尺寸 | 重点 |
| --- | --- | --- |
| 横幅 | 750×400 | 可带背景，展示系列气质，默认不加字 |
| 封面 | 240×240 | 透明PNG、完整主体、无文字 |
| 聊天图标 | 50×50 | 透明PNG、头部特写、缩小仍清楚 |
| 赞赏引导 | 750×560 | 温和自愿、配套文案，无假付款按钮或二维码 |
| 赞赏致谢 | 750×750 | 感谢支持，延续同一角色与配色 |

先看参考帧。有可用内置图像工具时，用它生成或编辑插画，五张分别调用和检查，保留真实alpha。不要用程序绘图冒充AI插画，不擅自改用API。生成后可做必要的机械尺寸适配和压缩，不拉伸角色；遵循实际工具的具体使用约束。

```bash
python scripts/sticker_pack.py resize-asset --input generated.png --output cover.png --width 240 --height 240
```

默认等比补透明边；全背景图可选 `--fit crop`。透明素材不用JPEG；需要低体积版本时，为允许JPEG的不透明素材另做副本，按当前页核对体积限制。

## 交付与归档

读 [references/delivery.md](references/delivery.md)。交付填写信息、文件对应表、提示词、检查报告与上传ZIP。原稿和参考帧单独存档，不默认进入上传ZIP。

```bash
python scripts/sticker_pack.py pack --manifest /path/to/album.json --output /path/to/album-upload.zip
```

ZIP只收录清单引用的文件，附填写信息和检查报告。已有目标不覆盖；失败不留下假成功ZIP。

Windows归档可用以下脚本，默认只展示计划；当前任务已授权移动时再执行第二条：

```powershell
./scripts/archive_pack.ps1 -SourceRoot 'C:\work' -TargetRoot 'G:\stickers\series' -Items @('series-output','series-upload.zip')
./scripts/archive_pack.ps1 -SourceRoot 'C:\work' -TargetRoot 'G:\stickers\series' -Items @('series-output','series-upload.zip') -Execute -Move
```

只处理明确列出的项，SHA256逐项校验后才移除源副本。不覆盖目标、不跟随链接、不删除整个工作区。重复文件先核对内容再合并，不能只凭同名删除；跨盘写入遵循环境权限。

准备完材料不等于已发布。仅在用户要求且会话授权允许时操作平台，并以实际回执报告状态。
