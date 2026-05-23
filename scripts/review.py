"""Review generated gacha images. Supports single + compound artist strings.

Usage: python scripts/review.py

Outputs:
  - updates artist_db.json for single artists
  - saves good_combos.json + good_combos.txt for compound strings
"""
import json
import os
import re
import sys
import time

OUTPUT_DIRS = [
    r"D:\AI\ComfyUI-aki-v1.7\ComfyUI\output\gacha",
    r"D:\AI\ComfyUI-aki-v1.7\ComfyUI\output\gacha2",
    r"D:\AI\ComfyUI-aki-v1.7\ComfyUI\output\gacha3",
]
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "artist_gacha", "artist_db.json")
COMBOS_PATH = os.path.join(PROJECT_DIR, "data", "good_combos.json")
COMBOS_TXT = os.path.join(PROJECT_DIR, "data", "good_combos.txt")


def sanitize(name):
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
    return {sanitize(a["name"]): a for a in db["artists"]}


def parse_compound_key(key, index):
    """Parse 'ask+anmi' back to '@ask, @anmi'."""
    parts = key.split("+")
    names = []
    for p in parts:
        entry = index.get(p)
        if entry:
            names.append(entry["name"])
        else:
            names.append(f"@{p}")
    return ", ".join(names)


def scan_images():
    """Scan all output dirs, group PNGs by key."""
    groups = {}
    for outdir in OUTPUT_DIRS:
        if not os.path.isdir(outdir):
            continue
        for fname in os.listdir(outdir):
            if not fname.endswith(".png"):
                continue
            match = re.match(r"(.+?)__\d+.*\.png$", fname)
            if not match:
                continue
            key = match.group(1)
            groups.setdefault(key, []).append(os.path.join(outdir, fname))
    return groups


def load_combos():
    if os.path.exists(COMBOS_PATH):
        with open(COMBOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"good": [], "bad": []}


def save_combos(combos):
    os.makedirs(os.path.dirname(COMBOS_PATH), exist_ok=True)
    with open(COMBOS_PATH, "w", encoding="utf-8") as f:
        json.dump(combos, f, ensure_ascii=False, indent=2)

    # Export copy-paste ready txt
    with open(COMBOS_TXT, "w", encoding="utf-8") as f:
        for s in combos["good"]:
            f.write(s + "\n")
    print(f"  -> {len(combos['good'])} 个画师串已导出到 good_combos.txt")


def is_compound(key):
    return "+" in key


def main():
    db = load_db()
    index = build_index(db)
    combos = load_combos()
    groups = scan_images()

    if not groups:
        print("output/gacha*/ 中没有找到生成图片。")
        return

    singles = {k: v for k, v in groups.items() if not is_compound(k)}
    compounds = {k: v for k, v in groups.items() if is_compound(k)}

    print(f"找到 {len(singles)} 个单画师分组, {len(compounds)} 个复合画师串分组")
    print()

    reviewed = 0
    total = len(groups)

    # --- Compound review ---
    combo_keys = sorted(compounds.keys())
    for key in combo_keys:
        paths = compounds[key]
        artist_string = parse_compound_key(key, index)

        # Skip already reviewed combos
        if artist_string in combos["good"] or artist_string in combos["bad"]:
            continue

        for p in paths:
            os.startfile(p)

        print(f"[{reviewed + 1}/{total}] {artist_string}  ({len(paths)} 张)")
        while True:
            choice = input("  g=好 b=差 s=跳过 q=退出 [g/b/s/q]: ").strip().lower()
            if choice == "g":
                if artist_string not in combos["good"]:
                    combos["good"].append(artist_string)
                if artist_string in combos["bad"]:
                    combos["bad"].remove(artist_string)
                reviewed += 1
                break
            elif choice == "b":
                if artist_string not in combos["bad"]:
                    combos["bad"].append(artist_string)
                if artist_string in combos["good"]:
                    combos["good"].remove(artist_string)
                reviewed += 1
                break
            elif choice == "s":
                break
            elif choice == "q":
                save_combos(combos)
                print(f"已审阅 {reviewed} 个，退出。")
                return
        if choice in ("g", "b"):
            save_combos(combos)

    # --- Single review ---
    single_keys = sorted(singles.keys())
    for key in single_keys:
        paths = singles[key]
        entry = index.get(key)
        if entry is None:
            continue
        if entry.get("reviewed"):
            continue

        for p in paths:
            os.startfile(p)

        name = entry["name"]
        current_priority = entry.get("priority", 1)
        status = {0: "差", 1: "未评", 2: "好"}.get(current_priority, "?")

        print(f"[{reviewed + 1}/{total}] {name}  (当前: priority={current_priority} [{status}], {len(paths)} 张)")
        while True:
            choice = input("  g=好 b=差 s=跳过 q=退出 [g/b/s/q]: ").strip().lower()
            if choice == "g":
                entry["priority"] = 2
                entry["reviewed"] = True
                reviewed += 1
                break
            elif choice == "b":
                entry["priority"] = 0
                entry["reviewed"] = True
                reviewed += 1
                break
            elif choice == "s":
                break
            elif choice == "q":
                save_db(db)
                save_combos(combos)
                print(f"已审阅 {reviewed} 个，退出。")
                return
        if choice in ("g", "b"):
            save_db(db)

    save_db(db)
    save_combos(combos)

    # Final summary
    print(f"\n完成！共审阅 {reviewed}/{total} 个。")
    if combos["good"]:
        print(f"\n=== 可粘贴画师串 ({len(combos['good'])} 个) ===")
        for s in combos["good"]:
            print(f"  {s}")
        print(f"\n已导出到: {COMBOS_TXT}")


if __name__ == "__main__":
    main()
