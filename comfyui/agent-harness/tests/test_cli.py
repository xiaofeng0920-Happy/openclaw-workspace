#!/usr/bin/env python3
"""
ComfyUI CLI 测试套件
"""

import pytest
import json
import os
from pathlib import Path
from click.testing import CliRunner
from src.cli_comfyui import cli, ComfyUIClient, create_chart_workflow


class TestComfyUIClient:
    """测试 ComfyUI 客户端"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = ComfyUIClient(host="127.0.0.1", port=8188)
        assert client.base_url == "http://127.0.0.1:8188"
        assert client.client_id.startswith("cli_")
    
    def test_client_custom_host(self):
        """测试自定义主机"""
        client = ComfyUIClient(host="192.168.1.100", port=9000)
        assert client.base_url == "http://192.168.1.100:9000"


class TestWorkflowCreation:
    """测试工作流创建"""
    
    def test_create_bar_chart_workflow(self):
        """测试创建柱状图工作流"""
        workflow = create_chart_workflow("bar", "测试图表", {"data": 123})
        
        assert "3" in workflow  # KSampler 节点
        assert "4" in workflow  # CheckpointLoader 节点
        assert "6" in workflow  # CLIPTextEncode 节点
        assert "9" in workflow  # SaveImage 节点
    
    def test_create_line_chart_workflow(self):
        """测试创建折线图工作流"""
        workflow = create_chart_workflow("line", "股价走势", {"prices": [100, 105, 102]})
        
        assert workflow is not None
        assert isinstance(workflow, dict)
    
    def test_create_pie_chart_workflow(self):
        """测试创建饼图工作流"""
        workflow = create_chart_workflow("pie", "资产配置", {"stocks": 60, "cash": 40})
        
        assert workflow is not None
        assert isinstance(workflow, dict)
    
    def test_workflow_structure(self):
        """测试工作流结构"""
        workflow = create_chart_workflow("bar", "测试", {})
        
        # 检查必需节点
        node_ids = list(workflow.keys())
        assert len(node_ids) >= 5  # 至少 5 个节点
        
        # 检查节点格式
        for node_id, node_data in workflow.items():
            assert "class_type" in node_data
            assert "inputs" in node_data


class TestCLIWorkflow:
    """测试 CLI 工作流命令"""
    
    def setup_method(self):
        """设置测试环境"""
        self.runner = CliRunner()
        self.test_dir = Path("/tmp/comfyui_test")
        self.test_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """清理测试环境"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_workflow_new(self):
        """测试创建新工作流"""
        output_file = self.test_dir / "test_workflow.json"
        
        result = self.runner.invoke(cli, [
            "workflow", "new",
            "-o", str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        assert "✅ 工作流已创建" in result.output
        
        # 验证 JSON 格式
        with open(output_file) as f:
            workflow = json.load(f)
        assert isinstance(workflow, dict)
    
    def test_workflow_new_with_template(self):
        """测试使用模板创建工作流"""
        output_file = self.test_dir / "test_template.json"
        
        result = self.runner.invoke(cli, [
            "workflow", "new",
            "-o", str(output_file),
            "-t", "财报对比"
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
    
    def test_workflow_load_not_found(self):
        """测试加载不存在的工作流"""
        result = self.runner.invoke(cli, [
            "workflow", "load",
            "不存在的文件.json"
        ])
        
        assert result.exit_code == 0
        assert "❌ 文件不存在" in result.output
    
    def test_workflow_export(self):
        """测试导出工作流"""
        # 先创建工作流
        workflow_file = self.test_dir / "workflow.json"
        export_file = self.test_dir / "workflow_api.json"
        
        self.runner.invoke(cli, ["workflow", "new", "-o", str(workflow_file)])
        
        result = self.runner.invoke(cli, [
            "workflow", "export",
            str(workflow_file),
            "--output", str(export_file)
        ])
        
        assert result.exit_code == 0
        assert export_file.exists()
        assert "✅ 工作流已导出" in result.output
        
        # 验证 API 格式
        with open(export_file) as f:
            api_data = json.load(f)
        assert "prompt" in api_data
        assert "client_id" in api_data


class TestCLIGenerate:
    """测试 CLI 生成命令"""
    
    def setup_method(self):
        """设置测试环境"""
        self.runner = CliRunner()
    
    def test_generate_chart_invalid_data(self):
        """测试生成图表 - 无效数据"""
        result = self.runner.invoke(cli, [
            "generate", "chart",
            "--type", "bar",
            "--title", "测试",
            "--data", "无效 JSON",
            "--output", "test.png"
        ])
        
        assert result.exit_code == 0
        assert "❌ 数据解析失败" in result.output
    
    def test_generate_chart_from_file(self):
        """测试从文件生成图表"""
        # 创建测试数据文件
        test_dir = Path("/tmp/comfyui_test")
        test_dir.mkdir(exist_ok=True)
        data_file = test_dir / "test_data.json"
        
        with open(data_file, "w") as f:
            json.dump({"Q1": 100, "Q2": 150}, f)
        
        result = self.runner.invoke(cli, [
            "generate", "chart",
            "--type", "bar",
            "--title", "季度营收",
            "--data", str(data_file),
            "--output", str(test_dir / "output.png")
        ])
        
        # 由于 ComfyUI 未运行，应该显示连接错误
        assert result.exit_code == 0


class TestCLIEnhance:
    """测试 CLI 增强命令"""
    
    def setup_method(self):
        """设置测试环境"""
        self.runner = CliRunner()
        self.test_dir = Path("/tmp/comfyui_test")
        self.test_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """清理测试环境"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_enhance_chart_not_found(self):
        """测试美化图表 - 文件不存在"""
        result = self.runner.invoke(cli, [
            "enhance", "chart",
            "--input", "不存在的文件.png",
            "--output", "output.png"
        ])
        
        assert result.exit_code == 0
        assert "❌ 文件不存在" in result.output
    
    def test_enhance_insight(self):
        """测试生成洞察"""
        # 创建测试数据
        data_file = self.test_dir / "data.json"
        output_file = self.test_dir / "insight.txt"
        
        with open(data_file, "w") as f:
            json.dump({"revenue": 1000, "profit": 200}, f)
        
        result = self.runner.invoke(cli, [
            "enhance", "insight",
            "--data", str(data_file),
            "--output", str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        assert "✅ 洞察已生成" in result.output


class TestCLIBatch:
    """测试 CLI 批量命令"""
    
    def setup_method(self):
        """设置测试环境"""
        self.runner = CliRunner()
        self.test_dir = Path("/tmp/comfyui_test")
        self.test_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """清理测试环境"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_batch_generate_not_found(self):
        """测试批量生成 - 目录不存在"""
        result = self.runner.invoke(cli, [
            "batch", "generate",
            "--input-dir", "不存在的目录",
            "--output-dir", str(self.test_dir / "output")
        ])
        
        assert result.exit_code == 0
        assert "❌ 目录不存在" in result.output
    
    def test_batch_generate_empty(self):
        """测试批量生成 - 空目录"""
        input_dir = self.test_dir / "input"
        input_dir.mkdir(exist_ok=True)
        
        result = self.runner.invoke(cli, [
            "batch", "generate",
            "--input-dir", str(input_dir),
            "--output-dir", str(self.test_dir / "output")
        ])
        
        assert result.exit_code == 0
        assert "发现 0 个数据文件" in result.output


class TestCLIStatus:
    """测试 CLI 状态命令"""
    
    def test_status_comfyui_not_running(self):
        """测试状态 - ComfyUI 未运行"""
        runner = CliRunner()
        result = runner.invoke(cli, ["status"])
        
        assert result.exit_code == 0
        assert "❌ 无法连接到 ComfyUI" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
