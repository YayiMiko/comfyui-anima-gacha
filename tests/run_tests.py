"""Tests for artist_gacha nodes. Run from ComfyUI Python env:

    D:/AI/ComfyUI-aki-v1.7/python/python.exe tests/run_tests.py
"""
import json
import os
import sys
import tempfile

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMFYUI_ROOT = r"D:\AI\ComfyUI-aki-v1.7\ComfyUI"

# ComfyUI must be on sys.path for folder_paths import
sys.path.insert(0, COMFYUI_ROOT)
sys.path.insert(0, os.path.join(PROJECT_DIR, "artist_gacha"))

passed = 0
failed = 0


def check(cond, msg):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {msg}")
    else:
        failed += 1
        print(f"  FAIL  {msg}")


# ── 1. JSON schemas ──
print("=== 1. JSON 数据文件 ===")

with open(os.path.join(PROJECT_DIR, "artist_gacha", "artist_db.json"), "r", encoding="utf-8") as f:
    db = json.load(f)
check(len(db["artists"]) >= 100, f"{len(db['artists'])} artists (>=100)")

cats = set()
for a in db["artists"]:
    cats.add(a.get("category", ""))
    check("id" in a and "name" in a, f"id+name: {a.get('id','?')}")
    if a["name"]:
        check(a["name"].startswith("@"), f"@ prefix: {a['name']}")
check(len(cats) >= 4, f"{len(cats)} categories: {cats}")

with open(os.path.join(PROJECT_DIR, "artist_gacha", "prompt_templates.json"), "r", encoding="utf-8") as f:
    tmpl = json.load(f)
check(len(tmpl["subjects"]) >= 10, f"{len(tmpl['subjects'])} subjects (>=10)")

# ── 2. Workflow JSON ──
print("=== 2. 工作流 JSON ===")

with open(os.path.join(PROJECT_DIR, "gacha_workflow.json"), "r", encoding="utf-8") as f:
    wf = json.load(f)

ids = {n["id"] for n in wf["nodes"]}
types = {n["type"] for n in wf["nodes"]}
check("GachaPromptBuilder" in types, "GachaPromptBuilder present")
check("GachaSaveImage" in types, "GachaSaveImage present")
check(len(wf["nodes"]) == 11, f"11 nodes ({len(wf['nodes'])})")

for link in wf["links"]:
    s, _, t, _, _ = link
    check(s in ids, f"link src {s} valid")
    check(t in ids, f"link tgt {t} valid")

# ── 3. Node logic ──
print("=== 3. 节点逻辑 ===")

import folder_paths
folder_paths.get_output_directory = lambda: tempfile.gettempdir()

from nodes import GachaPromptBuilder, GachaSaveImage, _sanitize_filename

# 3a. _sanitize_filename
check(_sanitize_filename("@wlop, @ask") == "wlop+ask", "sanitize: compound")
check(_sanitize_filename("@akihiko yoshida") == "akihiko_yoshida", "sanitize: spaces")
check(_sanitize_filename("") == "no_artist", "sanitize: empty -> no_artist")
check(_sanitize_filename("(no artist)") == "no_artist", "sanitize: placeholder")

# 3b. basic build
b = GachaPromptBuilder()
pos, neg, art, meta_json = b.build(seed=42, artist_count=1, min_priority=1, subject="1girl, test")
check("1girl, test" in pos, "subject in prompt")
check("masterpiece" in pos, "quality in prompt")
check("@" in art, f"artist has @: {art}")
check(neg == "worst quality, low quality, score_1, score_2, score_3, artist name", "negative default")

meta = json.loads(meta_json)
check(meta["seed"] == 42, f"seed={meta['seed']}")
check(len(meta["artists"]) == 1, f"1 artist: {meta['artists']}")

# 3c. reproducibility
pos2, _, art2, _ = b.build(seed=42, artist_count=1, min_priority=1, subject="1girl, test")
check(pos == pos2 and art == art2, "same seed = same output")

# 3d. compound artists (count=3)
_, _, art3, meta3_json = b.build(seed=123, artist_count=3, min_priority=1, subject="1girl")
meta3 = json.loads(meta3_json)
check(meta3["artist_count"] == 3, "artist_count=3")
check(len(meta3["artists"]) == 3, f"3 artists: {meta3['artists']}")
check(art3.count("@") == 3, f"3 @ in '{art3}'")

# 3e. min_priority out of range
try:
    b.build(seed=1, artist_count=1, min_priority=999, subject="t")
    check(False, "min_priority=999 should raise")
except ValueError as e:
    check("没有 priority" in str(e), f"ValueError: {e}")

# 3f. subject from template pool (empty)
pos_empty, _, _, _ = b.build(seed=777, artist_count=1, min_priority=1, subject="")
check("1girl" in pos_empty, "empty subject -> from pool")

# 3g. extra_tags
pos_xt, _, _, _ = b.build(seed=1, artist_count=1, min_priority=1, subject="t", extra_tags="sketch, nsfw")
check("sketch, nsfw" in pos_xt, "extra_tags in prompt")

# 3h. SaveImage
saver = GachaSaveImage()
import torch
img = torch.zeros(1, 64, 64, 3)
result = saver.save(img, "@test_artist", meta_json)
check("ui" in result and len(result["ui"]["images"]) == 1, "save returns 1 image")
fname = result["ui"]["images"][0]["filename"]
check("gacha/test_artist" in fname, f"filename: {fname}")

# ── Summary ──
print(f"\n{'='*40}")
print(f"  {passed} passed, {failed} failed, {passed+failed} total")
if failed:
    print("  SOME TESTS FAILED!")
    sys.exit(1)
else:
    print("  ALL TESTS PASSED")
