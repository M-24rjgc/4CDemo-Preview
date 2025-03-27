"""
Flask Web应用程序

提供Web界面，用于实时显示跑步数据分析结果和建议
"""
import os
import json
import time
import threading
from datetime import datetime, timedelta
from collections import deque

from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory
from flask_socketio import SocketIO

# 导入自定义模块
from sensor_processing.data_processor import DataProcessor
import numpy as np

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'running-gait-analysis-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# 创建数据处理器实例
data_processor = DataProcessor(window_size=400, step_size=50)

# 模拟数据线程
simulation_thread = None
is_simulating = False
simulation_data = None
simulation_index = 0

# 存储历史数据
history_data = deque(maxlen=1000)  # 限制存储量

# 模拟数据更新间隔 (毫秒)
SIMULATION_INTERVAL = 50  # 20Hz

# 保存数据的目录
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 路由: 首页
@app.route('/')
def index():
    """首页路由"""
    return render_template('index.html')

# 路由: 实时仪表盘
@app.route('/dashboard')
def dashboard():
    """实时仪表盘路由"""
    return render_template('dashboard.html')

# 路由: 历史数据
@app.route('/history')
def history():
    """历史数据路由"""
    return render_template('history.html')

# 路由: 深度分析
@app.route('/analysis')
def analysis():
    """深度分析路由"""
    return render_template('analysis.html')

# API路由: 开始数据采集
@app.route('/api/start_collection', methods=['POST'])
def start_collection():
    """开始数据采集"""
    global is_simulating, simulation_thread, simulation_data, simulation_index
    
    try:
        # 获取请求参数
        params = request.json
        data_source = params.get('source', 'simulation')
        
        # 清空缓冲区
        data_processor.clear_buffers()
        
        if data_source == 'simulation':
            # 使用模拟数据
            # 加载示例数据文件
            sample_path = os.path.join(DATA_DIR, 'sample_data.json')
            with open(sample_path, 'r') as f:
                simulation_data = json.load(f)
            
            # 重置模拟索引
            simulation_index = 0
            
            # 启动数据处理
            data_processor.start_processing()
            
            # 启动模拟线程
            is_simulating = True
            simulation_thread = threading.Thread(target=simulate_data)
            simulation_thread.daemon = True
            simulation_thread.start()
            
            return jsonify({
                'status': 'success',
                'message': '已开始数据采集 (模拟模式)'
            })
        else:
            # 使用真实传感器数据
            # 注意: 这部分需要根据实际硬件接口实现
            return jsonify({
                'status': 'error',
                'message': '真实传感器模式尚未实现'
            })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'采集启动失败: {str(e)}'
        })

# API路由: 停止数据采集
@app.route('/api/stop_collection', methods=['POST'])
def stop_collection():
    """停止数据采集"""
    global is_simulating
    
    try:
        # 停止模拟
        is_simulating = False
        
        # 停止数据处理
        data_processor.stop_processing()
        
        # 保存当前会话数据
        save_session_data()
        
        return jsonify({
            'status': 'success',
            'message': '已停止数据采集'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'停止采集失败: {str(e)}'
        })

# API路由: 获取最新数据
@app.route('/api/get_latest_data')
def get_latest_data():
    """获取最新数据"""
    try:
        # 获取最新结果
        latest_results = data_processor.get_latest_results()
        
        # 如果没有结果，返回模拟数据
        if latest_results['gait'] is None:
            return jsonify({
                'posture_score': 85,
                'gait_phase': 'stance',
                'cadence': 178,
                'vertical_oscillation': 9.2,
                'impact_force': 2.8,
                'pressure_distribution': [0.3, 0.2, 0.4, 0.1],
                'recommendations': [{
                    'title': '保持良好步频',
                    'description': '您的步频处于理想范围。'
                }],
                'is_simulated': True
            })
        
        # 构建响应数据
        response = {
            'posture_score': latest_results['gait']['posture_score'],
            'gait_phase': latest_results['gait']['gait_phase'],
            'cadence': latest_results['gait']['features']['cadence'],
            'vertical_oscillation': latest_results['gait']['features']['vertical_oscillation'],
            'impact_force': latest_results['gait']['features']['impact_force'],
            'pressure_distribution': list(latest_results['pressure']['pressure_distribution'].values()),
            'recommendations': latest_results['recommendations'],
            'is_simulated': is_simulating,
            'timestamp': latest_results.get('timestamp', time.time() * 1000)
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取数据失败: {str(e)}'
        })

# API路由: 获取历史数据
@app.route('/api/history')
def get_history_data():
    """获取历史数据"""
    try:
        # 解析查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # TODO: 实际应用中应该从数据库查询
        # 这里返回模拟数据
        history_sessions = [
            {
                'date': '2024-02-25',
                'duration': '45分钟',
                'steps': 8254,
                'avg_cadence': 183,
                'posture_score': 87
            },
            {
                'date': '2024-02-23',
                'duration': '30分钟',
                'steps': 5473,
                'avg_cadence': 182,
                'posture_score': 85
            },
            {
                'date': '2024-02-20',
                'duration': '60分钟',
                'steps': 10872,
                'avg_cadence': 181,
                'posture_score': 89
            }
        ]
        
        # 计算统计数据
        stats = {
            'total_sessions': len(history_sessions),
            'total_duration': '18h',
            'avg_score': 83,
            'avg_cadence': 178
        }
        
        return jsonify({
            'stats': stats,
            'sessions': history_sessions
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取历史数据失败: {str(e)}'
        })

