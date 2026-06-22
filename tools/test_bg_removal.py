import sys
import os
import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps, ImageDraw
from rembg import remove, new_session

def test_bg_removal():
    input_file = Path("data/input/2025-297.jpg")
    output_dir = Path("data/output/bg_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_file.exists():
        print(f"Error: {input_file} not found!")
        return
        
    print("Loading image...")
    img = cv2.imread(str(input_file))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    
    # Initialize sessions
    print("Initializing rembg sessions...")
    session_human = new_session("u2net_human_seg")
    session_general = new_session("isnet-general-use")
    
    # Run 1: Default (what was used)
    print("Run 1: Default rembg...")
    out_default = remove(img_pil, session=session_human, alpha_matting=True)
    out_default.save(output_dir / "1_default.png")
    
    # Run 2: isnet-general-use model (higher accuracy)
    print("Run 2: ISNet model...")
    try:
        out_isnet = remove(img_pil, session=session_general, alpha_matting=True)
        out_isnet.save(output_dir / "2_isnet.png")
    except Exception as e:
        print(f"ISNet failed: {e}")
        out_isnet = None
        
    # Run 3: Default + custom alpha matting parameters
    print("Run 3: Default with custom alpha matting...")
    out_matting = remove(
        img_pil, 
        session=session_human, 
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=15
    )
    out_matting.save(output_dir / "3_custom_matting.png")
    
    # Run 4: Morphological cleanup (Erosion/MinFilter + Blur) on Default
    print("Run 4: Default + Alpha Erosion & Smoothing...")
    alpha = out_default.split()[3]
    # MinFilter(3) acts as a 1-pixel erosion (removes edge halos)
    alpha_eroded = alpha.filter(ImageFilter.MinFilter(3))
    # GaussianBlur(2) smooths out the jagged edges
    alpha_smoothed = alpha_eroded.filter(ImageFilter.GaussianBlur(1))
    
    out_eroded = out_default.copy()
    out_eroded.putalpha(alpha_smoothed)
    out_eroded.save(output_dir / "4_eroded_smooth.png")

    # Run 5: Morphological cleanup on ISNet
    if out_isnet:
        print("Run 5: ISNet + Alpha Erosion & Smoothing...")
        alpha_is = out_isnet.split()[3]
        alpha_is_eroded = alpha_is.filter(ImageFilter.MinFilter(3))
        alpha_is_smoothed = alpha_is_eroded.filter(ImageFilter.GaussianBlur(1))
        
        out_is_eroded = out_isnet.copy()
        out_is_eroded.putalpha(alpha_is_smoothed)
        out_is_eroded.save(output_dir / "5_isnet_eroded.png")

    print("\nVerification Composites (on White Background):")
    # Composite them on a solid white background to check edge halos
    for name, img_transparent in [
        ("1_default_white.png", out_default),
        ("2_isnet_white.png", out_isnet),
        ("3_custom_white.png", out_matting),
        ("4_eroded_white.png", out_eroded),
        ("5_isnet_eroded_white.png", out_is_eroded if out_isnet else None)
    ]:
        if img_transparent is None:
            continue
        white_bg = Image.new("RGBA", img_transparent.size, (255, 255, 255, 255))
        composite = Image.alpha_composite(white_bg, img_transparent)
        composite.save(output_dir / name)
        
    print(f"\nAll test images saved to: {output_dir}")

if __name__ == "__main__":
    test_bg_removal()
