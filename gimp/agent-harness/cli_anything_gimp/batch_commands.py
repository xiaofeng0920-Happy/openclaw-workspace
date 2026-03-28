"""
Batch processing commands for GIMP
"""

import os
import subprocess
import tempfile
from pathlib import Path
import click


def generate_resize_script(input_file: str, output_file: str, width: int, height: int) -> str:
    """Generate Script-Fu code for single image resize"""
    return f'''
(define (resize-image)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{input_file}" "{input_file}")))
         (drawable (car (gimp-image-get-active-layer image))))
    (gimp-image-scale image {width} {height})
    (file-png-save RUN-NONINTERACTIVE image drawable 
                   "{output_file}" "{output_file}" 
                   0 9 0 0 0 0 0)
    (gimp-image-delete image))
  (gimp-quit 0))
'''


def generate_watermark_script(input_dir: str, output_dir: str, text: str, position: str, 
                              font_size: int, color: str, opacity: float) -> str:
    """Generate Script-Fu code for batch watermark"""
    # Parse color hex to RGB (0-1 range)
    r = int(color[1:3], 16) / 255.0
    g = int(color[3:5], 16) / 255.0
    b = int(color[5:7], 16) / 255.0
    
    return f'''
(define (batch-watermark)
  (let* ((pattern "{input_dir}/*")
         (filelist (cadr (file-glob pattern 1))))
    (while (not (null? filelist))
      (let* ((filename (car filelist))
             (basename (car (gimp-filename-base filename)))
             (image (car (gimp-file-load RUN-NONINTERACTIVE filename filename)))
             (drawable (car (gimp-image-get-active-layer image)))
             (width (car (gimp-image-width image)))
             (height (car (gimp-image-height image)))
             (text-layer (car (gimp-text-fontname image drawable 0 0 "{text}" 10 
                                       TRUE {font_size} 0 "Sans"))))
        ; Position text based on position parameter
        (let* ((text-width (car (gimp-drawable-width text-layer)))
               (text-height (car (gimp-drawable-height text-layer)))
               (x 10)
               (y 10))
          (cond
            ((string= "{position}" "top-left")
             (set! x 10) (set! y (+ text-height 10)))
            ((string= "{position}" "top-right")
             (set! x (- width text-width 10)) (set! y (+ text-height 10)))
            ((string= "{position}" "bottom-left")
             (set! x 10) (set! y (- height 10)))
            ((string= "{position}" "bottom-right")
             (set! x (- width text-width 10)) (set! y (- height 10))))
          (gimp-layer-set-offsets text-layer x y))
        (gimp-layer-set-opacity text-layer {int(opacity * 100)})
        (file-png-save RUN-NONINTERACTIVE image drawable 
                       (string-append "{output_dir}/" basename) 
                       (string-append "{output_dir}/" basename) 
                       0 9 0 0 0 0 0)
        (gimp-image-delete image))
      (set! filelist (cdr filelist))))
  (gimp-quit 0))
'''


def generate_convert_script(input_dir: str, output_dir: str, output_format: str, quality: int) -> str:
    """Generate Script-Fu code for batch format conversion"""
    format_lower = output_format.lower()
    if format_lower == 'jpeg':
        format_lower = 'jpg'
    
    return f'''
(define (batch-convert)
  (let* ((pattern "{input_dir}/*")
         (filelist (cadr (file-glob pattern 1))))
    (while (not (null? filelist))
      (let* ((filename (car filelist))
             (basename (car (gimp-filename-base filename)))
             (name-without-ext (car (string-split basename ".")))
             (image (car (gimp-file-load RUN-NONINTERACTIVE filename filename)))
             (drawable (car (gimp-image-get-active-layer image))))
        (cond
          ((string= "{format_lower}" "png")
           (file-png-save RUN-NONINTERACTIVE image drawable 
                          (string-append "{output_dir}/" name-without-ext ".png") 
                          (string-append "{output_dir}/" name-without-ext ".png") 
                          0 9 0 0 0 0 0))
          ((string= "{format_lower}" "jpg")
           (file-jpeg-save RUN-NONINTERACTIVE image drawable 
                          (string-append "{output_dir}/" name-without-ext ".jpg") 
                          (string-append "{output_dir}/" name-without-ext ".jpg") 
                          0.95 0.9 0 0 "comment" 0 1 0 0))
          ((string= "{format_lower}" "pdf")
           (file-pdf-save RUN-NONINTERACTIVE image drawable 
                          (string-append "{output_dir}/" name-without-ext ".pdf") 
                          (string-append "{output_dir}/" name-without-ext ".pdf") 
                          0 0 0 0 0 0 0 0 0 0 0)))
        (gimp-image-delete image))
      (set! filelist (cdr filelist))))
  (gimp-quit 0))
'''