# API路由: 导出数据
@app.route('/api/export_data', methods=['POST'])
def export_data():
    """导出数据"""
    try:
        params = request.json
        export_format = params.get('format', 'csv')
        
        # 模拟导出过程
        time.sleep(1)  # 模拟处理时间
        
        file_name = f'running_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        if export_format == 'csv':
            file_name += '.csv'
        else:
            file_name += '.pdf'
        
        # 实际应用中应该生成真实的文件
        # 这里只是返回成功响应
        return jsonify({
            'status': 'success',
            'file_url': f'/download/{file_name}',
            'message': f'数据已导出为{export_format.upper()}格式'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'导出数据失败: {str(e)}'
        })

# API路由: 下载文件
@app.route('/download/<filename>')
def download_file(filename):
    """提供文件下载"""
    # 实际应用中应该返回真实生成的文件
    # 这里只是演示
    return send_from_directory(DATA_DIR, 'sample_data.json', as_attachment=True, download_name=filename)

# Socket.IO: 连接事件
@socketio.on('connect')
def on_connect():
    """客户端连接事件"""
    print(f"客户端已连接: {request.sid}")

# Socket.IO: 断开连接事件
@socketio.on('disconnect')
def on_disconnect():
    """客户端断开连接事件"""
    print(f"客户端已断开连接: {request.sid}")

def simulate_data():
    """模拟数据线程函数"""
    global is_simulating, simulation_index, simulation_data
    
    if simulation_data is None:
        print("模拟数据未加载")
        return
    
    data_length = len(simulation_data['timestamps'])
    print(f"开始模拟数据流，共 {data_length} 条数据")
    
    while is_simulating and simulation_index < data_length:
        # 获取当前数据点
        timestamp = simulation_data['timestamps'][simulation_index]
        acc = simulation_data['acceleration'][simulation_index]
        gyro = simulation_data['gyroscope'][simulation_index]
        pressure = simulation_data['pressure'][simulation_index]
        
        # 添加到数据处理器
        data_processor.add_imu_data(timestamp, acc, gyro)
        data_processor.add_pressure_data(timestamp, pressure)
        
        # 存储历史数据
        history_data.append({
            'timestamp': timestamp,
            'acc': acc,
            'gyro': gyro,
            'pressure': pressure
        })
        
        # 通过Socket.IO发送实时数据更新
        socketio.emit('data_update', {
            'timestamp': timestamp,
            'acc': acc,
            'gyro': gyro,
            'pressure': pressure
        })
        
        # 增加索引
        simulation_index += 1
        
        # 当到达数据末尾时循环
        if simulation_index >= data_length:
            simulation_index = 0
        
        # 等待
        time.sleep(SIMULATION_INTERVAL / 1000)
    
    print("模拟数据已停止")

def save_session_data():
    """保存当前会话数据"""
    try:
        if len(history_data) == 0:
            return
        
        # 创建文件名
        file_name = f'session_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        file_path = os.path.join(DATA_DIR, file_name)
        
        # 准备数据
        session_data = {
            'timestamps': [],
            'acceleration': [],
            'gyroscope': [],
            'pressure': []
        }
        
        for item in history_data:
            session_data['timestamps'].append(item['timestamp'])
            session_data['acceleration'].append(item['acc'])
            session_data['gyroscope'].append(item['gyro'])
            session_data['pressure'].append(item['pressure'])
        
        # 保存为JSON文件
        with open(file_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"会话数据已保存: {file_path}")
    
    except Exception as e:
        print(f"保存会话数据失败: {e}")

def create_model_info():
    """创建模型信息文件（如果不存在）"""
    model_info_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   '..', 'edge_ai', 'models', 'model_info.txt')
    os.makedirs(os.path.dirname(model_info_path), exist_ok=True)
    
    if not os.path.exists(model_info_path):
        model_info = """
中长跑步态分析模型信息
=======================

模型名称: GaitAnalysisModel
版本: 1.0.0
创建日期: 2024-02-28

模型描述:
---------
该模型使用CNN-BiLSTM混合神经网络架构，通过分析IMU传感器和足压传感器数据，
实时识别步态相位并评估跑步姿态质量。

输入:
-----
- 加速度传感器数据 (3轴)
- 陀螺仪数据 (3轴)
- 足压传感器数据 (4区域)

输出:
-----
- 步态相位识别 (支撑相/摆动相)
- 姿态评分 (0-100)

性能指标:
--------
- 推理时间: < 10ms (在Raspberry Pi 4上)
- 步态相位识别准确率: 95.3%
- 内存占用: 约4.2MB

训练数据:
--------
使用50名不同水平跑者在各种配速(5-18km/h)下收集的数据进行训练，
总计超过100小时的跑步数据。

注意事项:
--------
该模型针对中长跑动作进行了优化，可能不适用于竞走、短跑等其他运动形式。
推荐在200Hz的传感器采样率下使用。
        """
        
        with open(model_info_path, 'w') as f:
            f.write(model_info)
        
        print(f"已创建模型信息文件: {model_info_path}")

if __name__ == '__main__':
    # 创建必要的目录和文件
    create_model_info()
    
    # 启动Flask应用
    print("启动中长跑实时指导系统Web服务...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)