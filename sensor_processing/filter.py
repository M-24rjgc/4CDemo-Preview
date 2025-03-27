"""
滤波器模块

包含用于传感器数据滤波的各种算法
"""
import numpy as np
from scipy import signal

def lowpass_filter(data, cutoff, fs, order=4):
    """
    低通滤波器
    
    Args:
        data: 需要滤波的数据，形状为(n_samples, n_features)的numpy数组
        cutoff: 截止频率(Hz)
        fs: 采样频率(Hz)
        order: 滤波器阶数
        
    Returns:
        滤波后的数据
    """
    nyq = 0.5 * fs  # 奈奎斯特频率
    normal_cutoff = cutoff / nyq
    
    # 设计巴特沃斯低通滤波器
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    
    # 应用滤波器
    if len(data.shape) == 1:
        # 一维数据
        filtered_data = signal.filtfilt(b, a, data)
    else:
        # 多维数据，对每个维度分别滤波
        filtered_data = np.zeros_like(data)
        for i in range(data.shape[1]):
            filtered_data[:, i] = signal.filtfilt(b, a, data[:, i])
    
    return filtered_data

def highpass_filter(data, cutoff, fs, order=4):
    """
    高通滤波器
    
    Args:
        data: 需要滤波的数据，形状为(n_samples, n_features)的numpy数组
        cutoff: 截止频率(Hz)
        fs: 采样频率(Hz)
        order: 滤波器阶数
        
    Returns:
        滤波后的数据
    """
    nyq = 0.5 * fs  # 奈奎斯特频率
    normal_cutoff = cutoff / nyq
    
    # 设计巴特沃斯高通滤波器
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    
    # 应用滤波器
    if len(data.shape) == 1:
        # 一维数据
        filtered_data = signal.filtfilt(b, a, data)
    else:
        # 多维数据，对每个维度分别滤波
        filtered_data = np.zeros_like(data)
        for i in range(data.shape[1]):
            filtered_data[:, i] = signal.filtfilt(b, a, data[:, i])
    
    return filtered_data

def bandpass_filter(data, lowcut, highcut, fs, order=4):
    """
    带通滤波器
    
    Args:
        data: 需要滤波的数据，形状为(n_samples, n_features)的numpy数组
        lowcut: 低截止频率(Hz)
        highcut: 高截止频率(Hz)
        fs: 采样频率(Hz)
        order: 滤波器阶数
        
    Returns:
        滤波后的数据
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    
    # 设计巴特沃斯带通滤波器
    b, a = signal.butter(order, [low, high], btype='band', analog=False)
    
    # 应用滤波器
    if len(data.shape) == 1:
        # 一维数据
        filtered_data = signal.filtfilt(b, a, data)
    else:
        # 多维数据，对每个维度分别滤波
        filtered_data = np.zeros_like(data)
        for i in range(data.shape[1]):
            filtered_data[:, i] = signal.filtfilt(b, a, data[:, i])
    
    return filtered_data

def median_filter(data, kernel_size=5):
    """
    中值滤波器，用于去除尖峰噪声
    
    Args:
        data: 需要滤波的数据，形状为(n_samples, n_features)的numpy数组
        kernel_size: 滤波器核大小
        
    Returns:
        滤波后的数据
    """
    if len(data.shape) == 1:
        # 一维数据
        filtered_data = signal.medfilt(data, kernel_size=kernel_size)
    else:
        # 多维数据，对每个维度分别滤波
        filtered_data = np.zeros_like(data)
        for i in range(data.shape[1]):
            filtered_data[:, i] = signal.medfilt(data[:, i], kernel_size=kernel_size)
    
    return filtered_data

def moving_average_filter(data, window_size=5):
    """
    移动平均滤波器
    
    Args:
        data: 需要滤波的数据，形状为(n_samples, n_features)的numpy数组
        window_size: 窗口大小
        
    Returns:
        滤波后的数据
    """
    # 创建卷积窗口
    window = np.ones(window_size) / window_size
    
    if len(data.shape) == 1:
        # 一维数据
        filtered_data = np.convolve(data, window, mode='same')
    else:
        # 多维数据，对每个维度分别滤波
        filtered_data = np.zeros_like(data)
        for i in range(data.shape[1]):
            filtered_data[:, i] = np.convolve(data[:, i], window, mode='same')
    
    return filtered_data

def kalman_filter_1d(data, process_variance=1e-5, measurement_variance=1e-1):
    """
    一维卡尔曼滤波器
    
    Args:
        data: 需要滤波的一维数据
        process_variance: 过程噪声方差
        measurement_variance: 测量噪声方差
        
    Returns:
        滤波后的数据
    """
    # 初始化
    n = len(data)
    filtered_data = np.zeros(n)
    
    # 初始状态
    x_hat = data[0]  # 初始估计
    p = 1.0  # 初始协方差
    
    # 卡尔曼滤波
    for i in range(n):
        # 预测
        x_hat_minus = x_hat
        p_minus = p + process_variance
        
        # 更新
        k = p_minus / (p_minus + measurement_variance)  # 卡尔曼增益
        x_hat = x_hat_minus + k * (data[i] - x_hat_minus)
        p = (1 - k) * p_minus
        
        filtered_data[i] = x_hat
    
    return filtered_data