#!/usr/bin/env python3
"""
LibreOffice CLI - Investment Report Generation Tool

A CLI tool for creating Writer documents, Calc spreadsheets, and exporting to PDF/Word/Excel.
Built using CLI-Anything methodology for the investment analysis system.
"""

import click
import json
import os
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, List


class LibreOfficeError(Exception):
    """Custom exception for LibreOffice CLI errors"""
    pass


def get_sooffice_path():
    """Find soffice binary path"""
    paths = ["/usr/bin/soffice", "/usr/bin/libreoffice"]
    for path in paths:
        if os.path.exists(path):
            return path
    # Try PATH
    result = subprocess.run(["which", "soffice"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    raise LibreOfficeError("LibreOffice (soffice) not found. Please install LibreOffice.")


def ensure_project_file(project: str) -> dict:
    """Load or create project JSON file"""
    if not os.path.exists(project):
        return {"type": "unknown", "content": [], "metadata": {}}
    
    with open(project, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_project_file(project: str, data: dict):
    """Save project JSON file"""
    with open(project, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run_headless_conversion(input_file: str, output_format: str, output_dir: str = "."):
    """Run LibreOffice headless conversion"""
    soffice = get_sooffice_path()
    
    format_map = {
        "pdf": "pdf",
        "docx": "docx",
        "odt": "odt",
        "xlsx": "calc_excel_2007_xml",
        "xls": "calc_excel_97",
        "csv": "Text - txt - csv (StarCalc)",
        "pptx": "impress8",
        "odp": "odp"
    }
    
    if output_format not in format_map:
        raise LibreOfficeError(f"Unsupported output format: {output_format}")
    
    cmd = [
        soffice,
        "--headless",
        "--convert-to", format_map[output_format],
        "--outdir", output_dir,
        input_file
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise LibreOfficeError(f"Conversion failed: {result.stderr}")
    
    return result


@click.group()
@click.version_option(version="1.0.0", prog_name="cli-anything-libreoffice")
def cli():
    """LibreOffice CLI for Investment Report Generation
    
    Create Writer documents, Calc spreadsheets, and export to PDF/Word/Excel.
    """
    pass


# =============================================================================
# Document Creation Commands
# =============================================================================

@cli.group()
def document():
    """Document creation and management"""
    pass


@document.command("new")
@click.option("--type", "doc_type", type=click.Choice(["writer", "calc", "impress"]), 
              required=True, help="Document type")
@click.option("-o", "--output", required=True, help="Output JSON project file")
@click.option("--template", help="Optional template file (ODT/OTS/OTP)")
def document_new(doc_type: str, output: str, template: Optional[str]):
    """Create a new document project
    
    Examples:
        cli-anything-libreoffice document new --type writer -o 投资报告.json
        cli-anything-libreoffice document new --type calc -o 持仓表.json
    """
    project_data = {
        "type": doc_type,
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat(),
        "content": [],
        "metadata": {
            "title": "",
            "author": "",
            "subject": ""
        },
        "template": template
    }
    
    # Ensure output directory exists
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    save_project_file(output, project_data)
    click.echo(f"✅ Created {doc_type} project: {output}")
    click.echo(f"   Use 'writer' or 'calc' commands to add content")


# =============================================================================
# Writer Commands
# =============================================================================

@cli.group()
def writer():
    """Writer document editing commands"""
    pass


@writer.command("add-heading")
@click.option("--project", required=True, help="Project JSON file")
@click.option("-t", "--text", required=True, help="Heading text")
@click.option("--level", type=int, default=1, help="Heading level (1-10)")
@click.option("--style", help="Custom style name")
def writer_add_heading(project: str, text: str, level: int, style: Optional[str]):
    """Add a heading to the document"""
    data = ensure_project_file(project)
    if data["type"] != "writer":
        raise LibreOfficeError(f"Project is type '{data['type']}', expected 'writer'")
    
    heading = {
        "type": "heading",
        "level": level,
        "text": text,
        "style": style,
        "timestamp": datetime.now().isoformat()
    }
    data["content"].append(heading)
    data["modified"] = datetime.now().isoformat()
    save_project_file(project, data)
    click.echo(f"✅ Added heading (level {level}): {text}")


@writer.command("add-paragraph")
@click.option("--project", required=True, help="Project JSON file")
@click.option("-t", "--text", required=True, help="Paragraph text")
@click.option("--style", help="Paragraph style")
def writer_add_paragraph(project: str, text: str, style: Optional[str]):
    """Add a paragraph to the document"""
    data = ensure_project_file(project)
    if data["type"] != "writer":
        raise LibreOfficeError(f"Project is type '{data['type']}', expected 'writer'")
    
    paragraph = {
        "type": "paragraph",
        "text": text,
        "style": style,
        "timestamp": datetime.now().isoformat()
    }
    data["content"].append(paragraph)
    data["modified"] = datetime.now().isoformat()
    save_project_file(project, data)
    click.echo(f"✅ Added paragraph ({len(text)} chars)")


@writer.command("add-table")
@click.option("--project", required=True, help="Project JSON file")
@click.option("--rows", type=int, required=True, help="Number of rows")
@click.option("--cols", type=int, required=True, help="Number of columns")
@click.option("--header", is_flag=True, help="First row is header")
@click.option("--caption", help="Table caption")
def writer_add_table(project: str, rows: int, cols: int, header: bool, caption: Optional[str]):
    """Add a table to the document"""
    data = ensure_project_file(project)
    if data["type"] != "writer":
        raise LibreOfficeError(f"Project is type '{data['type']}', expected 'writer'")
    
    table = {
        "type": "table",
        "rows": rows,
        "cols": cols,
        "header": header,
        "caption": caption,
        "data": [["" for _ in range(cols)] for _ in range(rows)],
        "style": {},
        "timestamp": datetime.now().isoformat()
    }
    data["content"].append(table)
    data["modified"] = datetime.now().isoformat()
    save_project_file(project, data)
    click.echo(f"✅ Added table ({rows}x{cols})")


@writer.command("fill-table")
@click.option("--project", required=True, help="Project JSON file")
@click.option("--data", "data_file", required=True, help="JSON file with table data")
@click.option("--table-index", type=int, default=-1, help="Table index (-1 for last)")
def writer_fill_table(project: str, data_file: str, table_index: int):
    """Fill table with data from JSON file"""
    data = ensure_project_file(project)
    if data["type"] != "writer":
        raise LibreOfficeError(f"Project is type '{data['type']}', expected 'writer'")
    
    # Load table data
    with open(data_file, 'r', encoding='utf-8') as f:
        table_data = json.load(f)
    
    # Find table
    tables = [c for c in data["content"] if c["type"] == "table"]
    if not tables:
        raise LibreOfficeError("No tables in document")
    
    table = tables[table_index]
    
    # Fill data
    if isinstance(table_data, list) and isinstance(table_data[0], list):
        for i, row in enumerate(table_data):
            if i < len(table["data"]):
                for j, cell in enumerate(row):
                    if j < len(table["data"][i]):
                        table["data"][i][j] = str(cell)
    
    data["modified"] = datetime.now().isoformat()
    save_project_file(project, data)
    click.echo(f"✅ Filled table with {len(table_data)} rows")


@writer.command("add-image")
@click.option("--project", required=True, help="Project JSON file")
@click.option("--path", required=True, help="Image file path")
@click.option("--caption", help="Image caption")
@click.option("--width", type=int, help="Width in pixels")
@click.option("--height", type=int, help="Height in pixels")
def writer_add_image(project: str, path: str, caption: Optional[str], 
                     width: Optional[int], height: Optional[int]):
    """Add an image to the document"""
    data = ensure_project_file(project)
    if data["type"] != "writer":
        raise LibreOfficeError(f"Project is type '{data['type']}', expected 'writer'")
    
    if not os.path.exists(path):
        raise LibreOfficeError(f"Image not found: {path}")
    
    image = {
        "type": "image",
        "path": os.path.abspath(path),
        "caption": caption,
        "width": width,
        "height": height,
        "timestamp": datetime.now().isoformat()
    }
    data["content"].append(image)
    data["modified"] = datetime.now().isoformat()
    save_project_file(project, data)
    click.echo(f"✅ Added image: {path}")


# =============================================================================
# Calc Commands
# =============================================================================

@cli.group()
def calc():
    """Calc spreadsheet editing commands"""
    pass


@calc.command("add-sheet")
@click.option("--project", required=True, help="Project JSON file")
@click.option("--name", default="Sheet1", help="Sheet name")
def calc_add_sheet(project: str, name: str):
    """Add a new sheet to the spreadsheet"""
    data = ensure_project_file(project)
    if data["type"] != "calc":
        raise LibreOfficeError(f"Project is type '{data['type']}', expected 'calc'")
    
    if "sheets" not in data:
        data["sheets"] = []
    
    sheet = {
        "name": name,
        "data": [],
        "timestamp": datetime.now().isoformat()
    }
    data["sheets"].append(sheet)
    data["modified"] = datetime.now().isoformat()
    save_project_file(project, data)
    click.echo(f"✅ Added sheet: {name}")


@calc.command("fill-data")
@click.option("--project", required=True, help="Project JSON file")
@click.option("--data", "data_file", required=True, help="JSON file with spreadsheet data")
@click.option("--sheet", default=0, help="Sheet index or name")
def calc_fill_data(project: str, data_file: str, sheet):
    """Fill sheet with data from JSON file"""
    data = ensure_project_file(project)
    if data["type"] != "calc":
        raise LibreOfficeError(f"Project is type '{data['type']}', expected 'calc'")
    
    # Load spreadsheet data
    with open(data_file, 'r', encoding='utf-8') as f:
        sheet_data = json.load(f)
    
    if "sheets" not in data:
        data["sheets"] = []
    
    # Find or create sheet
    if isinstance(sheet, int):
        if sheet >= len(data["sheets"]):
            data["sheets"].append({"name": f"Sheet{sheet+1}", "data": []})
        target_sheet = data["sheets"][sheet]
    else:
        existing = [s for s in data["sheets"] if s["name"] == sheet]
        if existing:
            target_sheet = existing[0]
        else:
            target_sheet = {"name": sheet, "data": []}
            data["sheets"].append(target_sheet)
    
    # Fill data
    if isinstance(sheet_data, list):
        target_sheet["data"] = sheet_data
    elif isinstance(sheet_data, dict) and "data" in sheet_data:
        target_sheet["data"] = sheet_data["data"]
    
    data["modified"] = datetime.now().isoformat()
    save_project_file(project, data)
    click.echo(f"✅ Filled sheet with data")


# =============================================================================
# Style Commands
# =============================================================================

@cli.group()
def style():
    """Style management commands"""
    pass


@style.command("heading")
@click.option("--project", required=True, help="Project JSON file")
@click.option("--font-size", type=int, help="Font size in points")
@click.option("--bold", is_flag=True, help="Bold text")
@click.option("--italic", is_flag=True, help="Italic text")
@click.option("--color", help="Color (hex: #RRGGBB)")
@click.option("--level", type=int, help="Heading level to style")
def style_heading(project: str, font_size: Optional[int], bold: bool, 
                  italic: bool, color: Optional[str], level: Optional[int]):
    """Style headings in the document"""
    data = ensure_project_file(project)
    
    if "styles" not in data:
        data["styles"] = {}
    if "heading" not in data["styles"]:
        data["styles"]["heading"] = {}
    
    style_data = data["styles"]["heading"]
    if font_size:
        style_data["font_size"] = font_size
    if bold:
        style_data["bold"] = True
    if italic:
        style_data["italic"] = True
    if color:
        style_data["color"] = color
    if level:
        style_data["level"] = level
    
    data["modified"] = datetime.now().isoformat()
    save_project_file(project, data)
    click.echo(f"✅ Updated heading style")


@style.command("table")
@click.option("--project", required=True, help="Project JSON file")
@click.option("--border", type=int, help="Border width in points")
@click.option("--header-color", help="Header row background color")
@click.option("--alternating", is_flag=True, help="Use alternating row colors")
def style_table(project: str, border: Optional[int], header_color: Optional[str], 
                alternating: bool):
    """Style tables in the document"""
    data = ensure_project_file(project)
    
    if "styles" not in data:
        data["styles"] = {}
    if "table" not in data["styles"]:
        data["styles"]["table"] = {}
    
    style_data = data["styles"]["table"]
    if border:
        style_data["border"] = border
    if header_color:
        style_data["header_color"] = header_color
    if alternating:
        style_data["alternating"] = True
    
    data["modified"] = datetime.now().isoformat()
    save_project_file(project, data)
    click.echo(f"✅ Updated table style")


# =============================================================================
# Export Commands
# =============================================================================

@cli.group()
def export():
    """Export and render commands"""
    pass


@export.command("render")
@click.argument("output")
@click.option("--project", required=True, help="Project JSON file")
@click.option("--type", "output_type", type=click.Choice(["pdf", "docx", "odt", "xlsx", "xls", "csv"]), 
              required=True, help="Output format")
@click.option("--template", help="Template file to use")
@click.option("--output-dir", default=".", help="Output directory")
def export_render(output: str, project: str, output_type: str, 
                  template: Optional[str], output_dir: str):
    """Render project to output format
    
    Examples:
        cli-anything-libreoffice --project 投资报告.json export render 投资报告.pdf --type pdf
        cli-anything-libreoffice --project 持仓表.json export render 持仓表.xlsx --type xlsx
    """
    data = ensure_project_file(project)
    
    # Create temporary ODT/ODS file from project
    temp_suffix = ".odt" if data["type"] == "writer" else ".ods"
    
    with tempfile.NamedTemporaryFile(suffix=temp_suffix, delete=False) as temp_file:
        temp_path = temp_file.name
        
        # Generate ODT/ODS content
        if data["type"] == "writer":
            generate_writer_odt(temp_path, data, template)
        elif data["type"] == "calc":
            generate_calc_ods(temp_path, data, template)
        else:
            raise LibreOfficeError(f"Unsupported project type: {data['type']}")
    
    try:
        # Convert to target format
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        run_headless_conversion(temp_path, output_type, output_dir)
        
        # Move/rename output file
        base_name = Path(output).stem
        expected_output = output_path / f"{base_name}.{output_type}"
        
        if expected_output.exists():
            click.echo(f"✅ Exported: {expected_output}")
        else:
            # Find generated file
            for f in output_path.glob(f"{base_name}.*"):
                click.echo(f"✅ Exported: {f}")
                break
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def generate_writer_odt(output_path: str, data: dict, template: Optional[str] = None):
    """Generate ODT file from project data using simple XML"""
    # For now, create a minimal ODT structure
    # In production, this would use odfpy or similar library
    
    content_xml = '<office:body><office:text>'
    
    for item in data.get("content", []):
        if item["type"] == "heading":
            level = item.get("level", 1)
            text = item.get("text", "")
            content_xml += f'<text:h text:outline-level="{level}">{text}</text:h>'
        elif item["type"] == "paragraph":
            text = item.get("text", "")
            content_xml += f'<text:p>{text}</text:p>'
        elif item["type"] == "table":
            rows = item.get("rows", 1)
            cols = item.get("cols", 1)
            table_data = item.get("data", [])
            content_xml += '<table:table><table:table-column/>' * cols
            for row_idx in range(rows):
                content_xml += '<table:table-row>'
                for col_idx in range(cols):
                    cell_value = ""
                    if row_idx < len(table_data) and col_idx < len(table_data[row_idx]):
                        cell_value = str(table_data[row_idx][col_idx])
                    content_xml += f'<table:table-cell><text:p>{cell_value}</text:p></table:table-cell>'
                content_xml += '</table:table-row>'
            content_xml += '</table:table>'
        elif item["type"] == "image":
            # Image handling would require embedding
            pass
    
    content_xml += '</office:text></office:body>'
    
    # Minimal ODT structure (zipped XML)
    # For simplicity, we'll create a text file that LibreOffice can open
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Generated Document\n\n")
        for item in data.get("content", []):
            if item["type"] == "heading":
                prefix = "#" * item.get("level", 1)
                f.write(f"{prefix} {item.get('text', '')}\n\n")
            elif item["type"] == "paragraph":
                f.write(f"{item.get('text', '')}\n\n")
            elif item["type"] == "table":
                table_data = item.get("data", [])
                for row in table_data:
                    f.write(" | ".join(str(cell) for cell in row) + "\n")
                f.write("\n")


def generate_calc_ods(output_path: str, data: dict, template: Optional[str] = None):
    """Generate ODS file from project data"""
    # Create CSV that LibreOffice can open
    with open(output_path, 'w', encoding='utf-8') as f:
        for sheet in data.get("sheets", []):
            sheet_data = sheet.get("data", [])
            for row in sheet_data:
                f.write(",".join(str(cell) for cell in row) + "\n")
            f.write("\n")


# =============================================================================
# Template Commands
# =============================================================================

@cli.group()
def template():
    """Template management commands"""
    pass


@template.command("list")
@click.option("--folder", default="templates", help="Template folder")
def template_list(folder: str):
    """List available templates"""
    if not os.path.exists(folder):
        click.echo("No templates folder found")
        return
    
    templates = []
    for f in os.listdir(folder):
        if f.endswith(('.odt', '.ots', '.otp')):
            templates.append(f)
    
    if templates:
        click.echo("Available templates:")
        for t in templates:
            click.echo(f"  - {t}")
    else:
        click.echo("No templates found")


@template.command("create")
@click.option("--type", "doc_type", type=click.Choice(["writer", "calc", "impress"]), 
              required=True, help="Template type")
@click.option("--name", required=True, help="Template name")
@click.option("--output", help="Output path (default: templates/{name}.od{t,s,p})")
def template_create(doc_type: str, name: str, output: Optional[str]):
    """Create a new template from current project"""
    suffix_map = {"writer": "odt", "calc": "ots", "impress": "otp"}
    suffix = suffix_map[doc_type]
    
    if not output:
        output = f"templates/{name}.{suffix}"
    
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create empty template
    if doc_type == "writer":
        content = "# Template\n\n## Section\n\nContent here...\n"
    elif doc_type == "calc":
        content = "Header1,Header2,Header3\nData1,Data2,Data3\n"
    else:
        content = "# Presentation Template\n\n## Slide 1\n\nContent...\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    click.echo(f"✅ Created template: {output}")


# =============================================================================
# Main CLI Entry Point
# =============================================================================

@cli.command("build")
@click.option("--project", required=True, help="Project JSON file")
@click.option("--output", required=True, help="Output file (PDF/DOCX/XLSX)")
@click.option("--template", help="Optional template")
def build(project: str, output: str, template: Optional[str]):
    """Build document from project (shortcut for export render)
    
    Examples:
        cli-anything-libreoffice build --project 投资报告.json --output 投资报告.pdf
    """
    output_type = Path(output).suffix.lower().lstrip('.')
    output_dir = str(Path(output).parent)
    
    export_render.callback(output, project, output_type, template, output_dir)


if __name__ == "__main__":
    cli()
