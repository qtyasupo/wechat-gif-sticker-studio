# 风格实例库

先按用户主体选择少量实例并实际看图，再询问样式。一次给出约3个方向；已有选择就沿用。画风、是否穿衣拿道具、动作与台词分开确定。

| 方向 | 本地例子 | 借鉴方式 |
| --- | --- | --- |
| 照片质感宠物拟人 | [洛小咪](../examples/luoxiaomi2/README.md)、[柯基](style-library/examples/pet-corgi) | 真实脸和毛发，服装、道具和聊天动作；洛小咪为本流程高清实例 |
| 像素聊天角色 | [像素小秘书](style-library/examples/01-replies)、[鲸鱼娘](style-library/examples/whale-maid) | 像素轮廓、短台词、用途分类；宠物可据此提出像素改编 |
| 高清插画／Q版 | [混合动作示例](style-library/examples/mixed-actions) | 借鉴插画材质和表情；宠物Q版属于拟议改编，不冒充已有猫咪实例 |
| 照片人物风格 | [人物高清](style-library/examples/public-figures-hd) | 仅人物题材时查阅，保留来源和署名 |
| 动作稳定性比较 | [修补候选](style-library/examples/anime-stability) | 上游仍标记待确认，用于比较问题，不推荐为已验收模板 |

完整参考库含223个GIF文件（包括集合预览、修补候选）。上游展厅统计218张既有独立表情和2张修补候选，集合预览不算新增独立作品。见 [本地展厅快照](style-library/README.md)。另有本仓库小橘、洛小咪各8张。

## 看图后的询问示例

“这只猫的银灰花纹、绿眼睛和圆脸会保留。你想要A照片质感拟人、B高清Q版插画，还是C像素游戏风？选择拟人时，偏原样猫咪，还是穿衣服、拿道具？”

用户选定后先交付一个 [合格尺寸静态造型参考](sizes.md)，认可后再写该系列GIF提示词。参考库用于画风、聊天用途、构图和节奏；生成分工见主技能。

## 来源与使用范围

上游：[WoYun520/pixel-gif-sticker-pack](https://github.com/WoYun520/pixel-gif-sticker-pack)，固定版本 `94561fef11744e8145311534274affb8d7f55716`。本地保存示例和参考文档，不安装第二个Skill；上游方法不替代本技能的网页生成流程。

- [许可](style-library/LICENSE)、[来源及逐文件SHA256](style-library/SOURCE.json)。
- 人物照片、角色等保留上游README和sources.json中的具体来源与条款；代码文档许可不自动赋予第三方角色或照片的无条件商用权限。
- 实例不直接混入用户新作品或上传包，不继承别人的署名。
- 上游过程提示词、检查记录为历史参考，其候选状态与视觉限制继续保留。
