#!/usr/bin/env python3
"""Improved OCR extraction with better preprocessing."""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np

def preprocess_image(image_path: str) -> Image.Image:
    """Advanced preprocessing for better OCR accuracy."""
    # Read with OpenCV
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Upscale for better recognition
    height, width = gray.shape
    scale = 2.0
    gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=15)
    
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    # Binarization
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Morphological operations to clean up noise
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    # Convert to PIL Image
    img_pil = Image.fromarray(cleaned)
    
    # Additional enhancement with PIL
    enhancer = ImageEnhance.Contrast(img_pil)
    img_pil = enhancer.enhance(1.5)
    enhancer = ImageEnhance.Sharpness(img_pil)
    img_pil = enhancer.enhance(1.5)
    
    return img_pil

def extract_text_detailed(image_path: str) -> dict:
    """Extract text with detailed information including confidence."""
    img = preprocess_image(image_path)
    
    # Get detailed data with bounding boxes
    data = pytesseract.image_to_data(img, lang='chi_sim+eng', config='--psm 6 --oem 3', output_type=pytesseract.Output.DICT)
    
    # Build structured output
    lines = []
    current_line = []
    current_y = -1
    
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 30 and data['text'][i].strip():
            y = data['top'][i]
            # Group by line (within 10 pixels)
            if current_y == -1 or abs(y - current_y) > 10:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [data['text'][i]]
                current_y = y
            else:
                current_line.append(data['text'][i])
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return {
        'full_text': '\n'.join(lines),
        'lines': lines
    }

if __name__ == "__main__":
    images = [
        "/home/admin/.openclaw/media/inbound/13b152a4-eb52-4028-8e22-238eea2f5648.png",
        "/home/admin/.openclaw/media/inbound/05438ca6-5c1a-4659-9395-27e3940a49dc.png"
    ]

    for i, img_path in enumerate(images, 1):
        print(f"\n{'='*70}")
        print(f"【图片 {i}】完整 OCR 结果:")
        print(f"{'='*70}")
        try:
            result = extract_text_detailed(img_path)
            print(result['full_text'])
            print(f"\n--- 分行版本 ---")
            for j, line in enumerate(result['lines'], 1):
                print(f"{j:2d}. {line}")
        except Exception as e:
            print(f"[错误：{e}]")
            import traceback
            traceback.print_exc()
