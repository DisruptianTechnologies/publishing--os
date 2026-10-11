"""
Cover Geometry & Blueprint Calculator for Amazon KDP Print.
Calculates exact spine widths, full-bleed canvas dimensions, safe zones,
and synthesizes commercial image prompts for generative cover art.
"""

from __future__ import annotations
from typing import Literal

# KDP Paper Thickness Multipliers (inches per page)
PAPER_FACTORS = {
    "white": 0.002252,   # Standard Black & White on White paper (50-61 lb)
    "cream": 0.002500,   # Black & White on Cream paper (50-61 lb)
    "color": 0.002347,   # Standard / Premium Color interior
}

# Standard KDP Trim Dimensions (Width x Height in inches)
TRIM_DIMENSIONS = {
    "5x8": (5.0, 8.0),
    "5.25x8": (5.25, 8.0),
    "5.5x8.5": (5.5, 8.5),
    "6x9": (6.0, 9.0),
    "7x10": (7.0, 10.0),
    "8.5x11": (8.5, 11.0),
}

BLEED_INCHES = 0.125
SAFE_MARGIN_INCHES = 0.125


def calculate_cover_dimensions(
    page_count: int,
    trim_size: str = "6x9",
    paper_type: Literal["white", "cream", "color"] = "white",
) -> dict:
    """
    Computes exact KDP Print Paperback full-wrap dimensions, spine width,
    canvas pixel requirements at 300 DPI, and barcode safe coordinates.
    """
    trim_w, trim_h = TRIM_DIMENSIONS.get(trim_size, (6.0, 9.0))
    paper_factor = PAPER_FACTORS.get(paper_type, 0.002252)

    # 1. Exact Spine Width
    spine_width_inches = round(page_count * paper_factor, 4)

    # 2. Total Canvas Dimensions (with 0.125" bleed on all outer edges)
    # Total Width = Bleed + Back Cover + Spine + Front Cover + Bleed
    total_width_inches = round(BLEED_INCHES + trim_w + spine_width_inches + trim_w + BLEED_INCHES, 4)
    # Total Height = Bleed + Trim Height + Bleed
    total_height_inches = round(BLEED_INCHES + trim_h + BLEED_INCHES, 4)

    # 3. Canvas at 300 DPI (Amazon minimum requirement)
    canvas_width_px = int(round(total_width_inches * 300))
    canvas_height_px = int(round(total_height_inches * 300))

    # 4. Critical Boundaries (measured from left edge)
    back_cover_start_x = BLEED_INCHES
    spine_start_x = round(BLEED_INCHES + trim_w, 4)
    spine_end_x = round(spine_start_x + spine_width_inches, 4)
    front_cover_start_x = spine_end_x

    # 5. Barcode Coordinates on Back Cover (Amazon standard: 2" W x 1.2" H)
    barcode_box = {
        "width_inches": 2.0,
        "height_inches": 1.2,
        "margin_from_bottom_inches": 0.25,
        "margin_from_spine_inches": 0.25,
        "recommended_location": "Bottom-right corner of back cover",
    }

    # 6. Spine Text Eligibility (Amazon requires at least 79-100 pages for spine text)
    can_print_spine_text = page_count >= 80

    return {
        "page_count": page_count,
        "trim_size": trim_size,
        "paper_type": paper_type,
        "spine_width_inches": spine_width_inches,
        "total_width_inches": total_width_inches,
        "total_height_inches": total_height_inches,
        "canvas_width_px": canvas_width_px,
        "canvas_height_px": canvas_height_px,
        "dpi": 300,
        "bleed_inches": BLEED_INCHES,
        "can_print_spine_text": can_print_spine_text,
        "boundaries": {
            "back_cover_start_x": back_cover_start_x,
            "spine_start_x": spine_start_x,
            "spine_end_x": spine_end_x,
            "front_cover_start_x": front_cover_start_x,
        },
        "barcode_box": barcode_box,
    }


def generate_cover_art_prompt(
    title: str,
    subtitle: str = "",
    genre: str = "nonfiction_productivity",
    visual_style: str = "minimalist_editorial",
) -> dict:
    """
    Synthesizes commercial-grade image generation prompts for book covers.
    """
    styles = {
        "minimalist_editorial": (
            "clean minimalist book cover artwork, sophisticated negative space, elegant Swiss typography layout, "
            "subtle textured background, premium matte finish aesthetic, award-winning book jacket design"
        ),
        "abstract_geometric": (
            "striking 3D isometric geometric forms, bold harmonious color gradient, sharp architectural lines, "
            "modern business publication look, depth and lighting, highly polished"
        ),
        "photographic_cinematic": (
            "cinematic studio photography, dramatic directional lighting, moody atmospheric depth, "
            "hyper-detailed realism, premium hardcover commercial presentation"
        ),
    }

    style_desc = styles.get(visual_style, styles["minimalist_editorial"])

    prompt = (
        f"A bestselling book cover background for '{title}'. {subtitle}. "
        f"Genre: {genre}. Aesthetic: {style_desc}. "
        f"High contrast, centered focal subject, generous top and bottom negative space reserved for title typography, "
        f"hyper-realistic lighting, 8k resolution, 300 DPI print quality."
    )

    negative_prompt = (
        "blurry, low quality, distorted text, accidental letters, watermark, copyright symbol, "
        "busy cluttered background, amateur vector graphics, neon glow"
    )

    return {
        "title": title,
        "genre": genre,
        "visual_style": visual_style,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "aspect_ratio": "1:1.5",
        "guidance_scale": 7.5,
    }
