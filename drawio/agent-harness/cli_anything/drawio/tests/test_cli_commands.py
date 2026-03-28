"""
CLI Command Tests for Draw.io CLI

Tests the Click-based CLI commands.
"""

import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner

from ..drawio_cli import cli


class TestCliCommands:
    """Test suite for CLI commands"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test files"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_help_command(self):
        """Test main help command"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Draw.io CLI' in result.output
        assert 'diagram' in result.output
        assert 'shape' in result.output
    
    def test_diagram_new(self):
        """Test creating new diagram"""
        output_file = os.path.join(self.temp_dir, 'test_new.drawio')
        result = self.runner.invoke(cli, ['diagram', 'new', '-o', output_file])
        
        assert result.exit_code == 0
        assert 'success' in result.output.lower() or 'created' in result.output.lower()
        assert os.path.exists(output_file)
    
    def test_diagram_new_with_type(self):
        """Test creating new diagram with type"""
        output_file = os.path.join(self.temp_dir, 'test_flowchart.drawio')
        result = self.runner.invoke(cli, [
            'diagram', 'new', 
            '-o', output_file,
            '--type', 'flowchart'
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(output_file)
    
    def test_diagram_new_json_output(self):
        """Test creating diagram with JSON output"""
        output_file = os.path.join(self.temp_dir, 'test_json.drawio')
        result = self.runner.invoke(cli, [
            '--json',
            'diagram', 'new', 
            '-o', output_file
        ])
        
        assert result.exit_code == 0
        # Should be valid JSON
        try:
            data = json.loads(result.output)
            assert 'status' in data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
    
    def test_shape_add(self):
        """Test adding a shape"""
        # First create a diagram
        project_file = os.path.join(self.temp_dir, 'test_shape.drawio')
        self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        
        # Add shape
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'shape', 'add',
            '--type', 'rectangle',
            '--label', 'Test Shape',
            '--x', '100',
            '--y', '100'
        ])
        
        assert result.exit_code == 0
        assert 'success' in result.output.lower()
    
    def test_shape_add_no_project(self):
        """Test adding shape without project fails"""
        # Create fresh runner to avoid state from previous tests
        from click.testing import CliRunner
        from ..drawio_cli import cli as fresh_cli
        
        runner = CliRunner()
        result = runner.invoke(fresh_cli, [
            'shape', 'add',
            '--type', 'rectangle',
            '--label', 'Test'
        ])
        
        # Should fail without project
        assert result.exit_code != 0
        assert 'error' in result.output.lower()
    
    def test_shape_add_with_style(self):
        """Test adding shape with custom style"""
        project_file = os.path.join(self.temp_dir, 'test_style.drawio')
        self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        
        style_json = '{"fillColor": "#FF0000", "strokeColor": "#000000"}'
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'shape', 'add',
            '--type', 'rectangle',
            '--label', 'Red Shape',
            '--style', style_json
        ])
        
        assert result.exit_code == 0
    
    def test_shape_add_invalid_style(self):
        """Test adding shape with invalid style JSON"""
        project_file = os.path.join(self.temp_dir, 'test_invalid.drawio')
        self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'shape', 'add',
            '--type', 'rectangle',
            '--label', 'Test',
            '--style', 'not-valid-json'
        ])
        
        assert result.exit_code != 0
        assert 'error' in result.output.lower()
    
    def test_connector_add(self):
        """Test adding a connector"""
        project_file = os.path.join(self.temp_dir, 'test_connector.drawio')
        self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        
        # Add two shapes first
        self.runner.invoke(cli, [
            '--project', project_file,
            'shape', 'add', '--label', 'Shape 1', '--x', '100', '--y', '100'
        ])
        self.runner.invoke(cli, [
            '--project', project_file,
            'shape', 'add', '--label', 'Shape 2', '--x', '300', '--y', '100'
        ])
        
        # Add connector
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'connector', 'add',
            '--from', 'shape-1',
            '--to', 'shape-2',
            '--label', 'Connects'
        ])
        
        assert result.exit_code == 0
        assert 'success' in result.output.lower()
    
    def test_text_add(self):
        """Test adding text"""
        project_file = os.path.join(self.temp_dir, 'test_text.drawio')
        self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'text', 'add',
            '-t', 'Title Text',
            '--font-size', '24',
            '--bold'
        ])
        
        assert result.exit_code == 0
        assert 'success' in result.output.lower()
    
    def test_text_add_no_bold(self):
        """Test adding text without bold"""
        project_file = os.path.join(self.temp_dir, 'test_text2.drawio')
        self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'text', 'add',
            '-t', 'Normal Text',
            '--font-size', '12'
        ])
        
        assert result.exit_code == 0
    
    def test_export_render_png(self):
        """Test exporting to PNG"""
        project_file = os.path.join(self.temp_dir, 'test_export.drawio')
        self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        
        output_file = os.path.join(self.temp_dir, 'output.png')
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'export', 'render', output_file,
            '--format', 'png',
            '--dpi', '300'
        ])
        
        assert result.exit_code == 0
        # Export info file should be created
        info_file = output_file.replace('.png', '.export.json')
        assert os.path.exists(info_file)
    
    def test_export_render_svg(self):
        """Test exporting to SVG"""
        project_file = os.path.join(self.temp_dir, 'test_export_svg.drawio')
        self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        
        output_file = os.path.join(self.temp_dir, 'output.svg')
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'export', 'render', output_file,
            '--format', 'svg'
        ])
        
        assert result.exit_code == 0
        info_file = output_file.replace('.svg', '.export.json')
        assert os.path.exists(info_file)
    
    def test_export_render_pdf(self):
        """Test exporting to PDF"""
        project_file = os.path.join(self.temp_dir, 'test_export_pdf.drawio')
        self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        
        output_file = os.path.join(self.temp_dir, 'output.pdf')
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'export', 'render', output_file,
            '--format', 'pdf'
        ])
        
        assert result.exit_code == 0
        info_file = output_file.replace('.pdf', '.export.json')
        assert os.path.exists(info_file)
    
    def test_export_no_project(self):
        """Test export without project fails"""
        from click.testing import CliRunner
        from ..drawio_cli import cli as fresh_cli
        
        runner = CliRunner()
        result = runner.invoke(fresh_cli, [
            'export', 'render', 'output.png',
            '--format', 'png'
        ])
        
        assert result.exit_code != 0
        assert 'error' in result.output.lower()
    
    def test_info_command(self):
        """Test info command"""
        project_file = os.path.join(self.temp_dir, 'test_info.drawio')
        self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'info'
        ])
        
        assert result.exit_code == 0
    
    def test_info_no_diagram(self):
        """Test info without loaded diagram"""
        from click.testing import CliRunner
        from ..drawio_cli import cli as fresh_cli
        
        runner = CliRunner()
        result = runner.invoke(fresh_cli, ['info'])
        
        assert result.exit_code != 0
        assert 'error' in result.output.lower()
    
    def test_list_templates(self):
        """Test listing templates"""
        result = self.runner.invoke(cli, ['list-templates'])
        
        assert result.exit_code == 0
        assert 'asset-allocation' in result.output
        assert 'price-chart' in result.output
        assert 'investment-flow' in result.output
    
    def test_template_asset_allocation(self):
        """Test creating asset allocation template"""
        from click.testing import CliRunner
        from ..drawio_cli import cli as fresh_cli
        
        runner = CliRunner()
        output_file = os.path.join(self.temp_dir, 'asset_alloc.drawio')
        result = runner.invoke(fresh_cli, [
            '--template', 'asset-allocation',
            'diagram', 'new',
            '-o', output_file
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(output_file)
    
    def test_template_with_data_file(self):
        """Test template with data file"""
        from click.testing import CliRunner
        from ..drawio_cli import cli as fresh_cli
        
        runner = CliRunner()
        # Create data file
        data_file = os.path.join(self.temp_dir, 'data.json')
        with open(data_file, 'w') as f:
            json.dump({'美股': '60%', '港股': '23%'}, f)
        
        output_file = os.path.join(self.temp_dir, 'with_data.drawio')
        result = runner.invoke(fresh_cli, [
            '--template', 'asset-allocation',
            '--data', data_file,
            'diagram', 'new',
            '-o', output_file
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(output_file)
    
    def test_template_invalid_data_file(self):
        """Test template with invalid data file"""
        output_file = os.path.join(self.temp_dir, 'invalid_data.drawio')
        result = self.runner.invoke(cli, [
            '--template', 'asset-allocation',
            '--data', '/nonexistent/file.json',
            '-o', output_file
        ])
        
        # Should fail because data file doesn't exist
        assert result.exit_code != 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
