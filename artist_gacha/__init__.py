from .nodes import GachaPromptBuilder, GachaSaveImage

NODE_CLASS_MAPPINGS = {
    "GachaPromptBuilder": GachaPromptBuilder,
    "GachaSaveImage": GachaSaveImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GachaPromptBuilder": "Gacha Prompt Builder",
    "GachaSaveImage": "Gacha Save Image",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
