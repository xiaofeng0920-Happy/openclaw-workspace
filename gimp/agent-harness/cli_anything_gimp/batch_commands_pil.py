"""
Batch processing commands using PIL (fallback when GIMP batch mode is unavailable)
"""

from pathlib import Path
import click
from PIL import Image, ImageDraw, ImageFont


def batch_resize(input_dir: str, output_dir: str, width: int, height: int, verbose: bool = False):
    """Batch resize images using PIL"""
    click.echo(f"📐 Batch resizing images from {input_dir} to {width}x{height}")
    
    # Create output directory if needed
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    input_path = Path(input_dir)
    image_files = list(input_path.glob('*.png')) + list(input_path.glob('*.jpg')) + \
                  list(input_path.glob('*.jpeg')) + list(input_path.glob('*.bmp'))
    
    if not image_files:
        click.echo(f"⚠️  No image files found in {input_dir}", err=True)
        return
    
    success_count = 0
    for img_file in image_files:
        try:
            if verbose:
                click.echo(f"  Processing: {img_file.name}")
            
            with Image.open(img_file) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                output_file = output_path / img_file.name
                resized.save(output_file)
                success_count += 1
                
                if verbose:
                    click.echo(f"  ✓ Saved: {output_file}")
        except Exception as e:
            click.echo(f"  ❌ Error processing {img_file.name}: {e}", err=True)
    
    if success_count == len(image_files):
        click.echo(f"✅ Batch resize complete! {success_count}/{len(image_files)} images. Output: {output_dir}")
    else:
        click.echo(f"⚠️  Batch resize partial: {success_count}/{len(image_files)} images", err=True)


def batch_watermark(input_dir: str, output_dir: str, text: str, position: str,
                    font_size: int, color: str, opacity: float, verbose: bool = False):
    """Batch add watermark using PIL"""
    click.echo(f"💧 Batch watermarking with text: '{text}' at {position}")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    input_path = Path(input_dir)
    image_files = list(input_path.glob('*.png')) + list(input_path.glob('*.jpg')) + \
                  list(input_path.glob('*.jpeg'))
    
    if not image_files:
        click.echo(f"⚠️  No image files found in {input_dir}", err=True)
        return
    
    success_count = 0
    for img_file in image_files:
        try:
            with Image.open(img_file) as img:
                # Convert to RGBA for transparency support
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Create transparent overlay for watermark
                txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(txt_layer)
                
                # Try to load a font, fall back to default
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # Get text size
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Calculate position
                padding = 10
                if position == 'top-left':
                    x, y = padding, padding
                elif position == 'top-right':
                    x, y = img.width - text_width - padding, padding
                elif position == 'bottom-left':
                    x, y = padding, img.height - text_height - padding
                else:  # bottom-right
                    x, y = img.width - text_width - padding, img.height - text_height - padding
                
                # Parse color
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                a = int(opacity * 255)
                
                # Draw text
                draw.text((x, y), text, font=font, fill=(r, g, b, a))
                
                # Composite
                watermarked = Image.alpha_composite(img, txt_layer)
                
                # Save
                output_file = output_path / img_file.name
                if img_file.suffix.lower() == '.jpg':
                    watermarked = watermarked.convert('RGB')
                watermarked.save(output_file)
                success_count += 1
                
                if verbose:
                    click.echo(f"  ✓ Saved: {output_file}")
        except Exception as e:
            click.echo(f"  ❌ Error processing {img_file.name}: {e}", err=True)
    
    if success_count == len(image_files):
        click.echo(f"✅ Batch watermark complete! {success_count}/{len(image_files)} images. Output: {output_dir}")
    else:
        click.echo(f"⚠️  Batch watermark partial: {success_count}/{len(image_files)} images", err=True)


def batch_convert(input_dir: str, output_dir: str, output_format: str, 
                  quality: int, verbose: bool = False):
    """Batch convert images using PIL"""
    click.echo(f"🔄 Batch converting images to {output_format.upper()}")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    input_path = Path(input_dir)
    image_files = list(input_path.glob('*.png')) + list(input_path.glob('*.jpg')) + \
                  list(input_path.glob('*.jpeg')) + list(input_path.glob('*.bmp'))
    
    if not image_files:
        click.echo(f"⚠️  No image files found in {input_dir}", err=True)
        return
    
    format_ext = '.' + output_format.lower().replace('jpeg', 'jpg')
    success_count = 0
    
    for img_file in image_files:
        try:
            with Image.open(img_file) as img:
                # Prepare output filename
                output_name = img_file.stem + format_ext
                output_file = output_path / output_name
                
                # Convert mode if necessary
                if output_format.lower() in ('jpg', 'jpeg') and img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Save with appropriate settings
                if output_format.lower() in ('jpg', 'jpeg'):
                    img.save(output_file, 'JPEG', quality=quality)
                elif output_format.lower() == 'png':
                    img.save(output_file, 'PNG', optimize=True)
                elif output_format.lower() == 'pdf':
                    img.save(output_file, 'PDF')
                else:
                    img.save(output_file)
                
                success_count += 1
                
                if verbose:
                    click.echo(f"  ✓ Saved: {output_file}")
        except Exception as e:
            click.echo(f"  ❌ Error processing {img_file.name}: {e}", err=True)
    
    if success_count == len(image_files):
        click.echo(f"✅ Batch convert complete! {success_count}/{len(image_files)} images. Output: {output_dir}")
    else:
        click.echo(f"⚠️  Batch convert partial: {success_count}/{len(image_files)} images", err=True)
