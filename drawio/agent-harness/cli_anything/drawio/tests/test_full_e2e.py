"""
End-to-End Tests for Draw.io CLI

Tests complete workflows from creation to export.
"""

import pytest
import os
import json
import tempfile
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from click.testing import CliRunner

from ..drawio_cli import cli
from ..utils.drawio_backend import DrawioBackend


class TestFullWorkflows:
    """End-to-end workflow tests"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test files"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_and_export_workflow(self):
        """Test complete workflow: create → add elements → export"""
        # Step 1: Create new diagram
        project_file = os.path.join(self.temp_dir, 'workflow_test.drawio')
        result = self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        assert result.exit_code == 0
        assert os.path.exists(project_file)
        
        # Step 2: Add shapes
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'shape', 'add', '--label', 'Start', '--x', '100', '--y', '100'
        ])
        assert result.exit_code == 0
        
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'shape', 'add', '--label', 'End', '--x', '300', '--y', '100'
        ])
        assert result.exit_code == 0
        
        # Step 3: Add connector
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'connector', 'add',
            '--from', 'shape-1',
            '--to', 'shape-2'
        ])
        assert result.exit_code == 0
        
        # Step 4: Add text
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'text', 'add', '-t', 'Workflow Title', '--font-size', '18', '--bold'
        ])
        assert result.exit_code == 0
        
        # Step 5: Export
        png_output = os.path.join(self.temp_dir, 'workflow.png')
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'export', 'render', png_output,
            '--format', 'png'
        ])
        assert result.exit_code == 0
        
        # Verify export info created
        info_file = png_output.replace('.png', '.export.json')
        assert os.path.exists(info_file)
    
    def test_template_with_data_workflow(self):
        """Test template workflow with external data"""
        from click.testing import CliRunner
        from ..drawio_cli import cli as fresh_cli
        
        runner = CliRunner()
        # Create data file
        data_file = os.path.join(self.temp_dir, 'portfolio.json')
        portfolio_data = {
            '美股': '55%',
            '港股': '25%',
            '债券': '10%',
            '现金': '10%'
        }
        with open(data_file, 'w') as f:
            json.dump(portfolio_data, f)
        
        # Create diagram from template with data
        output_file = os.path.join(self.temp_dir, 'portfolio_chart.drawio')
        result = runner.invoke(fresh_cli, [
            '--template', 'asset-allocation',
            '--data', data_file,
            'diagram', 'new',
            '-o', output_file
        ])
        assert result.exit_code == 0
        assert os.path.exists(output_file)
        
        # Verify file is valid XML
        tree = ET.parse(output_file)
        root = tree.getroot()
        assert root.tag == 'mxfile'
        
        # Export
        svg_output = os.path.join(self.temp_dir, 'portfolio.svg')
        result = self.runner.invoke(cli, [
            '--project', output_file,
            'export', 'render', svg_output,
            '--format', 'svg'
        ])
        assert result.exit_code == 0
    
    def test_investment_analysis_workflow(self):
        """Test complete investment analysis workflow"""
        from click.testing import CliRunner
        from ..drawio_cli import cli as fresh_cli
        
        runner = CliRunner()
        # Create investment flow diagram
        flow_file = os.path.join(self.temp_dir, 'investment_flow.drawio')
        result = runner.invoke(fresh_cli, [
            '--template', 'investment-flow',
            'diagram', 'new',
            '-o', flow_file
        ])
        assert result.exit_code == 0
        
        # Add custom analysis step
        result = runner.invoke(fresh_cli, [
            '--project', flow_file,
            'shape', 'add',
            '--type', 'decision',
            '--label', '止损检查',
            '--x', '500', '--y', '400'
        ])
        assert result.exit_code == 0
        
        # Create asset allocation
        alloc_file = os.path.join(self.temp_dir, 'allocation.drawio')
        result = runner.invoke(fresh_cli, [
            '--template', 'asset-allocation',
            'diagram', 'new',
            '-o', alloc_file
        ])
        assert result.exit_code == 0
        
        # Create price chart
        price_data = os.path.join(self.temp_dir, 'prices.json')
        with open(price_data, 'w') as f:
            json.dump({'prices': [100, 105, 110, 108, 115, 120]}, f)
        
        chart_file = os.path.join(self.temp_dir, 'price_chart.drawio')
        result = runner.invoke(fresh_cli, [
            '--template', 'price-chart',
            '--data', price_data,
            'diagram', 'new',
            '-o', chart_file
        ])
        assert result.exit_code == 0
        
        # All files should exist
        assert os.path.exists(flow_file)
        assert os.path.exists(alloc_file)
        assert os.path.exists(chart_file)
    
    def test_json_output_workflow(self):
        """Test JSON output mode throughout workflow"""
        # Create with JSON output
        project_file = os.path.join(self.temp_dir, 'json_test.drawio')
        result = self.runner.invoke(cli, [
            '--json',
            'diagram', 'new', '-o', project_file
        ])
        assert result.exit_code == 0
        
        # Parse JSON output
        output_data = json.loads(result.output)
        assert output_data['status'] == 'success'
        assert 'file' in output_data
        
        # Add shape with JSON output
        result = self.runner.invoke(cli, [
            '--json',
            '--project', project_file,
            'shape', 'add', '--label', 'Test', '--x', '100', '--y', '100'
        ])
        assert result.exit_code == 0
        
        output_data = json.loads(result.output)
        assert output_data['status'] == 'success'
        assert 'shape_id' in output_data
    
    def test_multiple_shapes_and_connectors(self):
        """Test creating complex diagram with many elements"""
        project_file = os.path.join(self.temp_dir, 'complex.drawio')
        
        # Create new
        result = self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        assert result.exit_code == 0
        
        # Add multiple shapes in a chain
        for i in range(5):
            result = self.runner.invoke(cli, [
                '--project', project_file,
                'shape', 'add',
                '--label', f'Step {i+1}',
                '--x', str(100 + i * 150),
                '--y', '200'
            ])
            assert result.exit_code == 0
        
        # Add connectors between steps
        for i in range(4):
            result = self.runner.invoke(cli, [
                '--project', project_file,
                'connector', 'add',
                '--from', f'shape-{i+1}',
                '--to', f'shape-{i+2}'
            ])
            assert result.exit_code == 0
        
        # Verify file can be loaded
        backend = DrawioBackend()
        success = backend.load(project_file)
        assert success is True
        assert backend.shape_counter >= 9  # 5 shapes + 4 connectors
    
    def test_file_persistence(self):
        """Test that files persist correctly across sessions"""
        project_file = os.path.join(self.temp_dir, 'persist_test.drawio')
        
        # Session 1: Create and add elements
        result = self.runner.invoke(cli, ['diagram', 'new', '-o', project_file])
        assert result.exit_code == 0
        
        result = self.runner.invoke(cli, [
            '--project', project_file,
            'shape', 'add', '--label', 'Persistent Shape', '--x', '100', '--y', '100'
        ])
        assert result.exit_code == 0
        
        # Verify file exists
        assert os.path.exists(project_file)
        original_size = os.path.getsize(project_file)
        
        # Session 2: Load and add more (simulated by new runner)
        runner2 = CliRunner()
        result = runner2.invoke(cli, [
            '--project', project_file,
            'shape', 'add', '--label', 'Second Shape', '--x', '300', '--y', '100'
        ])
        assert result.exit_code == 0
        
        # File should be larger
        new_size = os.path.getsize(project_file)
        assert new_size > original_size
        
        # Verify both shapes exist
        backend = DrawioBackend()
        backend.load(project_file)
        assert backend.shape_counter >= 2
    
    def test_error_handling_no_project(self):
        """Test error handling when no project specified"""
        from click.testing import CliRunner
        from ..drawio_cli import cli as fresh_cli
        
        runner = CliRunner()
        # Try to add shape without project
        result = runner.invoke(fresh_cli, [
            'shape', 'add', '--label', 'Orphan Shape'
        ])
        
        # Should fail gracefully
        assert result.exit_code != 0
        assert 'error' in result.output.lower()
    
    def test_error_handling_invalid_file(self):
        """Test error handling with invalid file path"""
        result = self.runner.invoke(cli, [
            '--project', '/nonexistent/path/file.drawio',
            'shape', 'add', '--label', 'Test'
        ])
        
        # Should handle gracefully
        assert 'error' in result.output.lower() or result.exit_code != 0
    
    def test_cli_help_all_commands(self):
        """Test that all commands have help"""
        commands = [
            ['--help'],
            ['diagram', '--help'],
            ['diagram', 'new', '--help'],
            ['shape', '--help'],
            ['shape', 'add', '--help'],
            ['connector', '--help'],
            ['connector', 'add', '--help'],
            ['text', '--help'],
            ['text', 'add', '--help'],
            ['export', '--help'],
            ['export', 'render', '--help'],
            ['info', '--help'],
            ['list-templates', '--help'],
        ]
        
        for cmd in commands:
            result = self.runner.invoke(cli, cmd)
            assert result.exit_code == 0, f"Help failed for: {cmd}"


class TestInstalledCli:
    """Tests for installed CLI (if available)"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test files"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.skip(reason="Requires installed CLI")
    def test_installed_cli_help(self):
        """Test installed CLI help command"""
        result = subprocess.run(
            ['cli-anything-drawio', '--help'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'Draw.io CLI' in result.stdout
    
    @pytest.mark.skip(reason="Requires installed CLI")
    def test_installed_cli_create(self):
        """Test installed CLI diagram creation"""
        output_file = os.path.join(self.temp_dir, 'installed_test.drawio')
        result = subprocess.run(
            ['cli-anything-drawio', 'diagram', 'new', '-o', output_file],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert os.path.exists(output_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
