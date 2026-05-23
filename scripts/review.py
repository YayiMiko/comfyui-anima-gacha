"""Review generated gacha images and update artist_db.json priorities.

Usage: python scripts/review.py

Scans output/gacha/, groups by artist, opens images in viewer,
then prompts for rating. Updates artist_db.json in place.
"""
import json
import os
import re
import sys

OUTPUT_DIR = r"D:\AI\ComfyUI-aki-v1.7\ComfyUI\output\gacha"
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "artist_gacha", "artist_db.json",
)


def sanitize(name):
    """Mirrors _sanitize_filename in nodes.py."""
    if not name or name == "(no artist)":
        return "no_artist"
    return name.replace("@", "").replace(", ", "+").replace(" ", "_").replace("/", "_")


def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(db):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print("  -> artist_db.json 已更新")


def build_index(db):
    """Build {sanitized_name: artist_entry} lookup."""
    return {sanitize(a["name"]): a for a in db["artists"]}


def scan_images():
    """Scan output dir, group PNGs by artist."""
    groups = {}
    if not os.path.isdir(OUTPUT_DIR):
        print(f"输出目录不存在: {OUTPUT_DIR}")
        return groups

    for fname in os.listdir(OUTPUT_DIR):
        if not fname.endswith(".png"):
            continue
        # Format: {artist_id}__{seed}.png or {artist1}+{artist2}__{seed}.png
        # For single artists, artist_id is the sanitized name
        # For compound, it's artist1+artist2
        match = re.match(r"(.+?)__\d+.*\.png$", fname)
        if not match:
            continue
        key = match.group(1)
        groups.setdefault(key, []).append(os.path.join(OUTPUT_DIR, fname))
    return groups


def main():
    db = load_db()
    index = build_index(db)
    groups = scan_images()

    if not groups:
        print("output/gacha/ 中没有找到生成图片，请先跑阶段 1 生成。")
        return

    # Show stats
    matched = sum(1 for k in groups if k in index)
    unmatched = sum(1 for k in groups if k not in index)
    print(f"找到 {len(groups)} 个画师分组（{matched} 匹配数据库, {unmatched} 未匹配）")
    print()

    reviewed = 0
    total = len(groups)

    for key, paths in sorted(groups.items()):
        entry = index.get(key)
        if entry is None:
            continue  # skip unmatched (compound strings etc.)

        name = entry["name"]
        current_priority = entry.get("priority", 1)
        status = {0: "差", 1: "未评", 2: "好"}.get(current_priority, "?")

        # Open all images for this artist
        for p in paths:
            os.startfile(p)

        print(f"[{reviewed + 1}/{total}] {name}  (当前: priority={current_priority} [{status}], {len(paths)} 张)")
        while True:
            choice = input("  g=好 b=差 s=跳过 q=退出 [g/b/s/q]: ").strip().lower()
            if choice == "g":
                entry["priority"] = 2
                entry["reviewed"] = True
                break
            elif choice == "b":
                entry["priority"] = 0
                entry["reviewed"] = True
                break
            elif choice == "s":
                break
            elif choice == "q":
                save_db(db)
                print(f"已审阅 {reviewed} 个，退出。")
                return
        if choice in ("g", "b"):
            reviewed += 1
            save_db(db)

    save_db(db)
    print(f"\n完成！共审阅 {reviewed}/{total} 个画师。")


if __name__ == "__main__":
    main()
