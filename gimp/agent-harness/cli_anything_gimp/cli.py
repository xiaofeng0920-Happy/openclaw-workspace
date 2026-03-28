#!/usr/bin/env python3
"""
CLI-Anything GIMP - Command Line Interface

Usage:
    cli-anything-gimp [OPTIONS] COMMAND [ARGS]...

Commands:
    batch       Batch processing (resize/watermark/convert)
    image       Single image operations
    project     Project operations (requires --project)
    export      Export operations
"""

import click
import os
import sys
import tempfile
from pathlib import Path
# Use PIL-based batch commands for reliability
from .batch_commands_pil import batch_resize, batch_watermark, batch_convert
from .project_commands import (
    project_text_add, project_arrow_add, project_highlight_add,
    project_adjust_brightness, project_filter_sharpen, project_border_add
)
from .export_commands import export_render, export_all
from .image_commands import image_open


@click.group()
@click.option('--project', '-p', 'project_file', help='XCF project file to work on')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, project_file, verbose):
    """CLI-Anything GIMP - Batch image processing for investment charts"""
    ctx.ensure_object(dict)
    ctx.obj['project_file'] = project_file
    ctx.obj['verbose'] = verbose
    ctx.obj['gimp_path'] = '/usr/bin/gimp'
    

@cli.group()
@click.pass_context
def batch(ctx):
    """Batch processing commands"""
    pass


@cli.group()
@click.pass_context
def image(ctx):
    """Single image operations"""
    pass


@cli.group()
@click.pass_context
def project(ctx):
    """Project operations (requires --project)"""
    if ctx.obj.get('project_file') is None:
        click.echo("❌ Error: --project flag is required for project commands", err=True)
        sys.exit(1)
    pass


@cli.group()
@click.pass_context
def export(ctx):
    """Export operations"""
    if ctx.obj.get('project_file') is None:
        click.echo("❌ Error: --project flag is required for export commands", err=True)
        sys.exit(1)
    pass


# Batch commands
@batch.command('resize')
@click.option('--input-dir', '-i', required=True, help='Input directory')
@click.option('--output-dir', '-o', required=True, help='Output directory')
@click.option('--width', '-w', type=int, required=True, help='Target width')
@click.option('--height', '-H', type=int, required=True, help='Target height')
@click.pass_context
def batch_resize_cmd(ctx, input_dir, output_dir, width, height):
    """Batch resize images"""
    batch_resize(input_dir, output_dir, width, height, ctx.obj['verbose'])


@batch.command('watermark')
@click.option('--input-dir', '-i', required=True, help='Input directory')
@click.option('--output-dir', '-o', required=True, help='Output directory')
@click.option('--text', '-t', required=True, help='Watermark text')
@click.option('--position', default='bottom-right', 
              type=click.Choice(['top-left', 'top-right', 'bottom-left', 'bottom-right']),
              help='Watermark position')
@click.option('--font-size', default=24, help='Font size')
@click.option('--color', default='#ffffff', help='Text color (hex)')
@click.option('--opacity', default=0.7, help='Text opacity (0-1)')
@click.pass_context
def batch_watermark_cmd(ctx, input_dir, output_dir, text, position, font_size, color, opacity):
    """Batch add watermark to images"""
    batch_watermark(input_dir, output_dir, text, position, font_size, color, opacity, ctx.obj['verbose'])


@batch.command('convert')
@click.option('--input-dir', '-i', required=True, help='Input directory')
@click.option('--output-dir', '-o', required=True, help='Output directory')
@click.option('--format', '-f', 'output_format', required=True,
              type=click.Choice(['png', 'jpg', 'jpeg', 'pdf']),
              help='Output format')
@click.option('--quality', default=95, help='Quality for JPG (1-100)')
@click.pass_context
def batch_convert_cmd(ctx, input_dir, output_dir, output_format, quality):
    """Batch convert images to different format"""
    batch_convert(input_dir, output_dir, output_format, quality, ctx.obj['verbose'])


# Image commands
@image.command('open')
@click.argument('input_file')
@click.option('--output', '-o', help='Output XCF file (default: input filename.xcf)')
@click.pass_context
def image_open_cmd(ctx, input_file, output):
    """Open image as XCF project"""
    image_open(input_file, output, ctx.obj['verbose'])


# Project commands
@project.group('text')
@click.pass_context
def project_text(ctx):
    """Text annotation operations"""
    pass


