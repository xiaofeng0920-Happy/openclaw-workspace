"""
Project-level commands for GIMP (operate on XCF files)
"""

import os
import subprocess
import tempfile
import click


def generate_text_script(project_file: str, text: str, x: int, y: int, 
                         font_size: int, color: str, font: str) -> str:
    """Generate Script-Fu code for adding text"""
    r = int(color[1:3], 16) / 255.0
    g = int(color[3:5], 16) / 255.0
    b = int(color[5:7], 16) / 255.0
    
    return f'''
(define (add-text)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{project_file}" "{project_file}")))
         (drawable (car (gimp-image-get-active-layer image)))
         (text-layer (car (gimp-text-fontname image drawable {x} {y} "{text}" 10 
                                   TRUE {font_size} 0 "{font}"))))
    (gimp-image-set-active-layer image text-layer)
    (file-gimp-save RUN-NONINTERACTIVE image drawable "{project_file}" "{project_file}" 
                    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
    (gimp-image-delete image))
  (gimp-quit 0))
'''


def generate_arrow_script(project_file: str, from_point: str, to_point: str, 
                          color: str, width: int) -> str:
    """Generate Script-Fu code for adding arrow"""
    from_x, from_y = map(int, from_point.split(','))
    to_x, to_y = map(int, to_point.split(','))
    r = int(color[1:3], 16) / 255.0
    g = int(color[3:5], 16) / 255.0
    b = int(color[5:7], 16) / 255.0
    
    return f'''
(define (add-arrow)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{project_file}" "{project_file}")))
         (drawable (car (gimp-image-get-active-layer image)))
         (layer (car (gimp-layer-new image (car (gimp-image-width image))) 
                                     (car (gimp-image-height image)) 
                                     RGBA-IMAGE "Arrow" 100 LAYER-MODE-NORMAL)))
    (gimp-image-insert-layer image layer 0 0)
    (gimp-context-set-foreground (list {r} {g} {b}))
    (gimp-context-set-brush-size {width})
    ; Draw line
    (gimp-paintbrush-default layer 2 (list {from_x} {from_y} {to_x} {to_y}))
    ; Draw arrowhead (simplified)
    (gimp-paintbrush-default layer 2 (list {to_x} {to_y} (- {to_x} 10) (- {to_y} 10)))
    (gimp-paintbrush-default layer 2 (list {to_x} {to_y} (+ {to_x} 10) (- {to_y} 10)))
    (file-gimp-save RUN-NONINTERACTIVE image drawable "{project_file}" "{project_file}" 
                    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
    (gimp-image-delete image))
  (gimp-quit 0))
'''


def generate_highlight_script(project_file: str, x: int, y: int, width: int, height: int,
                               color: str, opacity: float, line_width: int) -> str:
    """Generate Script-Fu code for adding highlight box"""
    r = int(color[1:3], 16) / 255.0
    g = int(color[3:5], 16) / 255.0
    b = int(color[5:7], 16) / 255.0
    
    return f'''
(define (add-highlight)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{project_file}" "{project_file}")))
         (drawable (car (gimp-image-get-active-layer image)))
         (layer (car (gimp-layer-new image (car (gimp-image-width image))) 
                                     (car (gimp-image-height image)) 
                                     RGBA-IMAGE "Highlight" {int(opacity * 100)} LAYER-MODE-NORMAL)))
    (gimp-image-insert-layer image layer 0 0)
    (gimp-context-set-foreground (list {r} {g} {b}))
    (gimp-context-set-brush-size {line_width})
    ; Draw rectangle
    (gimp-rect-select image {x} {y} {width} {height} CHANNEL-OP-REPLACE FALSE 0)
    (gimp-edit-stroke layer)
    (gimp-selection-none image)
    (file-gimp-save RUN-NONINTERACTIVE image drawable "{project_file}" "{project_file}" 
                    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
    (gimp-image-delete image))
  (gimp-quit 0))
'''


def generate_brightness_script(project_file: str, brightness: int, contrast: int) -> str:
    """Generate Script-Fu code for brightness/contrast adjustment"""
    return f'''
(define (adjust-brightness)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{project_file}" "{project_file}")))
         (drawable (car (gimp-image-get-active-layer image))))
    (gimp-drawable-brightness-contrast drawable {brightness / 100.0} {contrast / 100.0})
    (file-gimp-save RUN-NONINTERACTIVE image drawable "{project_file}" "{project_file}" 
                    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
    (gimp-image-delete image))
  (gimp-quit 0))
'''


