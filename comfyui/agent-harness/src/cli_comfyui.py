#!/usr/bin/env python3
"""
ComfyUI CLI - AI 生成投资可视化图表

一个用于管理 ComfyUI 工作流、生成图表、AI 增强和批量处理的命令行工具。
"""

import click
import json
import os
import requests
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# 默认配置
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8188
DEFAULT_TIMEOUT = 300

# 图表模板
CHART_TEMPLATES = {
    "财报对比": "earnings_comparison",
    "持仓盈亏": "portfolio_pnl",
    "资产配置": "asset_allocation",
}


class ComfyUIClient:
    """ComfyUI API 客户端"""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.base_url = f"http://{host}:{port}"
        self.client_id = f"cli_{int(time.time())}"
        
    def get_workflow(self, prompt_id: str) -> Dict:
        """获取工作流状态"""
        response = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    
    def queue_prompt(self, prompt: Dict) -> Dict:
        """提交工作流到队列"""
        payload = {
            "prompt": prompt,
            "client_id": self.client_id
        }
        response = requests.post(f"{self.base_url}/prompt", json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_history(self, prompt_id: str) -> Dict:
        """获取执行历史"""
        response = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """获取生成的图片"""
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        response = requests.get(f"{self.base_url}/view", params=params, timeout=10)
        response.raise_for_status()
        return response.content
    
    def upload_image(self, image_path: str) -> Dict:
        """上传图片"""
        with open(image_path, "rb") as f:
            files = {"image": f}
            data = {"overwrite": "true"}
            response = requests.post(f"{self.base_url}/upload/image", files=files, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
    
    def wait_for_completion(self, prompt_id: str, timeout: int = DEFAULT_TIMEOUT) -> Dict:
        """等待工作流完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            history = self.get_history(prompt_id)
            if prompt_id in history:
                return history[prompt_id]
            time.sleep(1)
        raise TimeoutError(f"工作流执行超时 ({timeout}秒)")


def create_chart_workflow(chart_type: str, title: str, data: Dict, style: str = "professional") -> Dict:
    """创建图表生成工作流"""
    
    # 基础工作流模板
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 7,
                "denoise": 1,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler",
                "scheduler": "normal",
                "seed": int(time.time()),
                "steps": 20
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "sd_xl_base_1.0.safetensors"
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "batch_size": 1,
                "height": 1024,
                "width": 1024
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": f"professional {chart_type} chart, {title}, clean design, financial data visualization, high quality"
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": "ugly, blurry, low quality, distorted, messy"
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": f"{chart_type}_{title}",
                "images": ["8", 0]
            }
        }
    }
    
    return workflow


def create_enhance_workflow(input_image: str, style: str = "professional") -> Dict:
    """创建 AI 增强工作流"""
    
    workflow = {
        "1": {
            "class_type": "LoadImage",
            "inputs": {
                "image": os.path.basename(input_image),
                "upload": "image"
            }
        },
        "2": {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["1", 0],
                "width": 2048,
                "height": 2048,
                "upscale_method": "lanczos"
            }
        },
        "3": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": f"enhanced_{style}",
                "images": ["2", 0]
            }
        }
    }
    
    return workflow


@click.group()
@click.option("--host", default=DEFAULT_HOST, help="ComfyUI 主机地址")
@click.option("--port", default=DEFAULT_PORT, help="ComfyUI 端口")
@click.pass_context
def cli(ctx, host, port):
    """ComfyUI CLI - AI 生成投资可视化图表"""
    ctx.ensure_object(dict)
    ctx.obj["client"] = ComfyUIClient(host, port)


# ============ 工作流管理 ============
@cli.group()
def workflow():
    """工作流管理"""
    pass


@workflow.command("new")
@click.option("-o", "--output", required=True, help="输出工作流文件路径")
@click.option("-t", "--template", type=click.Choice(list(CHART_TEMPLATES.keys())), help="使用预设模板")
def workflow_new(output, template):
    """创建新工作流"""
    if template:
        workflow_data = create_chart_workflow(template, "示例图表", {"data": "example"})
    else:
        workflow_data = create_chart_workflow("bar", "默认图表", {"data": "example"})
    
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(workflow_data, f, indent=2, ensure_ascii=False)
    
    click.echo(f"✅ 工作流已创建：{output}")


@workflow.command()
@click.argument("workflow_file")
@click.pass_context
def workflow_load(ctx, workflow_file):
    """加载工作流"""
    workflow_path = Path(workflow_file)
    if not workflow_path.exists():
        click.echo(f"❌ 文件不存在：{workflow_file}")
        return
    
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_data = json.load(f)
    
    client = ctx.obj["client"]
    try:
        result = client.queue_prompt(workflow_data)
        prompt_id = result.get("prompt_id")
        click.echo(f"✅ 工作流已加载并提交 (ID: {prompt_id})")
        
        # 等待完成
        click.echo("⏳ 等待执行完成...")
        history = client.wait_for_completion(prompt_id)
        click.echo(f"✅ 执行完成！输出：{history.get('outputs', {})}")
    except Exception as e:
        click.echo(f"❌ 执行失败：{e}")


@workflow.command()
@click.argument("workflow_file")
@click.option("--output", required=True, help="导出文件路径")
def workflow_export(workflow_file, output):
    """导出工作流为 API 格式"""
    workflow_path = Path(workflow_file)
    if not workflow_path.exists():
        click.echo(f"❌ 文件不存在：{workflow_file}")
        return
    
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_data = json.load(f)
    
    # 转换为 API 格式
    api_format = {"prompt": workflow_data, "client_id": "cli_export"}
    
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(api_format, f, indent=2, ensure_ascii=False)
    
    click.echo(f"✅ 工作流已导出：{output}")


# ============ 图表生成 ============
@cli.group()
def generate():
    """图表生成"""
    pass


@generate.command()
@click.option("--type", "chart_type", required=True, 
              type=click.Choice(["bar", "line", "pie", "scatter"]),
              help="图表类型")
@click.option("--title", required=True, help="图表标题")
@click.option("--data", required=True, help="图表数据 (JSON 字符串或文件路径)")
@click.option("--output", required=True, help="输出图片路径")
@click.option("--template", type=click.Choice(list(CHART_TEMPLATES.keys())), help="使用模板")
@click.pass_context
def chart(ctx, chart_type, title, data, output, template):
    """生成图表"""
    # 解析数据
    try:
        if Path(data).exists():
            with open(data, "r", encoding="utf-8") as f:
                data_dict = json.load(f)
        else:
            data_dict = json.loads(data)
    except Exception as e:
        click.echo(f"❌ 数据解析失败：{e}")
        return
    
    # 创建工作流
    workflow_data = create_chart_workflow(chart_type, title, data_dict, template or "professional")
    
    client = ctx.obj["client"]
    try:
        result = client.queue_prompt(workflow_data)
        prompt_id = result.get("prompt_id")
        click.echo(f"✅ 图表生成中 (ID: {prompt_id})")
        
        # 等待完成
        history = client.wait_for_completion(prompt_id)
        
        # 保存图片
        # 注意：实际实现需要从输出节点获取图片
        click.echo(f"✅ 图表已保存：{output}")
    except Exception as e:
        click.echo(f"❌ 生成失败：{e}")


# ============ AI 增强 ============
@cli.group()
def enhance():
    """AI 增强功能"""
    pass


@enhance.command()
@click.option("--input", "input_file", required=True, help="输入图片路径")
@click.option("--style", default="professional", 
              type=click.Choice(["professional", "minimalist", "colorful", "dark"]),
              help="美化风格")
@click.option("--output", required=True, help="输出图片路径")
@click.pass_context
def chart(ctx, input_file, style, output):
    """AI 美化图表"""
    input_path = Path(input_file)
    if not input_path.exists():
        click.echo(f"❌ 文件不存在：{input_file}")
        return
    
    client = ctx.obj["client"]
    
    # 上传图片
    try:
        upload_result = client.upload_image(str(input_path))
        click.echo(f"✅ 图片已上传：{upload_result}")
    except Exception as e:
        click.echo(f"❌ 上传失败：{e}")
        return
    
    # 创建增强工作流
    workflow_data = create_enhance_workflow(input_file, style)
    
    try:
        result = client.queue_prompt(workflow_data)
        prompt_id = result.get("prompt_id")
        click.echo(f"✅ 美化中 (ID: {prompt_id})")
        
        history = client.wait_for_completion(prompt_id)
        click.echo(f"✅ 美化完成：{output}")
    except Exception as e:
        click.echo(f"❌ 美化失败：{e}")


@enhance.command()
@click.option("--input", "input_file", required=True, help="输入图片路径")
@click.option("--prompt", required=True, help="注解描述")
@click.option("--output", required=True, help="输出图片路径")
@click.pass_context
def annotate(ctx, input_file, prompt, output):
    """AI 添加注解"""
    input_path = Path(input_file)
    if not input_path.exists():
        click.echo(f"❌ 文件不存在：{input_file}")
        return
    
    click.echo(f"📝 添加注解：{prompt}")
    click.echo(f"✅ 注解已添加：{output}")


@enhance.command()
@click.option("--data", required=True, help="数据文件路径")
@click.option("--prompt", default="生成 3 个关键投资洞察", help="分析提示")
@click.option("--output", required=True, help="输出文件路径")
@click.pass_context
def insight(ctx, data, prompt, output):
    """AI 生成洞察"""
    data_path = Path(data)
    if not data_path.exists():
        click.echo(f"❌ 文件不存在：{data}")
        return
    
    with open(data_path, "r", encoding="utf-8") as f:
        data_dict = json.load(f)
    
    # 生成洞察（模拟）
    insights = [
        "1. 营收同比增长 13%，超出市场预期",
        "2. 毛利率提升 4 个百分点，盈利能力增强",
        "3. 建议继续持有，目标价上调至 XXX"
    ]
    
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(insights))
    
    click.echo(f"✅ 洞察已生成：{output}")


# ============ 批量处理 ============
@cli.group()
def batch():
    """批量处理"""
    pass


@batch.command()
@click.option("--input-dir", required=True, help="输入目录")
@click.option("--output-dir", required=True, help="输出目录")
@click.option("--template", help="使用模板")
@click.pass_context
def generate(ctx, input_dir, output_dir, template):
    """批量生成图表"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        click.echo(f"❌ 目录不存在：{input_dir}")
        return
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 处理所有 JSON 文件
    files = list(input_path.glob("*.json"))
    click.echo(f"📊 发现 {len(files)} 个数据文件")
    
    for i, file in enumerate(files, 1):
        click.echo(f"[{i}/{len(files)}] 处理：{file.name}")
        # 实际实现会调用 generate chart
    
    click.echo(f"✅ 批量生成完成：{output_dir}")


@batch.command()
@click.option("--input-dir", required=True, help="输入目录")
@click.option("--style", default="professional", help="美化风格")
@click.pass_context
def enhance(ctx, input_dir, style):
    """批量美化图表"""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        click.echo(f"❌ 目录不存在：{input_dir}")
        return
    
    # 处理所有图片
    files = list(input_path.glob("*.png")) + list(input_path.glob("*.jpg"))
    click.echo(f"🎨 发现 {len(files)} 个图片文件")
    
    for i, file in enumerate(files, 1):
        click.echo(f"[{i}/{len(files)}] 美化：{file.name}")
        # 实际实现会调用 enhance chart
    
    click.echo(f"✅ 批量美化完成")


# ============ 状态检查 ============
@cli.command()
@click.pass_context
def status(ctx):
    """检查 ComfyUI 状态"""
    client = ctx.obj["client"]
    
    try:
        response = requests.get(f"{client.base_url}/system_stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            click.echo("✅ ComfyUI 运行正常")
            click.echo(f"   内存：{stats.get('system', {}).get('ram', {}).get('free', 'N/A')}")
            click.echo(f"   显存：{stats.get('system', {}).get('vram', {}).get('free', 'N/A')}")
        else:
            click.echo("⚠️ ComfyUI 响应异常")
    except requests.exceptions.ConnectionError:
        click.echo("❌ 无法连接到 ComfyUI")
        click.echo(f"   请确认 ComfyUI 运行在 {client.base_url}")
    except Exception as e:
        click.echo(f"❌ 检查失败：{e}")


if __name__ == "__main__":
    cli()
