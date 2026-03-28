#!/usr/bin/env python3
"""
Automated test suite for CLI-Anything GIMP

Run with: pytest tests/test_gimp_cli.py -v
Or: python -m pytest tests/test_gimp_cli.py -v
"""

import os
import sys
import subprocess
import shutil
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from click.testing import CliRunner
from cli_anything_gimp.cli import cli


class TestCLIInstallation:
    """Test CLI installation and basic commands"""
    
    def test_cli_help(self):
        """Test main help command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'CLI-Anything GIMP' in result.output
        assert 'batch' in result.output
        assert 'project' in result.output
        assert 'export' in result.output
    
    def test_batch_help(self):
        """Test batch command help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['batch', '--help'])
        assert result.exit_code == 0
        assert 'resize' in result.output
        assert 'watermark' in result.output
        assert 'convert' in result.output
    
    def test_project_help(self):
        """Test project command help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['project', '--help'])
        assert result.exit_code == 0
        assert 'text' in result.output
        assert 'arrow' in result.output
        assert 'highlight' in result.output
    
    def test_export_help(self):
        """Test export command help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['export', '--help'])
        assert result.exit_code == 0
        assert 'render' in result.output
        assert 'all' in result.output


class TestBatchCommands:
    """Test batch processing commands"""
    
    @pytest.fixture
    def test_dirs(self, tmp_path):
        """Create test directories"""
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        return input_dir, output_dir
    
    def test_batch_resize_requires_input_dir(self):
        """Test batch resize requires input directory"""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'batch', 'resize',
            '--output-dir', '/tmp/test',
            '--width', '800',
            '--height', '600'
        ])
        assert result.exit_code != 0
        assert 'input-dir' in result.output or 'Missing option' in result.output
    
    def test_batch_resize_requires_output_dir(self):
        """Test batch resize requires output directory"""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'batch', 'resize',
            '--input-dir', '/tmp/test',
            '--width', '800',
            '--height', '600'
        ])
        assert result.exit_code != 0
    
    def test_batch_watermark_requires_text(self):
        """Test batch watermark requires text"""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'batch', 'watermark',
            '--input-dir', '/tmp/test',
            '--output-dir', '/tmp/test'
        ])
        assert result.exit_code != 0
        assert 'text' in result.output or 'Missing option' in result.output
    
    def test_batch_convert_requires_format(self):
        """Test batch convert requires format"""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'batch', 'convert',
            '--input-dir', '/tmp/test',
            '--output-dir', '/tmp/test'
        ])
        assert result.exit_code != 0
        assert 'format' in result.output or 'Missing option' in result.output


class TestProjectCommands:
    """Test project-level commands"""
    
    def test_project_requires_project_flag(self):
        """Test project commands require --project flag"""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'project', 'text', 'add',
            '--text', 'Test',
            '--x', '100',
            '--y', '100'
        ])
        assert result.exit_code != 0
        assert '--project' in result.output or 'required' in result.output.lower()
    
    def test_export_requires_project_flag(self):
        """Test export commands require --project flag"""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'export', 'render',
            'output.png'
        ])
        assert result.exit_code != 0
        assert '--project' in result.output or 'required' in result.output.lower()


class TestScriptFuGeneration:
    """Test Script-Fu code generation"""
    
    def test_resize_script_generation(self):
        """Test resize script is generated correctly"""
        from cli_anything_gimp.batch_commands import generate_resize_script
        
        script = generate_resize_script('/input/test.png', '/output/test.png', 800, 600)
        assert 'resize-image' in script
        assert '/input/test.png' in script
        assert 'gimp-image-scale' in script
        assert '800' in script
        assert '600' in script
    
    def test_watermark_script_generation(self):
        """Test watermark script is generated correctly"""
        from cli_anything_gimp.batch_commands import generate_watermark_script
        
        script = generate_watermark_script(
            '/input', '/output', 'Test', 'bottom-right', 24, '#ffffff', 0.7
        )
        assert 'batch-watermark' in script
        assert 'Test' in script
        assert 'bottom-right' in script
        assert 'gimp-text-fontname' in script
    
    def test_convert_script_generation(self):
        """Test convert script is generated correctly"""
        from cli_anything_gimp.batch_commands import generate_convert_script
        
        script = generate_convert_script('/input', '/output', 'png', 95)
        assert 'batch-convert' in script
        assert 'file-png-save' in script


class TestIntegration:
    """Integration tests with actual GIMP"""
    
    @pytest.fixture
    def test_env(self, tmp_path):
        """Create test environment with sample image"""
        test_dir = tmp_path / "integration_test"
        test_dir.mkdir()
        
        # Create a simple test image using ImageMagick if available
        input_file = test_dir / "test_input.png"
        try:
            subprocess.run([
                'convert', '-size', '200x200', 'xc:blue',
                str(input_file)
            ], check=True, capture_output=True)
            has_imagemagick = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            has_imagemagick = False
        
        return {
            'dir': test_dir,
            'input_file': input_file,
            'has_imagemagick': has_imagemagick
        }
    
    @pytest.mark.skip(reason="Requires GIMP and sample images")
    def test_batch_resize_integration(self, test_env):
        """Test batch resize with actual GIMP"""
        if not test_env['has_imagemagick']:
            pytest.skip("ImageMagick not available")
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'batch', 'resize',
            '--input-dir', str(test_env['dir']),
            '--output-dir', str(test_env['dir'] / 'output'),
            '--width', '100',
            '--height', '100',
            '--verbose'
        ])
        
        # Should complete without error
        assert result.exit_code == 0
    
    @pytest.mark.skip(reason="Requires GIMP and sample images")
    def test_image_open_integration(self, test_env):
        """Test image open with actual GIMP"""
        if not test_env['has_imagemagick']:
            pytest.skip("ImageMagick not available")
        
        runner = CliRunner()
        xcf_file = test_env['dir'] / "test.xcf"
        result = runner.invoke(cli, [
            'image', 'open',
            str(test_env['input_file']),
            '-o', str(xcf_file),
            '--verbose'
        ])
        
        assert result.exit_code == 0
        assert xcf_file.exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
