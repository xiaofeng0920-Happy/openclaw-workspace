"""
Draw.io CLI - Main Command Line Interface

A Click-based CLI for creating and editing Draw.io diagrams programmatically.
Supports investment analysis chart templates.
"""

import click
import json
import sys
import os
from typing import Optional
from pathlib import Path

from .utils.drawio_backend import DrawioBackend


class DrawioCLI:
    """Main CLI class with stateful operations"""
    
    def __init__(self):
        self.backend = DrawioBackend()
        self.current_file = None
        self.json_output = False
    
    def output(self, data):
        """Output data in appropriate format"""
        if self.json_output:
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            if isinstance(data, dict):
                for key, value in data.items():
                    click.echo(f"{key}: {value}")
            else:
                click.echo(str(data))


# Global CLI instance
cli_state = DrawioCLI()


@click.group()
@click.option('--project', '-p', 'project_file', 
              help='Project file (.drawio) to work with')
@click.option('--json', 'json_output', is_flag=True,
              help='Output in JSON format')
@click.option('--template', '-t', 'template_name',
              type=click.Choice(['asset-allocation', 'price-chart', 'investment-flow', 'org', 'mindmap']),
              help='Use a template')
@click.option('--data', '-d', 'data_file',
              type=click.Path(exists=True),
              help='Data file for template (JSON)')
@click.pass_context
def cli(ctx, project_file, json_output, template_name, data_file):
    """
    Draw.io CLI - Create and edit diagrams for investment analysis
    
    Examples:
    
    \b
        # Create new diagram
        cli-anything-drawio diagram new -o 投资流程.drawio
        
        # Use template
        cli-anything-drawio --template asset-allocation --data 持仓.json -o 资产配置.drawio
        
        # Add shape to existing project
        cli-anything-drawio --project 投资流程.drawio shape add --type rectangle --label "步骤 1"
        
        # Export to PNG
        cli-anything-drawio --project 图表.drawio export render 图表.png --format png
    """
    ctx.ensure_object(dict)
    ctx.obj['project_file'] = project_file
    ctx.obj['json_output'] = json_output
    ctx.obj['template_name'] = template_name
    ctx.obj['data_file'] = data_file
    
    cli_state.json_output = json_output
    
    # Load project if specified
    if project_file:
        if os.path.exists(project_file):
            cli_state.backend.load(project_file)
            cli_state.current_file = project_file


@cli.group()
def diagram():
    """Diagram creation and management"""
    pass


@diagram.command('new')
@click.option('--output', '-o', 'output_file', required=True,
              help='Output file path')
@click.option('--type', 'diagram_type', default='default',
              help='Diagram type (default, flowchart, org, mindmap)')
@click.pass_context
def diagram_new(ctx, output_file, diagram_type):
    """Create a new diagram"""
    template = ctx.obj.get('template_name')
    data_file = ctx.obj.get('data_file')
    
    # Load data if provided
    data = None
    if data_file:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    # Create from template or new
    if template:
        cli_state.backend.create_template(template, data)
    else:
        cli_state.backend.create_new(diagram_type)
    
    # Save
    filepath = cli_state.backend.save(output_file)
    cli_state.current_file = filepath
    
    result = {
        'status': 'success',
        'message': f'Created new diagram: {filepath}',
        'file': filepath,
        'type': template or diagram_type,
    }
    
    cli_state.output(result)


@cli.group()
def shape():
    """Shape operations"""
    pass


@shape.command('add')
@click.option('--type', 'shape_type', default='rectangle',
              help='Shape type (rectangle, ellipse, rhombus, triangle, etc.)')
@click.option('--label', '-l', 'label', required=True,
              help='Shape label/text')
@click.option('--x', 'x_pos', default=100, type=int,
              help='X position')
@click.option('--y', 'y_pos', default=100, type=int,
              help='Y position')
@click.option('--width', '-w', 'width', default=120, type=int,
              help='Shape width')
@click.option('--height', '-h', 'height', default=60, type=int,
              help='Shape height')
@click.option('--style', '-s', 'style', default=None,
              help='Custom style (JSON string)')
@click.pass_context
def shape_add(ctx, shape_type, label, x_pos, y_pos, width, height, style):
    """Add a shape to the diagram"""
    project_file = ctx.obj.get('project_file')
    
    if not project_file:
        cli_state.output({'error': 'No project specified. Use --project or create new diagram first'})
        sys.exit(1)
    
    # Parse style if provided
    style_dict = None
    if style:
        try:
            style_dict = json.loads(style)
        except json.JSONDecodeError:
            cli_state.output({'error': 'Invalid style JSON'})
            sys.exit(1)
    
    # Add shape
    shape_id = cli_state.backend.add_shape(
        label=label,
        shape_type=shape_type,
        x=x_pos,
        y=y_pos,
        width=width,
        height=height,
        style=style_dict
    )
    
    # Save if we have a project file
    if project_file:
        cli_state.backend.save(project_file)
    
    result = {
        'status': 'success',
        'message': f'Added shape: {label}',
        'shape_id': shape_id,
        'type': shape_type,
        'position': {'x': x_pos, 'y': y_pos},
    }
    
    cli_state.output(result)


