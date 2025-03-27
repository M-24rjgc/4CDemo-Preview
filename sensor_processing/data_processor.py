"""
数据处理器模块

负责协调传感器数据处理流程，包括滤波、特征提取等
"""
import numpy as np
import queue
import threading
import time
from collections import deque

from sensor_processing.filter import (
    lowpass_filter, median_filter, highpass_filter, bandpass_filter
)
from sensor_processing.feature_extractor import (
    extract_features, extract_pressure_features
)
from edge_ai.inference import GaitAnalysisModel

class DataProcessor:
    """
    数据处理器类
    
    负责对传感器原始数据进行处理、特征提取和模型推理
    """
    
    def __init__(self, window_size=400, step_size=50):
        """
        初始化数据处理器
        
        Args:
            window_size: 滑动窗口大小（数据点数量）
            step_size: 滑动窗口步长（数据点数量）
        """
        self.window_size = window_size
        self.step_size = step_size
        
        # 初始化数据缓冲区
        self.acc_buffer = deque(maxlen=window_size * 2)  # 加速度缓冲区
        self.gyro_buffer = deque(maxlen=window_size * 2)  # 角速度缓冲区
        self.pressure_buffer = deque(maxlen=window_size * 2)  # 足压缓冲区
        self.timestamp_buffer = deque(maxlen=window_size * 2)  # 时间戳缓冲区
        
        # 初始化处理队列
        self.processing_queue = queue.Queue(maxsize=100)
        self.result_queue = queue.Queue(maxsize=100)
        
        # 加载模型
        self.model = GaitAnalysisModel()
        
        # 设置采样率 (Hz)
        self.sampling_rate = 200
        
        # 滤波器参数
        self.acc_lowpass_cutoff = 20.0  # 加速度低通滤波截止频率
        self.gyro_lowpass_cutoff = 20.0  # 角速度低通滤波截止频率
        
        # 初始化处理线程
        self.processing_thread = None
        self.is_running = False
        self.lock = threading.Lock()
        
        # 最新分析结果
        self.latest_results = {
            'gait': None,
            'pressure': None,
            'recommendations': []
        }
    
    def start_processing(self):
        """
        启动数据处理线程
        """
        if not self.is_running:
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._process_data_loop)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            print("数据处理线程已启动")
    
    def stop_processing(self):
        """
        停止数据处理线程
        """
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
            print("数据处理线程已停止")
    
    def add_imu_data(self, timestamp, acc_data, gyro_data):
        """
        添加IMU数据到缓冲区
        
        Args:
            timestamp: 时间戳 (毫秒)
            acc_data: 加速度数据 [x, y, z]
            gyro_data: 角速度数据 [x, y, z]
        """
        with self.lock:
            self.timestamp_buffer.append(timestamp)
            self.acc_buffer.append(acc_data)
            self.gyro_buffer.append(gyro_data)
            
            # 当累积足够数据后，将数据放入处理队列
            if len(self.acc_buffer) >= self.window_size and len(self.acc_buffer) % self.step_size == 0:
                self._queue_data_for_processing()
    
    def add_pressure_data(self, timestamp, pressure_data):
        """
        添加足压数据到缓冲区
        
        Args:
            timestamp: 时间戳 (毫秒)
            pressure_data: 足压数据 [前脚掌, 中脚掌, 后脚掌, 外侧]
        """
        with self.lock:
            # 确保时间戳对齐
            while len(self.timestamp_buffer) > len(self.pressure_buffer):
                self.pressure_buffer.append(pressure_data)
    
    def get_latest_results(self):
        """
        获取最新分析结果
        
        Returns:
            最新的分析结果字典
        """
        return self.latest_results.copy()
    
    def get_buffered_data(self):
        """
        获取缓冲区中的数据
        
        Returns:
            缓冲区数据字典
        """
        with self.lock:
            return {
                'timestamps': list(self.timestamp_buffer),
                'acceleration': list(self.acc_buffer),
                'gyroscope': list(self.gyro_buffer),
                'pressure': list(self.pressure_buffer)
            }
    
    def clear_buffers(self):
        """
        清空所有数据缓冲区
        """
        with self.lock:
            self.acc_buffer.clear()
            self.gyro_buffer.clear()
            self.pressure_buffer.clear()
            self.timestamp_buffer.clear()
    
    def _queue_data_for_processing(self):
        """
        将窗口数据放入处理队列
        """
        # 创建数据窗口的副本
        acc_window = np.array(list(self.acc_buffer)[-self.window_size:])
        gyro_window = np.array(list(self.gyro_buffer)[-self.window_size:])
        
        # 创建足压数据副本（如果有）
        if len(self.pressure_buffer) >= self.window_size:
            pressure_window = np.array(list(self.pressure_buffer)[-self.window_size:])
        else:
            # 如果足压数据不足，使用零填充
            pressure_window = np.zeros((self.window_size, 4))
        
        # 将数据放入处理队列
        try:
            self.processing_queue.put(
                {
                    'acc': acc_window,
                    'gyro': gyro_window,
                    'pressure': pressure_window
                },
                block=False
            )
        except queue.Full:
            print("处理队列已满，丢弃当前数据窗口")
    
    def _process_data_loop(self):
        """
        数据处理线程主循环
        """
        while self.is_running:
            try:
                # 尝试从队列获取数据窗口
                data = self.processing_queue.get(block=True, timeout=0.1)
                
                # 处理数据
                result = self._process_data_window(data)
                
                # 更新最新结果
                if result:
                    self.latest_results = result
                    
                    # 将结果放入结果队列
                    try:
                        self.result_queue.put(result, block=False)
                    except queue.Full:
                        # 如果结果队列满了，移除最旧的结果
                        try:
                            self.result_queue.get_nowait()
                            self.result_queue.put(result, block=False)
                        except:
                            pass
                
                # 标记任务完成
                self.processing_queue.task_done()
            
            except queue.Empty:
                # 队列为空，等待新数据
                time.sleep(0.01)
            except Exception as e:
                print(f"数据处理出错: {e}")
    
    def _process_data_window(self, data):
        """
        处理单个数据窗口
        
        Args:
            data: 包含加速度、角速度和足压数据的字典
            
        Returns:
            处理结果字典
        """
        # 解包数据
        acc_data = data['acc']
        gyro_data = data['gyro']
        pressure_data = data['pressure']
        
        try:
            # 1. 应用滤波器
            acc_filtered = lowpass_filter(acc_data, self.acc_lowpass_cutoff, self.sampling_rate)
            gyro_filtered = lowpass_filter(gyro_data, self.gyro_lowpass_cutoff, self.sampling_rate)
            
            # 对垂直方向加速度应用中值滤波去除尖峰
            acc_filtered[:, 2] = median_filter(acc_filtered[:, 2], kernel_size=5)
            
            # 2. 特征提取
            imu_features = extract_features(acc_filtered, gyro_filtered)
            pressure_features = extract_pressure_features(pressure_data)
            
            # 3. 模型推理
            gait_result = self.model.infer(imu_features)
            pressure_result = self.model.analyze_pressure(pressure_features)
            
            # 4. 生成建议
            recommendations = self.model.generate_recommendations(gait_result, pressure_result)
            
            # 返回处理结果
            return {
                'gait': gait_result,
                'pressure': pressure_result,
                'recommendations': recommendations,
                'timestamp': time.time() * 1000  # 当前时间戳（毫秒）
            }
        
        except Exception as e:
            print(f"数据窗口处理失败: {e}")
            return None
    
    def get_latest_cadence(self):
        """
        获取最新步频
        
        Returns:
            步频值或None
        """
        if self.latest_results['gait'] is not None:
            return self.latest_results['gait']['features']['cadence']
        return None
    
    def get_latest_posture_score(self):
        """
        获取最新姿态评分
        
        Returns:
            姿态评分或None
        """
        if self.latest_results['gait'] is not None:
            return self.latest_results['gait']['posture_score']
        return None
    
    def get_latest_gait_phase(self):
        """
        获取最新步态相位
        
        Returns:
            步态相位或None
        """
        if self.latest_results['gait'] is not None:
            return self.latest_results['gait']['gait_phase']
        return None