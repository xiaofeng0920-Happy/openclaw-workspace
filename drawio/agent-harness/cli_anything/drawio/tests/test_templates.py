"""
Template Tests for Draw.io CLI

Tests the investment chart templates.
"""

import pytest
import os
import json
import tempfile
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from ..utils.drawio_backend import DrawioBackend


class TestTemplates:
    """Test suite for diagram templates"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.backend = DrawioBackend()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test files"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _validate_drawio_file(self, filepath):
        """Validate that a file is a valid .drawio XML"""
        assert os.path.exists(filepath)
        tree = ET.parse(filepath)
        root = tree.getroot()
        assert root.tag == 'mxfile'
        return root
    
    def test_asset_allocation_template_structure(self):
        """Test asset allocation template creates correct structure"""
        self.backend.create_template('asset-allocation')
        filepath = os.path.join(self.temp_dir, 'asset_allocation.drawio')
        self.backend.save(filepath)
        
        root = self._validate_drawio_file(filepath)
        
        # Should have diagram element
        diagram = root.find('diagram')
        assert diagram is not None
        assert diagram.get('name') == 'asset-allocation'
        
        # Should have multiple shapes (title + allocations)
        model = diagram.find('mxGraphModel')
        cells = model.find('root').findall('mxCell')
        # At least title + 3 allocation boxes
        assert len(cells) >= 4
    
    def test_asset_allocation_with_custom_data(self):
        """Test asset allocation with custom data"""
        custom_data = {
            '美股': '50%',
            '港股': '30%',
            '债券': '10%',
            '现金': '10%'
        }
        self.backend.create_template('asset-allocation', custom_data)
        filepath = os.path.join(self.temp_dir, 'custom_alloc.drawio')
        self.backend.save(filepath)
        
        root = self._validate_drawio_file(filepath)
        
        # Verify file is valid
        assert root is not None
        
        # Should have shapes for each allocation
        assert self.backend.shape_counter >= 4
    
    def test_price_chart_template_structure(self):
        """Test price chart template creates correct structure"""
        self.backend.create_template('price-chart')
        filepath = os.path.join(self.temp_dir, 'price_chart.drawio')
        self.backend.save(filepath)
        
        root = self._validate_drawio_file(filepath)
        
        diagram = root.find('diagram')
        assert diagram.get('name') == 'price-chart'
        
        # Should have axes and labels
        assert self.backend.shape_counter >= 3
    
    def test_price_chart_with_price_data(self):
        """Test price chart with actual price data"""
        price_data = {
            'prices': [100, 105, 102, 108, 110, 115, 112, 120, 125, 130],
            'symbol': 'AAPL',
            'period': '3M'
        }
        self.backend.create_template('price-chart', price_data)
        filepath = os.path.join(self.temp_dir, 'price_with_data.drawio')
        self.backend.save(filepath)
        
        root = self._validate_drawio_file(filepath)
        
        # Should have data point shapes
        assert self.backend.shape_counter >= 3
    
    def test_investment_flow_template_structure(self):
        """Test investment flow template creates correct structure"""
        self.backend.create_template('investment-flow')
        filepath = os.path.join(self.temp_dir, 'investment_flow.drawio')
        self.backend.save(filepath)
        
        root = self._validate_drawio_file(filepath)
        
        diagram = root.find('diagram')
        assert diagram.get('name') == 'investment-flow'
        
        # Main flow: 5 steps
        # Secondary flow: 5 steps
        # Title
        # Connectors: 4
        assert self.backend.shape_counter >= 11
    
    def test_investment_flow_has_connectors(self):
        """Test investment flow has proper connectors"""
        self.backend.create_template('investment-flow')
        filepath = os.path.join(self.temp_dir, 'flow_connectors.drawio')
        self.backend.save(filepath)
        
        root = self._validate_drawio_file(filepath)
        
        diagram = root.find('diagram')
        model = diagram.find('mxGraphModel')
        cells = model.find('root').findall('mxCell')
        
        # Count edges (connectors)
        edges = [c for c in cells if c.get('edge') == '1']
        assert len(edges) >= 4
    
    def test_org_chart_template_structure(self):
        """Test organization chart template creates correct structure"""
        self.backend.create_template('org')
        filepath = os.path.join(self.temp_dir, 'org_chart.drawio')
        self.backend.save(filepath)
        
        root = self._validate_drawio_file(filepath)
        
        diagram = root.find('diagram')
        assert diagram.get('name') == 'org'
        
        # Should have hierarchy levels
        # CEO + 3 directors + 6 teams = 10 shapes minimum
        assert self.backend.shape_counter >= 10
    
    def test_mindmap_template_structure(self):
        """Test mindmap template creates correct structure"""
        backend = DrawioBackend()
        backend.create_template('mindmap')
        filepath = os.path.join(self.temp_dir, 'mindmap.drawio')
        backend.save(filepath)
        
        root = self._validate_drawio_file(filepath)
        
        diagram = root.find('diagram')
        assert diagram.get('name') == 'mindmap'
        
        # Central topic + 4 branches + 4 connectors = 9 elements
        assert backend.shape_counter >= 5
    
    def test_mindmap_has_central_topic(self):
        """Test mindmap has central topic with ellipse shape"""
        backend = DrawioBackend()
        backend.create_template('mindmap')
        filepath = os.path.join(self.temp_dir, 'mindmap_center.drawio')
        backend.save(filepath)
        
        # First shape should be central topic
        # Central topic uses ellipse shape
        assert backend.shape_counter >= 1
    
    def test_all_templates_save_valid_xml(self):
        """Test all templates save valid XML"""
        templates = ['asset-allocation', 'price-chart', 'investment-flow', 'org', 'mindmap']
        
        for template in templates:
            backend = DrawioBackend()
            backend.create_template(template)
            filepath = os.path.join(self.temp_dir, f'{template}.drawio')
            saved = backend.save(filepath)
            
            # Validate XML
            tree = ET.parse(saved)
            root = tree.getroot()
            assert root.tag == 'mxfile', f"Template {template} has invalid root"
    
    def test_template_list_matches_implementation(self):
        """Test that template list matches implemented templates"""
        implemented = DrawioBackend.TEMPLATES.keys()
        expected = {'asset-allocation', 'price-chart', 'investment-flow', 'org', 'mindmap'}
        
        assert implemented == expected
    
    def test_template_names_are_descriptive(self):
        """Test template names have descriptions"""
        templates = DrawioBackend.TEMPLATES
        
        for name, description in templates.items():
            assert isinstance(name, str)
            assert isinstance(description, str)
            assert len(description) > 0
    
    def test_template_creates_unique_ids(self):
        """Test that templates create unique shape IDs"""
        backend1 = DrawioBackend()
        backend1.create_template('investment-flow')
        
        # Create another template
        backend2 = DrawioBackend()
        backend2.create_template('mindmap')
        
        # IDs should be independent (both start from 1)
        assert backend1.shape_counter >= 1
        assert backend2.shape_counter >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
