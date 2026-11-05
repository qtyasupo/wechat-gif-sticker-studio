# 微信 GIF 表情包工作室

给一个角色、一张参考图或一个成品文件夹，做出一套能聊天、能整理、能准备微信上架的表情包。

这个 Codex Skill 来自「小橘」和「青衫小剑客」的实际制作流程：先写统一角色的原生 GIF 提示词，用户去网页端生成；收回成品后，检查动画、制作专辑文案和五张配图，最后导出上传包并校验归档。

![小橘系列横幅](examples/xiaoju/assets/banner.png)

## 能做什么

| 你手里有什么 | Skill交付什么 |
| --- | --- |
| 一个角色主题 | 统一角色设定、表情用途与逐条完整GIF提示词 |
| 准备用网页端Image生成 | 可单独复制的提示词，不擅自代为生图 |
| 已生成的一套GIF | 真实帧数、循环、时长、重复与尺寸检查 |
| 准备微信上架 | 名称、介绍、版权署名、赞赏语和五张配图 |
| 零散素材和解压副本 | 上传ZIP、填写说明、SHA256校验与归档计划 |

只要提示词就只写提示词；需要实际动图时，按所选入口的真实能力执行。当前工具不能输出GIF，不代表整个模型不支持GIF。静态图集、改扩展名和整图摇摆不能冒充所需肢体动画。

## 安装与调用

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

## 示例

| 收到 | 好耶 | 抱抱 | 摸鱼中 |
| --- | --- | --- | --- |
| ![收到](examples/xiaoju/stickers/01_收到.gif) | ![好耶](examples/xiaoju/stickers/02_好耶.gif) | ![抱抱](examples/xiaoju/stickers/03_抱抱.gif) | ![摸鱼中](examples/xiaoju/stickers/04_摸鱼中.gif) |

- [小橘：12条完整GIF提示词与修改提示词](examples/xiaoju-prompts.md)
- [青衫小剑客：8条完整GIF提示词](examples/swordsman-prompts.md)
- [小橘：8张GIF、五张配图及完整发布清单](examples/xiaoju/album.json)
- [赞赏引导图](examples/xiaoju/assets/support.png)、[赞赏致谢图](examples/xiaoju/assets/thanks.png)

示例GIF保留了实际制作中的白色背景；白底不等于透明。封面和图标是透明PNG。示例作者署名是AIYasupo，使用Skill给其他人创作时必须换成其实际署名。

## 可复用脚本

只写提示词无需安装依赖。媒体检查、导出与打包使用Python 3.11+、Pillow；尺寸适配另需FFmpeg。Windows归档脚本使用PowerShell 7。

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

代码与文档采用[MIT许可](LICENSE)。示例为本工作流的AI辅助作品，署名AIYasupo。工作流参考了[pixel-gif-sticker-pack](https://github.com/WoYun520/pixel-gif-sticker-pack)的角色一致性和交付检查思路；本仓库的脚本独立实现，支持用户自行在网页端生成GIF的路径。
