"""
Export commands for GIMP
"""

import os
import subprocess
import tempfile
import click


def generate_render_script(project_file: str, output_file: str, output_format: str, quality: int) -> str:
    """Generate Script-Fu code for rendering/export"""
    format_lower = output_format.lower()
    
    if format_lower == 'png':
        save_code = f'''
        (file-png-save RUN-NONINTERACTIVE image drawable 
                       "{output_file}" "{output_file}" 
                       0 9 0 0 0 0 0)
        '''
    elif format_lower in ('jpg', 'jpeg'):
        quality_factor = quality / 100.0
        save_code = f'''
        (file-jpeg-save RUN-NONINTERACTIVE image drawable 
                       "{output_file}" "{output_file}" 
                       {quality_factor} 0.9 0 0 "Exported from CLI-Anything GIMP" 0 1 0 0)
        '''
    elif format_lower == 'pdf':
        save_code = f'''
        (file-pdf-save RUN-NONINTERACTIVE image drawable 
                       "{output_file}" "{output_file}" 
                       0 0 0 0 0 0 0 0 0 0 0)
        '''
    else:
        raise ValueError(f"Unsupported format: {output_format}")
    
    return f'''
(define (render-export)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{project_file}" "{project_file}")))
         (drawable (car (gimp-image-get-active-layer image))))
    {save_code}
    (gimp-image-delete image))
  (gimp-quit 0))
'''


def generate_export_all_script(project_file: str, output_dir: str, formats: list) -> str:
    """Generate Script-Fu code for exporting to multiple formats"""
    # Get base name without extension
    base_name = os.path.splitext(os.path.basename(project_file))[0]
    
    save_operations = []
    for fmt in formats:
        fmt = fmt.lower().strip()
        output_path = f"{output_dir}/{base_name}.{fmt}"
        if fmt == 'jpg':
            save_operations.append(f'''
            (file-jpeg-save RUN-NONINTERACTIVE image drawable 
                           "{output_path}" "{output_path}" 
                           0.95 0.9 0 0 "Exported from CLI-Anything GIMP" 0 1 0 0)
            ''')
        elif fmt == 'png':
            save_operations.append(f'''
            (file-png-save RUN-NONINTERACTIVE image drawable 
                           "{output_path}" "{output_path}" 
                           0 9 0 0 0 0 0)
            ''')
        elif fmt == 'pdf':
            save_operations.append(f'''
            (file-pdf-save RUN-NONINTERACTIVE image drawable 
                           "{output_path}" "{output_path}" 
                           0 0 0 0 0 0 0 0 0 0 0)
            ''')
    
    save_code = '\n'.join(save_operations)
    
    return f'''
(define (export-all)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{project_file}" "{project_file}")))
         (drawable (car (gimp-image-get-active-layer image))))
    {save_code}
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


def export_render(project_file: str, output_file: str, output_format: str, 
                  quality: int, verbose: bool = False):
    """Export project to image file"""
    click.echo(f"📤 Exporting {project_file} to {output_file} ({output_format.upper()})")
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    
    script = generate_render_script(project_file, output_file, output_format, quality)
    success = run_gimp_script(script, verbose)
    
    if success:
        click.echo(f"✅ Exported to {output_file}")
    else:
        click.echo("❌ Export failed", err=True)


def export_all(project_file: str, output_dir: str, formats: list, verbose: bool = False):
    """Export project to all specified formats"""
    click.echo(f"📤 Exporting {project_file} to {', '.join(formats)} formats")
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    script = generate_export_all_script(project_file, output_dir, formats)
    success = run_gimp_script(script, verbose)
    
    if success:
        click.echo(f"✅ Exported to {output_dir} in {len(formats)} formats")
    else:
        click.echo("❌ Export failed", err=True)
