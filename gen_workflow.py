"""Generate gacha_workflow.json for Anima 1.0 artist gacha."""
import json

wf = {
    "last_node_id": 11,
    "last_link_id": 15,
    "nodes": [
        # --- Node 1: GachaPromptBuilder ---
        {
            "id": 1, "type": "GachaPromptBuilder",
            "pos": [-50, 200], "size": [350, 200], "flags": {}, "order": 0, "mode": 0,
            "inputs": [
                {"name": "seed", "type": "INT", "widget": {"name": "seed"}, "link": None},
                {"name": "artist_count", "type": "INT", "widget": {"name": "artist_count"}, "link": None},
                {"name": "min_priority", "type": "INT", "widget": {"name": "min_priority"}, "link": None},
                {"name": "subject", "type": "STRING", "widget": {"name": "subject"}, "link": None},
                {"name": "extra_tags", "type": "STRING", "widget": {"name": "extra_tags"}, "link": None},
                {"name": "quality", "type": "STRING", "widget": {"name": "quality"}, "link": None},
                {"name": "negative", "type": "STRING", "widget": {"name": "negative"}, "link": None},
            ],
            "outputs": [
                {"name": "positive", "type": "STRING", "links": [1], "slot_index": 0},
                {"name": "negative", "type": "STRING", "links": [2], "slot_index": 1},
                {"name": "artist_string", "type": "STRING", "links": [14], "slot_index": 2},
                {"name": "metadata_json", "type": "STRING", "links": [15], "slot_index": 3},
            ],
            "properties": {"Node name for S&R": "GachaPromptBuilder"},
            "widgets_values": [0, 1, 1, "",
                "masterpiece",
                ""],
        },
        # --- Node 2: UNETLoader ---
        {
            "id": 2, "type": "UNETLoader",
            "pos": [-50, -80], "size": [367, 122], "flags": {}, "order": 1, "mode": 0,
            "showAdvanced": False,
            "inputs": [
                {"name": "unet_name", "type": "COMBO", "widget": {"name": "unet_name"}, "link": None},
                {"name": "weight_dtype", "type": "COMBO", "widget": {"name": "weight_dtype"}, "link": None},
            ],
            "outputs": [
                {"name": "MODEL", "type": "MODEL", "links": [3], "slot_index": 0},
            ],
            "properties": {"cnr_id": "comfy-core", "ver": "0.11.0", "Node name for S&R": "UNETLoader"},
            "widgets_values": ["anima_baseV10.safetensors", "default"],
        },
        # --- Node 3: CLIPLoader ---
        {
            "id": 3, "type": "CLIPLoader",
            "pos": [-50, 60], "size": [366, 147], "flags": {}, "order": 2, "mode": 0,
            "showAdvanced": False,
            "inputs": [
                {"name": "clip_name", "type": "COMBO", "widget": {"name": "clip_name"}, "link": None},
                {"name": "type", "type": "COMBO", "widget": {"name": "type"}, "link": None},
                {"name": "device", "type": "COMBO", "widget": {"name": "device"}, "link": None},
            ],
            "outputs": [
                {"name": "CLIP", "type": "CLIP", "links": [4, 5], "slot_index": 0},
            ],
            "properties": {"cnr_id": "comfy-core", "ver": "0.11.0", "Node name for S&R": "CLIPLoader"},
            "widgets_values": ["qwen_3_06b_base.safetensors", "stable_diffusion", "default"],
        },
        # --- Node 4: VAELoader ---
        {
            "id": 4, "type": "VAELoader",
            "pos": [-50, 230], "size": [370, 101], "flags": {}, "order": 3, "mode": 0,
            "inputs": [
                {"name": "vae_name", "type": "COMBO", "widget": {"name": "vae_name"}, "link": None},
            ],
            "outputs": [
                {"name": "VAE", "type": "VAE", "links": [6], "slot_index": 0},
            ],
            "properties": {"cnr_id": "comfy-core", "ver": "0.3.40", "Node name for S&R": "VAELoader"},
            "widgets_values": ["qwen_image_vae.safetensors"],
        },
        # --- Node 5: LoraLoader (turbo, default enabled) ---
        {
            "id": 5, "type": "LoraLoader",
            "pos": [350, -80], "size": [270, 170], "flags": {}, "order": 4, "mode": 0,
            "inputs": [
                {"name": "model", "type": "MODEL", "link": 3},
                {"name": "clip", "type": "CLIP", "link": 4},
                {"name": "lora_name", "type": "COMBO", "widget": {"name": "lora_name"}, "link": None},
                {"name": "strength_model", "type": "FLOAT", "widget": {"name": "strength_model"}, "link": None},
                {"name": "strength_clip", "type": "FLOAT", "widget": {"name": "strength_clip"}, "link": None},
            ],
            "outputs": [
                {"name": "MODEL", "type": "MODEL", "links": [7], "slot_index": 0},
                {"name": "CLIP", "type": "CLIP", "links": [8], "slot_index": 1},
            ],
            "properties": {"cnr_id": "comfy-core", "ver": "0.21.1", "Node name for S&R": "LoraLoader"},
            "widgets_values": ["anima-turbo-lora-v0.1.safetensors", 1.0, 1.0],
        },
        # --- Node 6: EmptyLatentImage ---
        {
            "id": 6, "type": "EmptyLatentImage",
            "pos": [350, 500], "size": [270, 143], "flags": {}, "order": 5, "mode": 0,
            "inputs": [
                {"name": "width", "type": "INT", "widget": {"name": "width"}, "link": None},
                {"name": "height", "type": "INT", "widget": {"name": "height"}, "link": None},
                {"name": "batch_size", "type": "INT", "widget": {"name": "batch_size"}, "link": None},
            ],
            "outputs": [
                {"name": "LATENT", "type": "LATENT", "links": [9], "slot_index": 0},
            ],
            "properties": {"cnr_id": "comfy-core", "ver": "0.3.40", "Node name for S&R": "EmptyLatentImage"},
            "widgets_values": [832, 1216, 1],
        },
        # --- Node 7: CLIPTextEncode (positive) ---
        {
            "id": 7, "type": "CLIPTextEncode",
            "pos": [700, 150], "size": [400, 200], "flags": {}, "order": 6, "mode": 0,
            "inputs": [
                {"name": "clip", "type": "CLIP", "link": 8},
                {"name": "text", "type": "STRING", "widget": {"name": "text"}, "link": 1},
            ],
            "outputs": [
                {"name": "CONDITIONING", "type": "CONDITIONING", "links": [10], "slot_index": 0},
            ],
            "title": "CLIP Text Encode (Positive)",
            "properties": {"cnr_id": "comfy-core", "ver": "0.3.65", "Node name for S&R": "CLIPTextEncode"},
            "widgets_values": [""],
        },
        # --- Node 8: CLIPTextEncode (negative) ---
        {
            "id": 8, "type": "CLIPTextEncode",
            "pos": [700, 380], "size": [400, 120], "flags": {}, "order": 7, "mode": 0,
            "inputs": [
                {"name": "clip", "type": "CLIP", "link": 5},
                {"name": "text", "type": "STRING", "widget": {"name": "text"}, "link": 2},
            ],
            "outputs": [
                {"name": "CONDITIONING", "type": "CONDITIONING", "links": [11], "slot_index": 0},
            ],
            "title": "CLIP Text Encode (Negative)",
            "properties": {"cnr_id": "comfy-core", "ver": "0.3.65", "Node name for S&R": "CLIPTextEncode"},
            "widgets_values": [""],
        },
        # --- Node 9: KSampler ---
        {
            "id": 9, "type": "KSampler",
            "pos": [1150, 150], "size": [297, 564], "flags": {}, "order": 8, "mode": 0,
            "inputs": [
                {"name": "model", "type": "MODEL", "link": 7},
                {"name": "positive", "type": "CONDITIONING", "link": 10},
                {"name": "negative", "type": "CONDITIONING", "link": 11},
                {"name": "latent_image", "type": "LATENT", "link": 9},
                {"name": "seed", "type": "INT", "widget": {"name": "seed"}, "link": None},
                {"name": "steps", "type": "INT", "widget": {"name": "steps"}, "link": None},
                {"name": "cfg", "type": "FLOAT", "widget": {"name": "cfg"}, "link": None},
                {"name": "sampler_name", "type": "COMBO", "widget": {"name": "sampler_name"}, "link": None},
                {"name": "scheduler", "type": "COMBO", "widget": {"name": "scheduler"}, "link": None},
                {"name": "denoise", "type": "FLOAT", "widget": {"name": "denoise"}, "link": None},
            ],
            "outputs": [
                {"name": "LATENT", "type": "LATENT", "links": [12], "slot_index": 0},
            ],
            "properties": {"cnr_id": "comfy-core", "ver": "0.3.40", "Node name for S&R": "KSampler"},
            "widgets_values": [0, "randomize", 12, 1.0, "er_sde", "simple", 1.0],
        },
        # --- Node 10: VAEDecode ---
        {
            "id": 10, "type": "VAEDecode",
            "pos": [1500, 200], "size": [225, 71], "flags": {}, "order": 9, "mode": 0,
            "inputs": [
                {"name": "samples", "type": "LATENT", "link": 12},
                {"name": "vae", "type": "VAE", "link": 6},
            ],
            "outputs": [
                {"name": "IMAGE", "type": "IMAGE", "links": [13], "slot_index": 0},
            ],
            "properties": {"cnr_id": "comfy-core", "ver": "0.3.40", "Node name for S&R": "VAEDecode"},
            "widgets_values": [],
        },
        # --- Node 11: GachaSaveImage ---
        {
            "id": 11, "type": "GachaSaveImage",
            "pos": [1500, 310], "size": [350, 150], "flags": {}, "order": 10, "mode": 0,
            "inputs": [
                {"name": "images", "type": "IMAGE", "link": 13},
                {"name": "artist_string", "type": "STRING", "widget": {"name": "artist_string"}, "link": 14},
                {"name": "metadata_json", "type": "STRING", "widget": {"name": "metadata_json"}, "link": 15},
            ],
            "outputs": [],
            "properties": {"Node name for S&R": "GachaSaveImage"},
            "widgets_values": ["", ""],
        },
    ],
    "links": [
        [1, 0, 7, 1, "STRING"],     # GachaPromptBuilder positive -> CLIPTextEncode(pos) text
        [1, 1, 8, 1, "STRING"],     # GachaPromptBuilder negative -> CLIPTextEncode(neg) text
        [2, 0, 5, 0, "MODEL"],      # UNETLoader -> LoraLoader model
        [3, 0, 5, 1, "CLIP"],       # CLIPLoader -> LoraLoader clip
        [3, 0, 8, 0, "CLIP"],       # CLIPLoader -> CLIPTextEncode(neg) clip
        [4, 0, 10, 1, "VAE"],       # VAELoader -> VAEDecode vae
        [5, 0, 9, 0, "MODEL"],      # LoraLoader MODEL -> KSampler model
        [5, 1, 7, 0, "CLIP"],       # LoraLoader CLIP -> CLIPTextEncode(pos) clip
        [6, 0, 9, 3, "LATENT"],     # EmptyLatentImage -> KSampler latent_image
        [7, 0, 9, 1, "CONDITIONING"],  # CLIPTextEncode(pos) -> KSampler positive
        [8, 0, 9, 2, "CONDITIONING"],  # CLIPTextEncode(neg) -> KSampler negative
        [9, 0, 10, 0, "LATENT"],    # KSampler -> VAEDecode samples
        [10, 0, 11, 0, "IMAGE"],    # VAEDecode -> GachaSaveImage images
        [1, 2, 11, 1, "STRING"],    # GachaPromptBuilder artist_string -> GachaSaveImage
        [1, 3, 11, 2, "STRING"],    # GachaPromptBuilder metadata_json -> GachaSaveImage
    ],
    "groups": [],
    "config": {},
    "extra": {
        "ds": {"scale": 1.0, "offset": [0, 0]},
        "workflowRendererVersion": "LG",
    },
    "version": 0.4,
}

print(json.dumps(wf, indent=2, ensure_ascii=False))
