# 微信 GIF 表情包工作室

给一张照片或一个角色，从实例库选风格，先确认静态造型，再由用户在网页端生成GIF，最后包装成微信表情专辑并跟进审核与上线状态。

![洛小咪系列横幅](examples/luoxiaomi2/assets/banner.png)

## 完整流程

| 阶段 | 助手交付 | 完成条件 |
| --- | --- | --- |
| 实例选风格 | 查阅相关实例，给出少量清楚的样式选择 | 用户确定画风与拟人程度 |
| 静态造型参考 | 单角色512×512 PNG及高清原稿 | 核对真实尺寸、身份与构图，用户认可 |
| GIF提示词 | 每条独立完整，写清参考图用途、动作、台词和循环 | 用户可逐条复制 |
| 用户网页生成 | 用户使用自己的网页入口逐张生成 | 收到实际GIF文件 |
| 成品检查 | 格式、尺寸、循环、时长、帧数、重复、透明与画面检查 | 问题处理或明确列出 |
| 微信包装 | 名称、介绍、版权、赞赏语、五张配图 | 核对实际尺寸、文字和透明度 |
| 打包与提交 | GIF上传副本、缩略图、清单、填写信息、检查报告、ZIP | 用户上传，记录待审核 |
| 审核与上线 | 按反馈定点修订、保留版本和回执 | 确认上线后记录日期与链接 |

默认分工是**助手设计和写提示词，用户在网页端生成GIF**。用户说“做GIF”时，沿用这一分工，交付逐条提示词；只有明确要求助手代为生成动图，才另行选择实际可用的入口。

## 实例库与尺寸参考

- [风格选择索引](references/style-library.md)：照片质感宠物拟人、高清插画改编、像素等方向。
- [本地实例展厅](references/style-library/README.md)：来自pixel-gif-sticker-pack固定版本的示例与参考，含223个GIF文件（含预览与候选），附来源和许可。
- [尺寸参考表](references/sizes.md)：静态参考、创作GIF、上传主图、缩略图和五张配图的用途与规格。
- [发布状态说明](references/publication.md)：材料就绪、待审核、需修改、通过、上线。

## 洛小咪完整案例

**2026-11-06：用户已上传微信，待审核。**当前不表示审核通过或已上线。

- [从选风格到提交的完整案例](examples/luoxiaomi2/README.md)
- [512×512单角色静态参考](examples/luoxiaomi2/reference.png)
- [八条完整GIF提示词](examples/luoxiaomi2/prompts.md)
- [8张GIF与五张配图清单](examples/luoxiaomi2/album.json)
- [五张配图预览](examples/luoxiaomi2/assets-preview.jpg)、[填写信息](examples/luoxiaomi2/publishing.md)

| 嗨起来 | 收到 | 抱抱 | 晚安 |
| --- | --- | --- | --- |
| ![嗨起来](examples/luoxiaomi2/stickers/01_嗨起来.gif) | ![收到](examples/luoxiaomi2/stickers/02_收到.gif) | ![抱抱](examples/luoxiaomi2/stickers/06_抱抱.gif) | ![晚安](examples/luoxiaomi2/stickers/08_晚安.gif) |

## 安装与调用

```text
使用 $wechat-gif-sticker-studio，根据我提供的猫咪照片，先从实例库给我几个风格选项。
我选定后生成一张合格尺寸的静态参考图；认可造型后再给8条完整GIF提示词。
GIF由我在网页端生成，做好后交给你检查和制作微信上架材料。
```

把本仓库链接发给Codex：

> 帮我安装这个Skill：https://github.com/qtyasupo/wechat-gif-sticker-studio

安装后下一轮可用；也可以将仓库复制为 `~/.codex/skills/wechat-gif-sticker-studio`。

```text
使用 $wechat-gif-sticker-studio，设计一套青白衣、高马尾的Q版古风剑客表情。
先给我8条完整提示词，我自己去网页端Image生成GIF。
每条保持同一角色，动作和台词不同，约2秒自然循环。
```