@project_text.command('add')
@click.option('--text', '-t', required=True, help='Text to add')
@click.option('--x', type=int, required=True, help='X coordinate')
@click.option('--y', type=int, required=True, help='Y coordinate')
@click.option('--font-size', default=24, help='Font size')
@click.option('--color', default='#00aa00', help='Text color (hex)')
@click.option('--font', default='Sans', help='Font family')
@click.pass_context
def project_text_add_cmd(ctx, text, x, y, font_size, color, font):
    """Add text annotation to project"""
    project_text_add(ctx.obj['project_file'], text, x, y, font_size, color, font, ctx.obj['verbose'])


@project.group('arrow')
@click.pass_context
def project_arrow(ctx):
    """Arrow annotation operations"""
    pass


@project_arrow.command('add')
@click.option('--from', 'from_point', required=True, help='Start point (x,y)')
@click.option('--to', 'to_point', required=True, help='End point (x,y)')
@click.option('--color', default='#ff0000', help='Arrow color (hex)')
@click.option('--width', default=3, help='Arrow line width')
@click.pass_context
def project_arrow_add_cmd(ctx, from_point, to_point, color, width):
    """Add arrow annotation to project"""
    project_arrow_add(ctx.obj['project_file'], from_point, to_point, color, width, ctx.obj['verbose'])


@project.group('highlight')
@click.pass_context
def project_highlight(ctx):
    """Highlight box operations"""
    pass


@project_highlight.command('add')
@click.option('--x', type=int, required=True, help='X coordinate')
@click.option('--y', type=int, required=True, help='Y coordinate')
@click.option('--width', '-w', type=int, required=True, help='Box width')
@click.option('--height', '-H', type=int, required=True, help='Box height')
@click.option('--color', default='#ffff00', help='Box color (hex)')
@click.option('--opacity', default=0.3, help='Box opacity (0-1)')
@click.option('--line-width', default=2, help='Border line width')
@click.pass_context
def project_highlight_add_cmd(ctx, x, y, width, height, color, opacity, line_width):
    """Add highlight box to project"""
    project_highlight_add(ctx.obj['project_file'], x, y, width, height, color, opacity, line_width, ctx.obj['verbose'])


@project.group('adjust')
@click.pass_context
def project_adjust(ctx):
    """Adjustment operations"""
    pass


@project_adjust.command('brightness')
@click.option('--brightness', '-b', default=0, help='Brightness adjustment (-100 to 100)')
@click.option('--contrast', '-c', default=0, help='Contrast adjustment (-100 to 100)')
@click.pass_context
def project_adjust_brightness_cmd(ctx, brightness, contrast):
    """Adjust brightness and contrast"""
    project_adjust_brightness(ctx.obj['project_file'], brightness, contrast, ctx.obj['verbose'])


@project.group('filter')
@click.pass_context
def project_filter(ctx):
    """Filter operations"""
    pass


@project_filter.command('sharpen')
@click.option('--radius', '-r', default=2, help='Sharpen radius')
@click.option('--amount', '-a', default=1.0, help='Sharpen amount')
@click.option('--threshold', '-t', default=0, help='Sharpen threshold')
@click.pass_context
def project_filter_sharpen_cmd(ctx, radius, amount, threshold):
    """Apply sharpen filter"""
    project_filter_sharpen(ctx.obj['project_file'], radius, amount, threshold, ctx.obj['verbose'])


@project.group('border')
@click.pass_context
def project_border(ctx):
    """Border operations"""
    pass


@project_border.command('add')
@click.option('--width', '-w', type=int, required=True, help='Border width in pixels')
@click.option('--color', default='#000000', help='Border color (hex)')
@click.pass_context
def project_border_add_cmd(ctx, width, color):
    """Add border to image"""
    project_border_add(ctx.obj['project_file'], width, color, ctx.obj['verbose'])


# Export commands
@export.command('render')
@click.argument('output_file')
@click.option('--format', '-f', 'output_format', default='png',
              type=click.Choice(['png', 'jpg', 'jpeg', 'pdf']),
              help='Output format')
@click.option('--quality', default=95, help='Quality for JPG (1-100)')
@click.pass_context
def export_render_cmd(ctx, output_file, output_format, quality):
    """Export project to image file"""
    export_render(ctx.obj['project_file'], output_file, output_format, quality, ctx.obj['verbose'])


@export.command('all')
@click.option('--output-dir', '-o', default='./export', help='Output directory')
@click.option('--formats', default='png,jpg', help='Comma-separated formats (png,jpg,pdf)')
@click.pass_context
def export_all_cmd(ctx, output_dir, formats):
    """Export project to all specified formats"""
    format_list = [f.strip() for f in formats.split(',')]
    export_all(ctx.obj['project_file'], output_dir, format_list, ctx.obj['verbose'])


def main():
    """Main entry point"""
    cli(obj={})


if __name__ == '__main__':
    main()
