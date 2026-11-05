#!/usr/bin/env python3
"""Inspect existing media, perform mechanical FFmpeg exports, and build upload ZIPs."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from PIL import Image

DEFAULT_PROFILE = Path(__file__).resolve().parents[1] / "references" / "wechat-profile.json"


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def safe_media(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("Media paths must be nonempty relative strings")
    posix = PurePosixPath(relative.replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts or ":" in relative:
        raise ValueError(f"Unsafe media path: {relative}")
    path = root.joinpath(*posix.parts)
    current = root
    for part in posix.parts:
        current = current / part
        if current.is_symlink() or getattr(current, "is_junction", lambda: False)():
            raise ValueError(f"Linked media is not accepted: {relative}")
    if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"Missing or escaped media: {relative}")
    return path


def media_info(path: Path) -> dict:
    with Image.open(path) as im:
        result = {"size": list(im.size), "format": im.format,
                  "frames": getattr(im, "n_frames", 1), "loop": im.info.get("loop"),
                  "bytes": path.stat().st_size, "sha256": sha256(path)}
        durations, decoded = [], set()
        alpha_min, alpha_max = 255, 0
        for index in range(result["frames"]):
            im.seek(index)
            rgba = im.convert("RGBA")
            decoded.add(hashlib.sha256(rgba.tobytes()).hexdigest())
            lo, hi = rgba.getchannel("A").getextrema()
            alpha_min, alpha_max = min(alpha_min, lo), max(alpha_max, hi)
            durations.append(im.info.get("duration", 0))
        result.update(duration_ms=sum(durations), frame_durations_ms=durations,
                      distinct_frames=len(decoded), alpha_range=[alpha_min, alpha_max])
        return result


def audit(manifest_path: Path, profile_path: Path) -> tuple[dict, dict, list[tuple[str, Path]]]:
    data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    profile = json.loads(profile_path.read_text(encoding="utf-8-sig"))
    root, errors, warnings, files, entries = manifest_path.parent.resolve(), [], [], [], []
    album = data.get("album", {})
    for key, (minimum, maximum) in profile["field_limits"].items():
        value = album.get(key, "")
        if not isinstance(value, str) or not minimum <= len(value) <= maximum:
            errors.append(f"album.{key}: expected {minimum}..{maximum} characters")
    stickers = data.get("stickers", [])
    if not isinstance(stickers, list) or not stickers:
        raise ValueError("stickers must be a nonempty list")
    captions, hashes = set(), set()

    def inspect(relative: str, label: str) -> dict | None:
        try:
            path = safe_media(root, relative)
            info = media_info(path)
            info.update(file=relative, role=label)
            files.append(info)
            entries.append((Path(relative).as_posix(), path))
            return info
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"{label}: {exc}")
            return None

    for index, sticker in enumerate(stickers, 1):
        caption = sticker.get("caption", "")
        if not isinstance(caption, str) or not caption.strip() or caption in captions:
            errors.append(f"sticker {index}: empty or duplicate caption")
        captions.add(caption)
        info = inspect(sticker.get("file"), f"sticker {index}")
        if info:
            if info["format"] != "GIF" or info["distinct_frames"] < 2:
                errors.append(f"sticker {index}: expected a visibly changing GIF")
            if info["size"] != profile["sticker_size"]:
                errors.append(f"sticker {index}: size {info['size']} != {profile['sticker_size']}")
            if info["loop"] != 0 or any(d <= 0 for d in info["frame_durations_ms"]):
                errors.append(f"sticker {index}: require infinite loop and positive frame delays")
            if info["sha256"] in hashes:
                errors.append(f"sticker {index}: duplicate GIF file")
            hashes.add(info["sha256"])
            if profile.get("sticker_max_bytes") and info["bytes"] > profile["sticker_max_bytes"]:
                errors.append(f"sticker {index}: exceeds configured byte limit")
        if sticker.get("thumbnail"):
            thumb = inspect(sticker["thumbnail"], f"thumbnail {index}")
            if thumb and (thumb["size"] != profile["thumbnail_size"] or thumb["format"] != "PNG"):
                errors.append(f"thumbnail {index}: wrong size or format")
    for name, rule in profile["assets"].items():
        info = inspect(data.get("assets", {}).get(name), name)
        if not info:
            continue
        if info["size"] != rule["size"] or info["format"] not in rule["formats"]:
            errors.append(f"{name}: wrong size or format")
        if rule.get("transparent") and info["alpha_range"] != [0, 255]:
            errors.append(f"{name}: require transparent background and opaque visible content")
        if rule.get("max_bytes") and info["bytes"] > rule["max_bytes"]:
            errors.append(f"{name}: exceeds configured byte limit")
    archive_names = [name.replace("\\", "/") for name, _ in entries]
    if len(archive_names) != len(set(archive_names)):
        errors.append("The same file is referenced multiple times")
    if any(name.casefold() in {"填写信息.md", "检查报告.json"} for name in archive_names):
        errors.append("Media file name conflicts with generated ZIP documentation")
    warnings.append("Visual review and current platform submission validation remain necessary.")
    report = {"valid": not errors, "errors": errors, "warnings": warnings,
              "sticker_count": len(stickers), "files": files}
    return data, report, entries


def ffmpeg(arguments: list[str]) -> None:
    executable = shutil.which("ffmpeg")
    if not executable:
        raise ValueError("FFmpeg is required for this export; audit and pack do not need it")
    result = subprocess.run([executable, "-hide_banner", "-loglevel", "error", "-n", *arguments],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise ValueError(result.stderr.strip() or "FFmpeg export failed")


def prepare(source: Path, output: Path, size: int) -> None:
    source = source.resolve(strict=True)
    if not source.is_dir() or size <= 0:
        raise ValueError("Require a GIF directory and positive target size")
    if output.resolve().is_relative_to(source):
        raise ValueError("Output must be outside the source directory")
    inputs = sorted(p for p in source.iterdir() if p.suffix.lower() == ".gif")
    if not inputs:
        raise ValueError("No top-level GIF inputs found")
    before = {}
    for path in inputs:
        if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            raise ValueError("Linked input is not accepted")
        info = media_info(path)
        if info["format"] != "GIF" or info["distinct_frames"] < 2:
            raise ValueError(f"Not an animated GIF: {path.name}")
        before[path] = info
    output.mkdir(parents=True, exist_ok=False)
    try:
        (output / "stickers").mkdir()
        (output / "thumbnails").mkdir()
        for path, info in before.items():
            target = output / "stickers" / path.name
            color = "0x00000000" if info["alpha_range"][0] == 0 else "white"
            filters = (f"[0:v]scale={size}:{size}:force_original_aspect_ratio=decrease:flags=lanczos,"
                       f"pad={size}:{size}:(ow-iw)/2:(oh-ih)/2:color={color},split[a][b];"
                       "[a]palettegen=reserve_transparent=1:stats_mode=diff[p];"
                       "[b][p]paletteuse=dither=sierra2_4a")
            ffmpeg(["-i", str(path), "-filter_complex", filters, "-loop", "0",
                    "-fps_mode", "passthrough", str(target)])
            after = media_info(target)
            if (after["size"] != [size, size] or after["distinct_frames"] < 2 or after["loop"] != 0
                    or after["duration_ms"] != info["duration_ms"]):
                raise ValueError(f"Animation invariant changed: {path.name}")
            ffmpeg(["-i", str(target), "-vf", "scale=120:120:flags=lanczos", "-frames:v", "1",
                    "-update", "1", str(output / "thumbnails" / (path.stem + ".png"))])
            if sha256(path) != info["sha256"]:
                raise ValueError(f"Source changed during export: {path.name}")
        write_json(output / "export-report.json", {"count": len(before), "size": [size, size],
                    "source_files_preserved": True, "thumbnail_size": [120, 120]})
    except Exception:
        (output / "INCOMPLETE.txt").write_text("Export failed. Do not upload this folder.\n", encoding="utf-8")
        raise


def resize_asset(source: Path, output: Path, width: int, height: int, fit: str) -> None:
    if width <= 0 or height <= 0 or output.suffix.lower() != ".png":
        raise ValueError("Use positive dimensions and a PNG output")
    if output.exists():
        raise FileExistsError(output)
    media_info(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    if fit == "crop":
        vf = f"scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos,crop={width}:{height}"
    else:
        vf = (f"scale={width}:{height}:force_original_aspect_ratio=decrease:flags=lanczos,format=rgba,"
              f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x00000000")
    ffmpeg(["-i", str(source), "-vf", vf, "-frames:v", "1", "-update", "1", str(output)])
    if media_info(output)["size"] != [width, height]:
        raise ValueError("Unexpected exported asset dimensions")


def pack(manifest: Path, profile: Path, output: Path) -> None:
    data, report, entries = audit(manifest, profile)
    if not report["valid"]:
        raise ValueError("Pack validation failed: " + "; ".join(report["errors"]))
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    album = data["album"]
    copy = "# 填写信息\n\n" + "\n\n".join(
        f"{key}（{len(value)}字）\n\n{value}" for key, value in album.items())
    # Temporary file is in the same directory, so exclusive publication stays on the same filesystem.
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".partial", delete=False) as stream:
        temporary = Path(stream.name)
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for name, path in entries:
                z.write(path, name.replace("\\", "/"))
            z.writestr("填写信息.md", copy)
            z.writestr("检查报告.json", json.dumps(report, ensure_ascii=False, indent=2))
        with zipfile.ZipFile(temporary) as z:
            if z.testzip() is not None:
                raise ValueError("ZIP integrity verification failed")
        # Exclusive copy avoids a race that could overwrite a user-created destination.
        try:
            with temporary.open("rb") as src, output.open("xb") as dst:
                shutil.copyfileobj(src, dst)
        except FileExistsError:
            raise
        except Exception:
            output.unlink(missing_ok=True)
            raise
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("audit", "pack"):
        child = sub.add_parser(name)
        child.add_argument("--manifest", type=Path, required=True)
        child.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
        child.add_argument("--report" if name == "audit" else "--output", type=Path, required=True)
    child = sub.add_parser("prepare")
    child.add_argument("--source", type=Path, required=True)
    child.add_argument("--output", type=Path, required=True)
    child.add_argument("--size", type=int, default=240)
    child = sub.add_parser("resize-asset")
    child.add_argument("--input", type=Path, required=True)
    child.add_argument("--output", type=Path, required=True)
    child.add_argument("--width", type=int, required=True)
    child.add_argument("--height", type=int, required=True)
    child.add_argument("--fit", choices=["contain", "crop"], default="contain")
    args = parser.parse_args()
    try:
        if args.command == "audit":
            _, report, _ = audit(args.manifest, args.profile)
            write_json(args.report, report)
            print(json.dumps({"valid": report["valid"], "errors": report["errors"]}, ensure_ascii=False))
            return 0 if report["valid"] else 1
        if args.command == "pack":
            pack(args.manifest, args.profile, args.output)
        elif args.command == "prepare":
            prepare(args.source, args.output, args.size)
        else:
            resize_asset(args.input, args.output, args.width, args.height, args.fit)
        print("Completed: " + str(args.output))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