```text
使用 $wechat-gif-sticker-studio，我的GIF已经做好了。
请根据这些文件制作微信上架文案、750×400横幅、240×240透明封面、
50×50透明图标、750×560赞赏引导图和750×750赞赏致谢图。
版权填我指定的署名，保留原GIF，输出上传包。
```

```text
使用 $wechat-gif-sticker-studio，把这一套素材归档到我指定的目录。
先核对重名文件，完全相同的合并，逐文件校验后再移动源副本。
```

## 其他示例

| 收到 | 好耶 | 抱抱 | 摸鱼中 |
| --- | --- | --- | --- |
| ![收到](examples/xiaoju/stickers/01_收到.gif) | ![好耶](examples/xiaoju/stickers/02_好耶.gif) | ![抱抱](examples/xiaoju/stickers/03_抱抱.gif) | ![摸鱼中](examples/xiaoju/stickers/04_摸鱼中.gif) |

- [小橘：12条完整GIF提示词与修改提示词](examples/xiaoju-prompts.md)
- [青衫小剑客：8条完整GIF提示词](examples/swordsman-prompts.md)
- [小橘：8张GIF、五张配图及完整发布清单](examples/xiaoju/album.json)
- [赞赏引导图](examples/xiaoju/assets/support.png)、[赞赏致谢图](examples/xiaoju/assets/thanks.png)

示例GIF保留了实际制作中的白色背景；白底不等于透明。封面和图标是透明PNG。示例作者署名是AIYasupo，使用Skill给其他人创作时必须换成其实际署名。

## 可复用脚本

实例选风格、写提示词无需安装媒体依赖。媒体检查、导出与打包使用Python 3.11+、Pillow；尺寸适配另需FFmpeg。Windows归档脚本使用PowerShell 7。

```bash
python -m pip install -r requirements.txt
python scripts/sticker_pack.py audit --manifest examples/xiaoju/album.json --report build/xiaoju-report.json
python scripts/sticker_pack.py pack --manifest examples/xiaoju/album.json --output build/xiaoju-upload.zip
python scripts/sticker_pack.py prepare --source /path/to/original-gifs --output /path/to/new-upload-folder --size 240
python scripts/sticker_pack.py resize-asset --input generated-cover.png --output cover.png --width 240 --height 240
```

透明图片默认等比补透明边；不透明背景图可用 `--fit crop` 做等比中心裁切。脚本只执行机械导出，不生成插画或新动作，不覆盖已有目标。

```powershell
# 默认仅展示计划
./scripts/archive_pack.ps1 -SourceRoot 'C:\work' -TargetRoot 'G:\stickers\series' -Items @('series-output','series-upload.zip')
# 复制并逐文件核对，-Move才会在验证后清理源项
./scripts/archive_pack.ps1 -SourceRoot 'C:\work' -TargetRoot 'G:\stickers\series' -Items @('series-output','series-upload.zip') -Execute -Move
```

## 关于微信规格

五张配图的默认尺寸来自本案例的用户指定值。字数配置为名称8、介绍80、版权10、赞赏语5–15字，见[可修改配置](references/wechat-profile.json)。这些值不承诺永久适用于全部提交入口；实际上传以当前页面为准，文件体积上限确认后再配置。

脚本通过不能代替视觉检查或平台审核。材料准备完成也不等于已经发布。

## 校验与许可

```bash
python -m unittest discover -s tests -v
```

代码与文档采用[MIT许可](LICENSE)。小橘和洛小咪示例为本工作流的AI辅助作品，署名AIYasupo。第三方实例库保留其独立许可与具体素材来源，见references/style-library/LICENSE与SOURCE.json。工作流参考了[pixel-gif-sticker-pack](https://github.com/WoYun520/pixel-gif-sticker-pack)的角色一致性和交付检查思路；本仓库的脚本独立实现，支持用户自行在网页端生成GIF的路径。
