"""
Single image operations for GIMP
"""

import os
import subprocess
import tempfile
import click


def generate_open_script(input_file: str, output_file: str) -> str:
    """Generate Script-Fu code for opening image as XCF"""
    return f'''
(define (open-as-xcf)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{input_file}" "{input_file}"))))
    (file-gimp-save RUN-NONINTERACTIVE image (car (gimp-image-get-active-layer image))
                    "{output_file}" "{output_file}" 
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


def image_open(input_file: str, output_file: str = None, verbose: bool = False):
    """Open image as XCF project"""
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"{base_name}.xcf"
    
    click.echo(f"📂 Opening {input_file} as XCF project: {output_file}")
    
    script = generate_open_script(input_file, output_file)
    success = run_gimp_script(script, verbose)
    
    if success:
        click.echo(f"✅ Created XCF project: {output_file}")
    else:
        click.echo("❌ Failed to create XCF project", err=True)
