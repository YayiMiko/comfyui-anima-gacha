import json
import os
import random
import time

import numpy as np
from PIL import Image

import folder_paths

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIST_DB_PATH = os.path.join(BASE_DIR, "artist_db.json")
TEMPLATES_PATH = os.path.join(BASE_DIR, "prompt_templates.json")
OUTPUT_DIR = os.path.join(folder_paths.get_output_directory(), "gacha")


def _sanitize_filename(s):
    if not s or s == "(no artist)":
        return "no_artist"
    return s.replace("@", "").replace(", ", "+").replace(" ", "_").replace("/", "_")


class GachaPromptBuilder:
    CATEGORY = "Gacha"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("positive", "negative", "artist_string", "metadata_json")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "artist_count": ("INT", {"default": 1, "min": 1, "max": 5}),
                "min_priority": ("INT", {"default": 1, "min": 0, "max": 10}),
            },
            "optional": {
                "subject": ("STRING", {"default": "", "multiline": False}),
                "extra_tags": ("STRING", {"default": "", "multiline": True}),
                "quality": (
                    "STRING",
                    {
                        "default": "newest, masterpiece, best quality, score_7, score_8, highres",
                        "multiline": False,
                    },
                ),
                "negative": (
                    "STRING",
                    {
                        "default": "worst quality, low quality, score_1, score_2, score_3, artist name",
                        "multiline": False,
                    },
                ),
            },
        }

    def build(
        self,
        seed,
        artist_count,
        min_priority,
        subject="",
        extra_tags="",
        quality="newest, masterpiece, best quality, score_7, score_8, highres",
        negative="worst quality, low quality, score_1, score_2, score_3, artist name",
    ):
        artists = self._load_artists(min_priority)
        subjects = self._load_subjects()

        if seed == 0:
            seed = random.randint(1, 0xFFFFFFFFFFFFFFFF)
        rng = random.Random(seed)

        count = min(artist_count, len(artists))
        picked = rng.sample(artists, count)
        names = [a["name"] for a in picked if a["name"]]
        artist_string = ", ".join(names) if names else "(no artist)"

        if not subject.strip():
            subject = rng.choice(subjects)

        parts = [quality.strip(), subject.strip()]
        if extra_tags.strip():
            parts.append(extra_tags.strip())
        parts.append(artist_string)
        positive = ", ".join(p for p in parts if p)

        metadata = {
            "seed": seed,
            "artist_count": count,
            "artist_string": artist_string,
            "artists": [a["name"] for a in picked],
            "subject": subject.strip(),
            "extra_tags": extra_tags.strip(),
            "positive": positive,
            "negative": negative.strip(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        return (
            positive,
            negative.strip(),
            artist_string,
            json.dumps(metadata, ensure_ascii=False, indent=2),
        )

    def _load_artists(self, min_priority):
        with open(ARTIST_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        pool = [a for a in data["artists"] if a.get("priority", 1) >= min_priority]
        if not pool:
            raise ValueError(
                f"没有 priority >= {min_priority} 的画师，请检查 artist_db.json"
            )
        return pool

    def _load_subjects(self):
        with open(TEMPLATES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("subjects", ["1girl, solo"])


class GachaSaveImage:
    CATEGORY = "Gacha"
    FUNCTION = "save"
    RETURN_TYPES = ()
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "artist_string": ("STRING", {"default": "", "multiline": False}),
                "metadata_json": ("STRING", {"default": "", "multiline": True}),
            }
        }

    def save(self, images, artist_string, metadata_json):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        try:
            meta = json.loads(metadata_json)
            seed = meta.get("seed", int(time.time()))
        except (json.JSONDecodeError, TypeError):
            seed = int(time.time())

        safe_name = _sanitize_filename(artist_string)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        base_name = f"{safe_name}__{seed}"

        results = []
        for i, image in enumerate(images):
            arr = (image.cpu().numpy() * 255).astype(np.uint8)
            pil_img = Image.fromarray(arr)

            png_name = f"{base_name}.png"
            png_path = os.path.join(OUTPUT_DIR, png_name)
            pil_img.save(png_path)

            json_name = f"{base_name}.json"
            json_path = os.path.join(OUTPUT_DIR, json_name)
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(metadata_json)

            results.append({"filename": f"gacha/{png_name}", "subfolder": "", "type": "output"})

        return {"ui": {"images": results}}
