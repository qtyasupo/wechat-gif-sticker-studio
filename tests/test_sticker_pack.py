import importlib.util
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sticker_pack", ROOT / "scripts" / "sticker_pack.py")
PACK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACK)


class StickerPackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.case = self.root / "case"
        shutil.copytree(ROOT / "examples" / "xiaoju", self.case)
        self.manifest = self.case / "album.json"

    def change_manifest(self, change):
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        change(data)
        self.manifest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_real_case_has_eight_valid_animations_and_five_assets(self):
        _, report, entries = PACK.audit(self.manifest, PACK.DEFAULT_PROFILE)
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["sticker_count"], 8)
        self.assertEqual(len(entries), 21)
        gifs = [row for row in report["files"] if row["role"].startswith("sticker")]
        self.assertTrue(all(row["frames"] == 9 and row["duration_ms"] == 1980 for row in gifs))

    def test_static_gif_does_not_pass_as_animation(self):
        source = self.case / "stickers" / "01_收到.gif"
        with Image.open(source) as im:
            frame = im.convert("RGB")
        frame.save(source, format="GIF", loop=0, duration=200)
        _, report, _ = PACK.audit(self.manifest, PACK.DEFAULT_PROFILE)
        self.assertFalse(report["valid"])
        self.assertTrue(any("changing GIF" in error for error in report["errors"]))

    def test_opaque_cover_is_rejected(self):
        cover = self.case / "assets" / "cover.png"
        with Image.open(cover) as im:
            opaque = Image.new("RGB", im.size, "white")
            opaque.paste(im, mask=im.getchannel("A"))
        opaque.save(cover)
        _, report, _ = PACK.audit(self.manifest, PACK.DEFAULT_PROFILE)
        self.assertTrue(any("cover: require transparent" in error for error in report["errors"]))

    def test_duplicate_caption_and_wrong_field_length_are_rejected(self):
        def change(data):
            data["stickers"][1]["caption"] = data["stickers"][0]["caption"]
            data["album"]["name"] = "很长的专辑名字" * 4
        self.change_manifest(change)
        _, report, _ = PACK.audit(self.manifest, PACK.DEFAULT_PROFILE)
        self.assertTrue(any("duplicate caption" in error for error in report["errors"]))
        self.assertTrue(any("album.name" in error for error in report["errors"]))

    def test_path_escape_and_absolute_paths_are_rejected(self):
        for relative in ("../private.txt", "/tmp/private.txt", "C:/private.txt", "assets/../../private.txt"):
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                PACK.safe_media(self.case, relative)

    def test_pack_contains_only_manifest_files_and_never_overwrites(self):
        (self.case / "do-not-publish.txt").write_text("private project note", encoding="utf-8")
        output = self.root / "upload.zip"
        PACK.pack(self.manifest, PACK.DEFAULT_PROFILE, output)
        original = PACK.sha256(output)
        with zipfile.ZipFile(output) as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(len(z.namelist()), 23)
            self.assertNotIn("do-not-publish.txt", z.namelist())
            self.assertIn("填写信息.md", z.namelist())
        with self.assertRaises(FileExistsError):
            PACK.pack(self.manifest, PACK.DEFAULT_PROFILE, output)
        self.assertEqual(PACK.sha256(output), original)

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg not available")
    def test_mechanical_export_preserves_original_and_animation_timing(self):
        source = self.root / "originals"
        source.mkdir()
        gif = source / "one.gif"
        shutil.copyfile(self.case / "stickers" / "01_收到.gif", gif)
        before = PACK.media_info(gif)
        output = self.root / "prepared"
        PACK.prepare(source, output, 128)
        after = PACK.media_info(output / "stickers" / "one.gif")
        self.assertEqual(PACK.sha256(gif), before["sha256"])
        self.assertEqual(after["size"], [128, 128])
        self.assertEqual(after["duration_ms"], before["duration_ms"])
        self.assertEqual(after["frames"], before["frames"])
        self.assertEqual(after["loop"], 0)
        self.assertGreater(after["distinct_frames"], 1)
        self.assertEqual(PACK.media_info(output / "thumbnails" / "one.png")["size"], [120, 120])

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg not available")
    def test_cover_resize_preserves_true_transparency(self):
        output = self.root / "cover.png"
        PACK.resize_asset(self.case / "assets" / "cover.png", output, 80, 80, "contain")
        info = PACK.media_info(output)
        self.assertEqual(info["size"], [80, 80])
        self.assertEqual(info["alpha_range"], [0, 255])


if __name__ == "__main__":
    unittest.main()
