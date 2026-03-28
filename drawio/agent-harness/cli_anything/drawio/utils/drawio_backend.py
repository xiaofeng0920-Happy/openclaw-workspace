"""
Draw.io Backend - XML-based .drawio file manipulation

.drawio files are XML-based and can be manipulated programmatically.
This module provides the core functionality for creating and editing diagrams.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class DrawioBackend:
    """Backend for manipulating .drawio files"""
    
    # Draw.io XML namespace
    NS = {'mx': 'http://www.w3.org/2005/08/mxGraph'}
    
    # Shape types mapping
    SHAPE_TYPES = {
        'rectangle': 'rectangle',
        'ellipse': 'ellipse',
        'rhombus': 'rhombus',
        'triangle': 'triangle',
        'cylinder': 'cylinder',
        'document': 'document',
        'folder': 'folder',
        'cloud': 'cloud',
        'actor': 'actor',
        'process': 'process',
        'decision': 'decision',
        'data': 'data',
        'terminator': 'terminator',
        'note': 'note',
    }
    
    # Template definitions
    TEMPLATES = {
        'asset-allocation': '资产配置图',
        'price-chart': '股价走势图',
        'investment-flow': '投资流程图',
        'org': '组织结构图',
        'mindmap': '思维导图',
    }
    
    def __init__(self):
        self.root = None
        self.tree = None
        self.diagram = None
        self.current_file = None
        self.shape_counter = 0
        
    def create_new(self, diagram_type: str = 'default') -> ET.Element:
        """Create a new .drawio document structure"""
        # Root element
        self.root = ET.Element('mxfile')
        self.root.set('host', 'cli-anything-drawio')
        self.root.set('modified', datetime.now().isoformat())
        self.root.set('version', '21.0.0')
        
        # Create diagram element
        self.diagram = ET.SubElement(self.root, 'diagram')
        self.diagram.set('id', f'diagram-{datetime.now().timestamp()}')
        self.diagram.set('name', diagram_type)
        
        # Create mxGraphModel
        model = ET.SubElement(self.diagram, 'mxGraphModel')
        model.set('dx', '1422')
        model.set('dy', '799')
        model.set('grid', '1')
        model.set('gridSize', '10')
        model.set('guides', '1')
        model.set('tooltips', '1')
        model.set('connect', '1')
        model.set('arrows', '1')
        model.set('fold', '1')
        model.set('page', '1')
        model.set('pageScale', '1')
        model.set('pageWidth', '827')
        model.set('pageHeight', '1169')
        model.set('math', '0')
        model.set('shadow', '0')
        
        # Create root
        root = ET.SubElement(model, 'root')
        
        # Add default layer
        layer = ET.SubElement(root, 'mxCell')
        layer.set('id', '0')
        
        # Add default layer (layer 1)
        layer1 = ET.SubElement(root, 'mxCell')
        layer1.set('id', '1')
        layer1.set('parent', '0')
        
        return self.root
    
    def add_shape(self, label: str, shape_type: str = 'rectangle',
                  x: int = 100, y: int = 100, width: int = 120, height: int = 60,
                  style: Optional[Dict] = None) -> str:
        """Add a shape to the current diagram"""
        if self.root is None:
            self.create_new()
        
        self.shape_counter += 1
        shape_id = f'shape-{self.shape_counter}'
        
        # Get model root
        model = self.diagram.find('mxGraphModel')
        root = model.find('root')
        
        # Create cell element
        cell = ET.SubElement(root, 'mxCell')
        cell.set('id', shape_id)
        cell.set('value', label)
        cell.set('style', self._build_style(shape_type, style))
        cell.set('vertex', '1')
        cell.set('parent', '1')
        
        # Add geometry
        geometry = ET.SubElement(cell, 'mxGeometry')
        geometry.set('x', str(x))
        geometry.set('y', str(y))
        geometry.set('width', str(width))
        geometry.set('height', str(height))
        
        return shape_id
    
    def add_connector(self, from_shape: str, to_shape: str, 
                      label: str = '', style: Optional[Dict] = None) -> str:
        """Add a connector between two shapes"""
        if self.root is None:
            raise ValueError("No diagram created yet")
        
        self.shape_counter += 1
        connector_id = f'connector-{self.shape_counter}'
        
        # Get model root
        model = self.diagram.find('mxGraphModel')
        root = model.find('root')
        
        # Create edge element
        edge = ET.SubElement(root, 'mxCell')
        edge.set('id', connector_id)
        edge.set('value', label)
        edge.set('style', self._build_connector_style(style))
        edge.set('edge', '1')
        edge.set('parent', '1')
        edge.set('source', from_shape)
        edge.set('target', to_shape)
        
        return connector_id
    
    def add_text(self, text: str, x: int = 100, y: int = 100,
                 font_size: int = 12, bold: bool = False,
                 width: int = 200, height: int = 30) -> str:
        """Add a text element"""
        style = {
            'text': 1,
            'html': 1,
            'fontSize': font_size,
            'fontStyle': 1 if bold else 0,
            'align': 'center',
            'verticalAlign': 'middle',
            'whiteSpace': 'wrap',
        }
        return self.add_shape(text, 'text', x, y, width, height, style)
    
    def _build_style(self, shape_type: str, style: Optional[Dict] = None) -> str:
        """Build Draw.io style string"""
        base_style = {
            'rectangle': 'rounded=0;whiteSpace=wrap;html=1;',
            'ellipse': 'ellipse;whiteSpace=wrap;html=1;',
            'rhombus': 'rhombus;whiteSpace=wrap;html=1;',
            'triangle': 'triangle;whiteSpace=wrap;html=1;',
            'cylinder': 'shape=cylinder;whiteSpace=wrap;html=1;',
            'document': 'shape=document;whiteSpace=wrap;html=1;',
            'folder': 'shape=folder;whiteSpace=wrap;html=1;',
            'cloud': 'shape=cloud;whiteSpace=wrap;html=1;',
            'actor': 'shape=actor;whiteSpace=wrap;html=1;',
            'process': 'shape=process;whiteSpace=wrap;html=1;',
            'decision': 'shape=rhombus;whiteSpace=wrap;html=1;',
            'data': 'shape=data;whiteSpace=wrap;html=1;',
            'terminator': 'shape=mxgraph.flowchart.terminator;whiteSpace=wrap;html=1;',
            'note': 'shape=note;whiteSpace=wrap;html=1;',
            'text': 'text;html=1;strokeColor=none;fillColor=none;align=center;',
        }
        
        style_str = base_style.get(shape_type, 'rounded=0;whiteSpace=wrap;html=1;')
        
        if style:
            for key, value in style.items():
                style_str += f'{key}={value};'
        
        return style_str
    
    def _build_connector_style(self, style: Optional[Dict] = None) -> str:
        """Build connector style string"""
        base = 'endArrow=classic;html=1;exitX=1;exitY=0.5;entryX=0;entryY=0.5;'
        
        if style:
            for key, value in style.items():
                base += f'{key}={value};'
        
        return base
    
    def create_template(self, template_name: str, data: Optional[Dict] = None) -> str:
        """Create a diagram from template"""
        self.create_new(template_name)
        
        if template_name == 'asset-allocation':
            self._create_asset_allocation(data)
        elif template_name == 'price-chart':
            self._create_price_chart(data)
        elif template_name == 'investment-flow':
            self._create_investment_flow()
        elif template_name == 'org':
            self._create_org_chart()
        elif template_name == 'mindmap':
            self._create_mindmap()
        
        return self.current_file
    
    def _create_asset_allocation(self, data: Optional[Dict] = None):
        """Create asset allocation pie chart"""
        # Title
        self.add_text("资产配置", x=300, y=50, font_size=24, bold=True, width=300)
        
        # Add date
        date_str = datetime.now().strftime('%Y-%m-%d')
        self.add_text(f"({date_str})", x=350, y=80, font_size=14, width=200)
        
        # Create pie chart representation (using rectangles for simplicity)
        if data:
            y_offset = 150
            for asset, percentage in data.items():
                self.add_shape(f"{asset}: {percentage}%", 'rectangle', 
                              x=250, y=y_offset, width=400, height=40)
                y_offset += 60
        else:
            # Default allocation
            allocations = [
                ("美股", "60%"),
                ("港股", "23%"),
                ("现金", "17%")
            ]
            y_offset = 150
            for asset, pct in allocations:
                self.add_shape(f"{asset}: {pct}", 'rectangle',
                              x=250, y=y_offset, width=400, height=40)
                y_offset += 60
    
    def _create_price_chart(self, data: Optional[Dict] = None):
        """Create price chart"""
        # Title
        self.add_text("股价走势图", x=300, y=50, font_size=24, bold=True, width=300)
        
        # Create axes
        # Y-axis
        self.add_shape('', 'line', x=100, y=100, width=2, height=300,
                      style={'strokeColor': '#000000', 'strokeWidth': 2})
        # X-axis
        self.add_shape('', 'line', x=100, y=400, width=600, height=2,
                      style={'strokeColor': '#000000', 'strokeWidth': 2})
        
        # Add labels
        self.add_text("股价", x=50, y=250, font_size=12, width=40, height=30)
        self.add_text("时间", x=400, y=420, font_size=12, width=80, height=30)
        
        # Add sample data points
        if data and 'prices' in data:
            for i, price in enumerate(data['prices'][:10]):
                x = 120 + i * 50
                y = 380 - (price / max(data['prices']) * 250)
                self.add_shape(f"{price}", 'ellipse', x, y, 60, 40)
        else:
            # Sample chart shape
            self.add_shape("📈 示例图表", 'rectangle', x=250, y=200, width=300, height=100)
    
    def _create_investment_flow(self):
        """Create investment flowchart"""
        # Main flow
        steps = [
            ("财报发布", 50, 200),
            ("数据分析", 250, 200),
            ("持仓评估", 450, 200),
            ("操作建议", 650, 200),
            ("执行交易", 850, 200),
        ]
        
        shape_ids = []
        for label, x, y in steps:
            shape_id = self.add_shape(label, 'process', x, y, 150, 60)
            shape_ids.append(shape_id)
        
        # Add connectors
        for i in range(len(shape_ids) - 1):
            self.add_connector(shape_ids[i], shape_ids[i + 1])
        
        # Secondary flow (below)
        secondary = [
            ("业绩会", 50, 320),
            ("盈亏计算", 250, 320),
            ("风险评级", 450, 320),
            ("止盈止损", 650, 320),
            ("飞书通知", 850, 320),
        ]
        
        for label, x, y in secondary:
            self.add_shape(label, 'rectangle', x, y, 150, 50)
        
        # Title
        self.add_text("投资决策流程", x=350, y=50, font_size=24, bold=True, width=400)
    
    def _create_org_chart(self):
        """Create organization chart"""
        # Title
        self.add_text("组织结构图", x=300, y=30, font_size=24, bold=True, width=300)
        
        # Hierarchy
        levels = [
            [("CEO/总经理", 350, 80, 200, 60)],
            [("技术总监", 150, 180, 150, 50), ("运营总监", 350, 180, 150, 50), ("财务总监", 550, 180, 150, 50)],
            [("开发团队", 100, 280, 100, 50), ("测试团队", 200, 280, 100, 50), 
             ("市场团队", 300, 280, 100, 50), ("销售团队", 400, 280, 100, 50),
             ("会计", 500, 280, 100, 50), ("审计", 600, 280, 100, 50)],
        ]
        
        for level in levels:
            for item in level:
                self.add_shape(*item)
    
    def _create_mindmap(self):
        """Create mindmap structure"""
        # Central topic
        center_id = self.add_shape("投资分析", 'ellipse', x=350, y=200, 
                                   width=150, height=80,
                                   style={'fillColor': '#FFE6CC', 'strokeColor': '#D79B00'})
        
        # Branches
        branches = [
            ("市场分析", 150, 100),
            ("持仓分析", 550, 100),
            ("风险评估", 150, 300),
            ("操作建议", 550, 300),
        ]
        
        for label, x, y in branches:
            branch_id = self.add_shape(label, 'rectangle', x, y, 120, 50)
            self.add_connector(center_id, branch_id, style={'endArrow': 'none'})
    
    def save(self, filepath: str) -> str:
        """Save the diagram to a .drawio file"""
        if self.root is None:
            raise ValueError("No diagram to save")
        
        # Ensure .drawio extension
        if not filepath.endswith('.drawio'):
            filepath += '.drawio'
        
        self.current_file = filepath
        
        # Convert to string with proper formatting
        xml_str = ET.tostring(self.root, encoding='unicode')
        
        # Pretty print
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ', encoding='UTF-8').decode('utf-8')
        
        # Remove extra blank lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        pretty_xml = '\n'.join(lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        return filepath
    
    def load(self, filepath: str) -> bool:
        """Load an existing .drawio file"""
        if not os.path.exists(filepath):
            return False
        
        self.tree = ET.parse(filepath)
        self.root = self.tree.getroot()
        self.diagram = self.root.find('diagram')
        self.current_file = filepath
        
        # Count existing shapes
        model = self.diagram.find('mxGraphModel')
        if model:
            root = model.find('root')
            if root:
                self.shape_counter = len(root.findall('mxCell'))
        
        return True
    
    def export_png(self, filepath: str, dpi: int = 300) -> str:
        """
        Export to PNG format
        
        Note: This requires Draw.io CLI or conversion tool.
        For now, we create a placeholder and document the requirement.
        """
        if not self.current_file:
            raise ValueError("No diagram loaded")
        
        # In production, this would call:
        # draw.io -x input.drawio -o output.png --dpi 300
        
        # For now, create a note about the export
        export_info = {
            'source': self.current_file,
            'target': filepath,
            'format': 'png',
            'dpi': dpi,
            'note': 'Export requires Draw.io CLI: draw.io -x input.drawio -o output.png --dpi 300'
        }
        
        info_file = filepath.replace('.png', '.export.json')
        with open(info_file, 'w') as f:
            json.dump(export_info, f, indent=2)
        
        return info_file
    
    def export_svg(self, filepath: str) -> str:
        """Export to SVG format"""
        if not self.current_file:
            raise ValueError("No diagram loaded")
        
        export_info = {
            'source': self.current_file,
            'target': filepath,
            'format': 'svg',
            'note': 'Export requires Draw.io CLI: draw.io -x input.drawio -o output.svg'
        }
        
        info_file = filepath.replace('.svg', '.export.json')
        with open(info_file, 'w') as f:
            json.dump(export_info, f, indent=2)
        
        return info_file
    
    def export_pdf(self, filepath: str) -> str:
        """Export to PDF format"""
        if not self.current_file:
            raise ValueError("No diagram loaded")
        
        export_info = {
            'source': self.current_file,
            'target': filepath,
            'format': 'pdf',
            'note': 'Export requires Draw.io CLI: draw.io -x input.drawio -o output.pdf'
        }
        
        info_file = filepath.replace('.pdf', '.export.json')
        with open(info_file, 'w') as f:
            json.dump(export_info, f, indent=2)
        
        return info_file
    
    def to_dict(self) -> Dict:
        """Convert current diagram to dictionary for JSON output"""
        if self.root is None:
            return {}
        
        result = {
            'file': self.current_file,
            'diagram_type': self.diagram.get('name') if self.diagram else 'unknown',
            'shape_count': self.shape_counter,
        }
        
        return result