def generate_sharpen_script(project_file: str, radius: float, amount: float, threshold: float) -> str:
    """Generate Script-Fu code for sharpening"""
    return f'''
(define (sharpen)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{project_file}" "{project_file}")))
         (drawable (car (gimp-image-get-active-layer image))))
    (plug-in-unsharp-mask RUN-NONINTERACTIVE image drawable {radius} {amount} {threshold})
    (file-gimp-save RUN-NONINTERACTIVE image drawable "{project_file}" "{project_file}" 
                    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
    (gimp-image-delete image))
  (gimp-quit 0))
'''


def generate_border_script(project_file: str, width: int, color: str) -> str:
    """Generate Script-Fu code for adding border"""
    r = int(color[1:3], 16) / 255.0
    g = int(color[3:5], 16) / 255.0
    b = int(color[5:7], 16) / 255.0
    
    return f'''
(define (add-border)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{project_file}" "{project_file}")))
         (drawable (car (gimp-image-get-active-layer image))))
    (plug-in-borderaverage RUN-NONINTERACTIVE image drawable {width} TRUE)
    (gimp-context-set-foreground (list {r} {g} {b}))
    (gimp-selection-all image)
    (gimp-edit-bucket-fill drawable FILL-FG ALPHA-TRUE 100 0 FALSE 0 0)
    (gimp-selection-none image)
    (file-gimp-save RUN-NONINTERACTIVE image drawable "{project_file}" "{project_file}" 
                    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
    (gimp-image-delete image))
  (gimp-quit 0))
'''


def run_gimp_script(script: str, verbose: bool = False) -> bool:
    """Run a Script-Fu script via GIMP batch mode"""
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


def project_text_add(project_file: str, text: str, x: int, y: int, 
                     font_size: int, color: str, font: str, verbose: bool = False):
    """Add text annotation to project"""
    click.echo(f"📝 Adding text: '{text}' at ({x}, {y})")
    
    script = generate_text_script(project_file, text, x, y, font_size, color, font)
    success = run_gimp_script(script, verbose)
    
    if success:
        click.echo(f"✅ Text added to {project_file}")
    else:
        click.echo("❌ Failed to add text", err=True)


def project_arrow_add(project_file: str, from_point: str, to_point: str, 
                      color: str, width: int, verbose: bool = False):
    """Add arrow annotation to project"""
    click.echo(f"🏹 Adding arrow from {from_point} to {to_point}")
    
    script = generate_arrow_script(project_file, from_point, to_point, color, width)
    success = run_gimp_script(script, verbose)
    
    if success:
        click.echo(f"✅ Arrow added to {project_file}")
    else:
        click.echo("❌ Failed to add arrow", err=True)


def project_highlight_add(project_file: str, x: int, y: int, width: int, height: int,
                          color: str, opacity: float, line_width: int, verbose: bool = False):
    """Add highlight box to project"""
    click.echo(f"🟨 Adding highlight box at ({x}, {y}) {width}x{height}")
    
    script = generate_highlight_script(project_file, x, y, width, height, color, opacity, line_width)
    success = run_gimp_script(script, verbose)
    
    if success:
        click.echo(f"✅ Highlight added to {project_file}")
    else:
        click.echo("❌ Failed to add highlight", err=True)


def project_adjust_brightness(project_file: str, brightness: int, contrast: int, 
                              verbose: bool = False):
    """Adjust brightness and contrast"""
    click.echo(f"🔆 Adjusting brightness: {brightness}, contrast: {contrast}")
    
    script = generate_brightness_script(project_file, brightness, contrast)
    success = run_gimp_script(script, verbose)
    
    if success:
        click.echo(f"✅ Brightness/contrast adjusted in {project_file}")
    else:
        click.echo("❌ Failed to adjust brightness/contrast", err=True)


def project_filter_sharpen(project_file: str, radius: float, amount: float, 
                          threshold: float, verbose: bool = False):
    """Apply sharpen filter"""
    click.echo(f"🔍 Applying sharpen: radius={radius}, amount={amount}")
    
    script = generate_sharpen_script(project_file, radius, amount, threshold)
    success = run_gimp_script(script, verbose)
    
    if success:
        click.echo(f"✅ Sharpen applied to {project_file}")
    else:
        click.echo("❌ Failed to apply sharpen", err=True)


def project_border_add(project_file: str, width: int, color: str, verbose: bool = False):
    """Add border to image"""
    click.echo(f"🖼️  Adding {width}px border with color {color}")
    
    script = generate_border_script(project_file, width, color)
    success = run_gimp_script(script, verbose)
    
    if success:
        click.echo(f"✅ Border added to {project_file}")
    else:
        click.echo("❌ Failed to add border", err=True)