@cli.group()
def connector():
    """Connector/line operations"""
    pass


@connector.command('add')
@click.option('--from', 'from_shape', required=True,
              help='Source shape ID')
@click.option('--to', 'to_shape', required=True,
              help='Target shape ID')
@click.option('--label', '-l', 'label', default='',
              help='Connector label')
@click.option('--style', '-s', 'style', default=None,
              help='Custom style (JSON string)')
@click.pass_context
def connector_add(ctx, from_shape, to_shape, label, style):
    """Add a connector between shapes"""
    project_file = ctx.obj.get('project_file')
    
    if not project_file and not cli_state.current_file:
        cli_state.output({'error': 'No project specified'})
        sys.exit(1)
    
    # Parse style if provided
    style_dict = None
    if style:
        try:
            style_dict = json.loads(style)
        except json.JSONDecodeError:
            cli_state.output({'error': 'Invalid style JSON'})
            sys.exit(1)
    
    # Add connector
    connector_id = cli_state.backend.add_connector(
        from_shape=from_shape,
        to_shape=to_shape,
        label=label,
        style=style_dict
    )
    
    # Save if we have a project file
    if project_file:
        cli_state.backend.save(project_file)
    
    result = {
        'status': 'success',
        'message': f'Added connector from {from_shape} to {to_shape}',
        'connector_id': connector_id,
    }
    
    cli_state.output(result)


@cli.group()
def text():
    """Text operations"""
    pass


@text.command('add')
@click.option('--text', '-t', 'text_content', required=True,
              help='Text content')
@click.option('--x', 'x_pos', default=100, type=int,
              help='X position')
@click.option('--y', 'y_pos', default=100, type=int,
              help='Y position')
@click.option('--font-size', 'font_size', default=12, type=int,
              help='Font size')
@click.option('--bold', 'is_bold', is_flag=True,
              help='Bold text')
@click.option('--width', '-w', 'width', default=200, type=int,
              help='Text box width')
@click.option('--height', '-h', 'height', default=30, type=int,
              help='Text box height')
@click.pass_context
def text_add(ctx, text_content, x_pos, y_pos, font_size, is_bold, width, height):
    """Add text to the diagram"""
    project_file = ctx.obj.get('project_file')
    
    if not project_file and not cli_state.current_file:
        cli_state.output({'error': 'No project specified'})
        sys.exit(1)
    
    # Add text
    text_id = cli_state.backend.add_text(
        text=text_content,
        x=x_pos,
        y=y_pos,
        font_size=font_size,
        bold=is_bold,
        width=width,
        height=height
    )
    
    # Save if we have a project file
    if project_file:
        cli_state.backend.save(project_file)
    
    result = {
        'status': 'success',
        'message': f'Added text: {text_content}',
        'text_id': text_id,
        'font_size': font_size,
        'bold': is_bold,
    }
    
    cli_state.output(result)


@cli.group()
def export():
    """Export operations"""
    pass


@export.command('render')
@click.argument('output_file')
@click.option('--format', 'export_format', 
              type=click.Choice(['png', 'svg', 'pdf']),
              default='png',
              help='Export format')
@click.option('--dpi', 'dpi', default=300, type=int,
              help='DPI for PNG export')
@click.pass_context
def export_render(ctx, output_file, export_format, dpi):
    """Render/export diagram to image format"""
    project_file = ctx.obj.get('project_file')
    
    if not project_file:
        cli_state.output({'error': 'No project specified'})
        sys.exit(1)
    
    # Export based on format
    if export_format == 'png':
        result_file = cli_state.backend.export_png(output_file, dpi)
    elif export_format == 'svg':
        result_file = cli_state.backend.export_svg(output_file)
    elif export_format == 'pdf':
        result_file = cli_state.backend.export_pdf(output_file)
    else:
        cli_state.output({'error': f'Unsupported format: {export_format}'})
        sys.exit(1)
    
    result = {
        'status': 'success',
        'message': f'Export info written to {result_file}',
        'source': project_file or cli_state.current_file,
        'target': output_file,
        'format': export_format,
        'note': 'Actual export requires Draw.io CLI installed separately',
    }
    
    cli_state.output(result)


@cli.command('info')
@click.pass_context
def show_info(ctx):
    """Show current diagram information"""
    project_file = ctx.obj.get('project_file')
    
    if not project_file:
        cli_state.output({'error': 'No diagram loaded'})
        sys.exit(1)
    
    info = cli_state.backend.to_dict()
    cli_state.output(info)


@cli.command('list-templates')
def list_templates():
    """List available templates"""
    from .utils.drawio_backend import DrawioBackend
    
    templates = DrawioBackend.TEMPLATES
    result = {
        'templates': templates,
        'count': len(templates),
    }
    cli_state.output(result)


def main():
    """Main entry point"""
    cli(obj={})


if __name__ == '__main__':
    main()