def run_gimp_script(script: str, verbose: bool = False):
    """Run a Script-Fu script via GIMP batch mode"""
    # Write script to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.scm', delete=False) as f:
        f.write(script)
        script_file = f.name
    
    try:
        # Use timeout and explicit quit to ensure GIMP exits
        cmd = ['timeout', '60', '/usr/bin/gimp', '-i', '-b', f'(load "{script_file}")', '-b', '(gimp-quit 0)']
        if verbose:
            click.echo(f"🔧 Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        
        if verbose and result.stdout:
            click.echo(result.stdout)
        if result.returncode != 0 and verbose:
            click.echo(f"❌ GIMP error: {result.stderr}", err=True)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        click.echo("❌ GIMP operation timed out", err=True)
        return False
    finally:
        os.unlink(script_file)


def batch_resize(input_dir: str, output_dir: str, width: int, height: int, verbose: bool = False):
    """Batch resize images"""
    click.echo(f"📐 Batch resizing images from {input_dir} to {width}x{height}")
    
    # Create output directory if needed
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    input_path = Path(input_dir)
    image_files = list(input_path.glob('*.png')) + list(input_path.glob('*.jpg')) + list(input_path.glob('*.jpeg'))
    
    if not image_files:
        click.echo(f"⚠️  No image files found in {input_dir}", err=True)
        return
    
    success_count = 0
    for img_file in image_files:
        output_file = Path(output_dir) / img_file.name
        script = generate_resize_script(str(img_file), str(output_file), width, height)
        if run_gimp_script(script, verbose):
            success_count += 1
    
    if success_count == len(image_files):
        click.echo(f"✅ Batch resize complete! {success_count}/{len(image_files)} images processed. Output: {output_dir}")
    else:
        click.echo(f"⚠️  Batch resize partial: {success_count}/{len(image_files)} images processed", err=True)


def batch_watermark(input_dir: str, output_dir: str, text: str, position: str,
                    font_size: int, color: str, opacity: float, verbose: bool = False):
    """Batch add watermark to images"""
    click.echo(f"💧 Batch watermarking with text: '{text}' at {position}")
    
    # Create output directory if needed
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    script = generate_watermark_script(input_dir, output_dir, text, position, 
                                       font_size, color, opacity)
    success = run_gimp_script(script, verbose)
    
    if success:
        click.echo(f"✅ Batch watermark complete! Output: {output_dir}")
    else:
        click.echo("❌ Batch watermark failed", err=True)


def batch_convert(input_dir: str, output_dir: str, output_format: str, 
                  quality: int, verbose: bool = False):
    """Batch convert images to different format"""
    click.echo(f"🔄 Batch converting images to {output_format.upper()}")
    
    # Create output directory if needed
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    script = generate_convert_script(input_dir, output_dir, output_format, quality)
    success = run_gimp_script(script, verbose)
    
    if success:
        click.echo(f"✅ Batch convert complete! Output: {output_dir}")
    else:
        click.echo("❌ Batch convert failed", err=True)
