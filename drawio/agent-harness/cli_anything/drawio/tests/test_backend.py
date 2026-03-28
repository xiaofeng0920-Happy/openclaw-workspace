"""
Backend Unit Tests for Draw.io CLI

Tests the core DrawioBackend class functionality.
"""

import pytest
import os
import json
import tempfile
from pathlib import Path

from ..utils.drawio_backend import DrawioBackend


class TestDrawioBackend:
    """Test suite for DrawioBackend class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.backend = DrawioBackend()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_new(self):
        """Test creating a new diagram structure"""
        root = self.backend.create_new('test-diagram')
        
        assert root is not None
        assert root.tag == 'mxfile'
        assert root.get('host') == 'cli-anything-drawio'
        
        # Check diagram element
        diagram = self.backend.diagram
        assert diagram is not None
        assert diagram.get('name') == 'test-diagram'
        
        # Check model structure
        model = diagram.find('mxGraphModel')
        assert model is not None
        
        # Check root element
        model_root = model.find('root')
        assert model_root is not None
    
    def test_add_shape(self):
        """Test adding a shape to diagram"""
        self.backend.create_new()
        
        shape_id = self.backend.add_shape(
            label='Test Shape',
            shape_type='rectangle',
            x=100,
            y=100,
            width=120,
            height=60
        )
        
        assert shape_id == 'shape-1'
        assert self.backend.shape_counter == 1
    
    def test_add_shape_custom_style(self):
        """Test adding a shape with custom style"""
        self.backend.create_new()
        
        style = {'fillColor': '#FF0000', 'strokeColor': '#000000'}
        shape_id = self.backend.add_shape(
            label='Red Shape',
            shape_type='rectangle',
            x=200,
            y=200,
            style=style
        )
        
        assert shape_id == 'shape-1'
    
    def test_add_connector(self):
        """Test adding a connector between shapes"""
        self.backend.create_new()
        
        # Add two shapes
        shape1 = self.backend.add_shape('Shape 1', 'rectangle', x=100, y=100)
        shape2 = self.backend.add_shape('Shape 2', 'rectangle', x=300, y=100)
        
        # Add connector
        connector_id = self.backend.add_connector(
            from_shape=shape1,
            to_shape=shape2,
            label='Connects'
        )
        
        assert connector_id == 'connector-3'
    
    def test_add_connector_no_diagram(self):
        """Test adding connector without diagram raises error"""
        with pytest.raises(ValueError, match="No diagram created"):
            self.backend.add_connector('shape1', 'shape2')
    
    def test_add_text(self):
        """Test adding text element"""
        self.backend.create_new()
        
        text_id = self.backend.add_text(
            text='Title Text',
            x=150,
            y=50,
            font_size=24,
            bold=True
        )
        
        assert text_id == 'shape-1'
    
    def test_save_file(self):
        """Test saving diagram to file"""
        self.backend.create_new()
        self.backend.add_shape('Test', 'rectangle', x=100, y=100)
        
        filepath = os.path.join(self.temp_dir, 'test.drawio')
        saved_path = self.backend.save(filepath)
        
        assert os.path.exists(saved_path)
        assert saved_path.endswith('.drawio')
        
        # Verify file is valid XML
        import xml.etree.ElementTree as ET
        tree = ET.parse(saved_path)
        root = tree.getroot()
        assert root.tag == 'mxfile'
    
    def test_save_auto_extension(self):
        """Test that .drawio extension is added automatically"""
        self.backend.create_new()
        
        filepath = os.path.join(self.temp_dir, 'test_no_ext')
        saved_path = self.backend.save(filepath)
        
        assert saved_path.endswith('.drawio')
    
    def test_load_file(self):
        """Test loading existing diagram"""
        # Create and save
        self.backend.create_new()
        self.backend.add_shape('Original', 'rectangle')
        filepath = os.path.join(self.temp_dir, 'load_test.drawio')
        self.backend.save(filepath)
        
        # Load in new backend
        new_backend = DrawioBackend()
        success = new_backend.load(filepath)
        
        assert success is True
        assert new_backend.current_file == filepath
        assert new_backend.shape_counter >= 1
    
    def test_load_nonexistent_file(self):
        """Test loading nonexistent file returns False"""
        success = self.backend.load('/nonexistent/path/file.drawio')
        assert success is False
    
    def test_export_png_info(self):
        """Test PNG export info creation"""
        self.backend.create_new()
        filepath = os.path.join(self.temp_dir, 'export_test.drawio')
        self.backend.save(filepath)
        
        png_path = os.path.join(self.temp_dir, 'output.png')
        info_path = self.backend.export_png(png_path, dpi=300)
        
        assert os.path.exists(info_path)
        assert info_path.endswith('.export.json')
        
        # Verify info content
        with open(info_path, 'r') as f:
            info = json.load(f)
        
        assert info['format'] == 'png'
        assert info['dpi'] == 300
        assert 'draw.io' in info['note']
    
    def test_export_svg_info(self):
        """Test SVG export info creation"""
        self.backend.create_new()
        filepath = os.path.join(self.temp_dir, 'export_test.drawio')
        self.backend.save(filepath)
        
        svg_path = os.path.join(self.temp_dir, 'output.svg')
        info_path = self.backend.export_svg(svg_path)
        
        assert os.path.exists(info_path)
        assert info_path.endswith('.export.json')
    
    def test_export_pdf_info(self):
        """Test PDF export info creation"""
        self.backend.create_new()
        filepath = os.path.join(self.temp_dir, 'export_test.drawio')
        self.backend.save(filepath)
        
        pdf_path = os.path.join(self.temp_dir, 'output.pdf')
        info_path = self.backend.export_pdf(pdf_path)
        
        assert os.path.exists(info_path)
        assert info_path.endswith('.export.json')
    
    def test_export_no_diagram(self):
        """Test export without diagram raises error"""
        with pytest.raises(ValueError, match="No diagram loaded"):
            self.backend.export_png('test.png')
    
    def test_to_dict(self):
        """Test converting diagram to dictionary"""
        self.backend.create_new('test-type')
        self.backend.add_shape('Test', 'rectangle')
        
        result = self.backend.to_dict()
        
        assert isinstance(result, dict)
        assert result['diagram_type'] == 'test-type'
        assert result['shape_count'] == 1
    
    def test_to_dict_empty(self):
        """Test to_dict with no diagram"""
        result = self.backend.to_dict()
        assert result == {}
    
    def test_shape_types(self):
        """Test various shape types"""
        self.backend.create_new()
        
        shape_types = ['rectangle', 'ellipse', 'rhombus', 'triangle', 
                       'cylinder', 'document', 'folder', 'cloud', 'actor']
        
        for i, shape_type in enumerate(shape_types):
            shape_id = self.backend.add_shape(
                f'{shape_type} shape',
                shape_type,
                x=100 + (i * 150),
                y=100
            )
            assert shape_id is not None
    
    def test_template_asset_allocation(self):
        """Test asset allocation template"""
        data = {'美股': '60%', '港股': '23%', '现金': '17%'}
        self.backend.create_template('asset-allocation', data)
        
        assert self.backend.shape_counter > 0
    
    def test_template_price_chart(self):
        """Test price chart template"""
        data = {'prices': [100, 105, 102, 108, 110, 115, 112, 120]}
        self.backend.create_template('price-chart', data)
        
        assert self.backend.shape_counter > 0
    
    def test_template_investment_flow(self):
        """Test investment flow template"""
        self.backend.create_template('investment-flow')
        
        # Should have main flow + secondary flow shapes
        assert self.backend.shape_counter >= 10
    
    def test_template_org_chart(self):
        """Test organization chart template"""
        self.backend.create_template('org')
        
        assert self.backend.shape_counter >= 5
    
    def test_template_mindmap(self):
        """Test mindmap template"""
        self.backend.create_template('mindmap')
        
        # Central topic + 4 branches
        assert self.backend.shape_counter >= 5
        assert self.backend.shape_counter <= 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
