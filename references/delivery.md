# 发布包与归档

建议结构：原始GIF、upload/stickers、upload/thumbnails、upload/assets、upload/album.json、prompts、design-originals、references、reports和上传ZIP。目录名沿用用户约定也可；只处理当前系列，不移动无关项目。

album.json的路径全部相对于该清单目录。示例见examples/xiaoju/album.json。至少有album字段、stickers列表和assets映射；每个sticker有file与caption，可选thumbnail。assets键为banner、cover、icon、support、thanks。

脚本拒绝绝对路径、..、符号链接和越界引用。不开赞赏时可用删去对应asset规则和support_prompt字段限制的自定义profile；不要写不存在的图片骗过校验。

上传ZIP只含清单引用文件、填写信息与检查报告，不递归打包整个项目，不默认包含原稿、参考帧、机器路径或临时凭据。

archive_pack.ps1默认展示计划，-Execute复制，-Execute -Move在全量SHA256核对后移除源项。拒绝重名目标、不自动覆盖或合并、不跟随链接。源项必须在指定工作根目录下，目标不能位于源项内部；不允许用整个根目录作为源项。复制内容与全部文件集合检查通过后才清理源项，记录哈希。

若已有发布包和解压副本重复，先看是否同一内容，逐文件SHA256确认。完全相同且用户已授权归类才合并；冲突内容保留不同版本。不要只凭同名删除，不把归档完成当作平台发布成功。
