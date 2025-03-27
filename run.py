#!/usr/bin/env python
"""
中长跑实时指导系统启动脚本

此脚本用于简化系统启动过程，提供一个统一的入口点，
自动处理虚拟环境、依赖检查和应用程序启动。
"""
import os
import sys
import subprocess
import platform
import time
import json
import webbrowser
from pathlib import Path


# 定义颜色代码（用于终端输出）
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """打印系统标题"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 70)
    print("                中长跑实时指导系统                ")
    print("      基于多模态传感器和边缘AI的跑步姿态分析      ")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    time.sleep(3)
def check_environment():
    """检查运行环境"""
    print(f"{Colors.BLUE}[1/5] 检查运行环境...{Colors.ENDC}")
    
    # 检查Python版本
    py_version = sys.version_info
    print(f"  - Python版本: {py_version.major}.{py_version.minor}.{py_version.micro}")
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 8):
        print(f"{Colors.RED}  错误: 需要Python 3.8或更高版本{Colors.ENDC}")
        return False
    
    # 检查操作系统
    system = platform.system()
    print(f"  - 操作系统: {system} {platform.version()}")
    
    print(f"{Colors.GREEN}  环境检查通过!{Colors.ENDC}")
    return True

def setup_virtual_env():
    """设置虚拟环境"""
    print(f"{Colors.BLUE}[2/5] 设置虚拟环境...{Colors.ENDC}")
    
    venv_dir = "venv"
    activation_script = os.path.join(
        venv_dir, 
        "Scripts" if platform.system() == "Windows" else "bin",
        "activate"
    )
    
    # 检查虚拟环境是否已存在
    if os.path.exists(venv_dir):
        print(f"  - 检测到现有虚拟环境: {venv_dir}")
    else:
        print(f"  - 创建新的虚拟环境: {venv_dir}")
        try:
            subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
            print(f"  - 虚拟环境创建完成")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}  错误: 创建虚拟环境失败: {e}{Colors.ENDC}")
            return False, None
    
    # 返回激活脚本路径
    return True, activation_script

def check_dependencies(activation_script):
    """检查并安装依赖"""
    print(f"{Colors.BLUE}[3/5] 检查依赖项...{Colors.ENDC}")
    
    # 执行命令的函数，激活虚拟环境
    def run_in_venv(cmd):
        if platform.system() == "Windows":
            return subprocess.run(f"{activation_script} && {cmd}", shell=True)
        else:
            return subprocess.run(f"source {activation_script} && {cmd}", shell=True)
    
    # 检查pip版本
    print("  - 检查pip版本...")
    run_in_venv("pip --version")
    
    # 安装/更新关键依赖
    key_packages = [
        "flask", "flask-socketio", 
        "numpy", "scipy", 
        "matplotlib", "pandas"
    ]
    
    print("  - 安装关键依赖...")
    for package in key_packages:
        print(f"    安装/更新 {package}...")
        result = run_in_venv(f"pip install {package}")
        if result.returncode != 0:
            print(f"{Colors.YELLOW}  警告: {package} 安装可能不完整{Colors.ENDC}")
    
    # 安装其他项目依赖
    if os.path.exists("requirements.txt"):
        print("  - 安装requirements.txt中的依赖...")
        result = run_in_venv("pip install -r requirements.txt")
        if result.returncode != 0:
            print(f"{Colors.YELLOW}  警告: 一些依赖可能未安装成功{Colors.ENDC}")
    
    return True

def prepare_demo_data():
    """准备演示数据"""
    print(f"{Colors.BLUE}[4/5] 准备演示数据...{Colors.ENDC}")
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    sample_data_path = data_dir / "sample_data.json"
    
    # 检查示例数据是否存在
    if sample_data_path.exists():
        print(f"  - 检测到现有示例数据: {sample_data_path}")
    else:
        print(f"  - 创建示例数据: {sample_data_path}")
        
        # 创建简单的示例数据
        sample_data = {
            "timestamps": [],
            "acceleration": [],
            "gyroscope": [],
            "pressure": [],
            "gait_labels": []
        }
        
        # 生成示例数据点
        import random
        import math
        from datetime import datetime, timedelta
        
        base_time = datetime.now()
        for i in range(500):  # 500个数据点
            # 时间戳
            time_point = base_time + timedelta(milliseconds=i*5)  # 5ms间隔，200Hz
            timestamp = time_point.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
            
            # 模拟跑步加速度数据（简单正弦波+噪声）
            period = i % 50  # 50点一个周期
            acc_z_base = 9.81  # 重力加速度
            acc_z_amp = 1.5    # 振幅
            acc_z = acc_z_base + acc_z_amp * math.sin(2 * math.pi * period / 50) + random.uniform(-0.2, 0.2)
            acc_x = random.uniform(-0.8, 0.8)  # 横向加速度
            acc_y = random.uniform(-0.5, 0.5)  # 前后加速度
            
            # 模拟角速度数据
            gyro_x = random.uniform(-0.3, 0.3)
            gyro_y = random.uniform(-0.2, 0.2)
            gyro_z = 0.15 * math.sin(2 * math.pi * period / 50) + random.uniform(-0.05, 0.05)
            
            # 模拟足压数据
            pressure_phase = (period / 50) * 2 * math.pi
            pressure_1 = 0.3 + 0.2 * math.sin(pressure_phase)  # 前脚掌
            pressure_2 = 0.2 + 0.1 * math.sin(pressure_phase + math.pi/4)  # 中脚掌
            pressure_3 = 0.4 + 0.2 * math.sin(pressure_phase + math.pi/2)  # 后脚掌
            pressure_4 = 0.1 + 0.05 * math.sin(pressure_phase + math.pi)   # 外侧
            
            # 模拟步态相位标签
            gait_phase = "stance" if period < 30 else "swing"
            
            # 添加到数据中
            sample_data["timestamps"].append(timestamp)
            sample_data["acceleration"].append([acc_x, acc_y, acc_z])
            sample_data["gyroscope"].append([gyro_x, gyro_y, gyro_z])
            sample_data["pressure"].append([pressure_1, pressure_2, pressure_3, pressure_4])
            sample_data["gait_labels"].append(gait_phase)
            
        # 保存示例数据
        with open(sample_data_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2)
            
        print(f"  - 示例数据已创建: {len(sample_data['timestamps'])} 条记录")
    
    # 创建模型目录
    models_dir = Path("edge_ai") / "models"
    models_dir.mkdir(exist_ok=True)
    
    return True

def start_application(activation_script):
    """启动应用程序"""
    print(f"{Colors.BLUE}[5/5] 启动应用程序...{Colors.ENDC}")
    
    # 在虚拟环境中执行命令
    def run_in_venv(cmd):
        if platform.system() == "Windows":
            full_cmd = f"{activation_script} && {cmd}"
            return subprocess.Popen(full_cmd, shell=True)
        else:
            full_cmd = f"source {activation_script} && {cmd}"
            return subprocess.Popen(full_cmd, shell=True)
    
    # 启动Flask应用
    print("  - 正在启动Web服务...")
    app_process = run_in_venv("python -m web_ui.app")
    
    # 等待服务启动
    print("  - 等待服务启动...")
    time.sleep(5)  # 等待5秒，确保服务启动完成
    
    # 打开Web浏览器
    try:
        print("  - 正在打开Web浏览器...")
        webbrowser.open("http://localhost:5000")
    except:
        print(f"{Colors.YELLOW}  - 无法自动打开浏览器，请手动访问: http://localhost:5000{Colors.ENDC}")
    
    print(f"{Colors.GREEN}{Colors.BOLD}")
    print("=" * 70)
    print("              中长跑实时指导系统已启动!                ")
    print("          请在浏览器中访问: http://localhost:5000     ")
    print("             按 Ctrl+C 停止服务并退出                 ")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    
    # 等待应用程序运行结束
    try:
        app_process.wait()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}接收到停止信号，正在关闭服务...{Colors.ENDC}")
        app_process.terminate()
        app_process.wait()
        print(f"{Colors.GREEN}服务已停止{Colors.ENDC}")
    
    return True

def main():
    """主函数"""
    # 切换到脚本所在目录，确保相对路径正确
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print_header()
    
    if not check_environment():
        sys.exit(1)
    
    success, activation_script = setup_virtual_env()
    if not success:
        sys.exit(1)
    
    if not check_dependencies(activation_script):
        sys.exit(1)
    
    if not prepare_demo_data():
        sys.exit(1)
    
    start_application(activation_script)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())