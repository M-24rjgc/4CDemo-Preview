"""
特征提取模块

从处理后的传感器数据中提取有用特征，以供模型推理使用
"""
import numpy as np
from scipy import stats, signal

def extract_features(acc_data, gyro_data):
    """
    从IMU数据中提取特征
    
    Args:
        acc_data: 形状为(n_samples, 3)的加速度数据 [x, y, z]
        gyro_data: 形状为(n_samples, 3)的角速度数据 [x, y, z]
        
    Returns:
        提取的特征字典
    """
    features = {}
    
    # ===== 时域特征 =====
    # 加速度统计特征
    features['acc_mean'] = np.mean(acc_data, axis=0)  # 均值 (3,)
    features['acc_std'] = np.std(acc_data, axis=0)   # 标准差 (3,)
    features['acc_min'] = np.min(acc_data, axis=0)   # 最小值 (3,)
    features['acc_max'] = np.max(acc_data, axis=0)   # 最大值 (3,)
    features['acc_range'] = features['acc_max'] - features['acc_min']  # 范围 (3,)
    features['acc_rms'] = np.sqrt(np.mean(np.square(acc_data), axis=0))  # 均方根 (3,)
    features['acc_kurtosis'] = stats.kurtosis(acc_data, axis=0)  # 峰度 (3,)
    features['acc_skewness'] = stats.skew(acc_data, axis=0)  # 偏度 (3,)
    
    # 角速度统计特征
    features['gyro_mean'] = np.mean(gyro_data, axis=0)  # 均值 (3,)
    features['gyro_std'] = np.std(gyro_data, axis=0)   # 标准差 (3,)
    features['gyro_min'] = np.min(gyro_data, axis=0)   # 最小值 (3,)
    features['gyro_max'] = np.max(gyro_data, axis=0)   # 最大值 (3,)
    features['gyro_range'] = features['gyro_max'] - features['gyro_min']  # 范围 (3,)
    features['gyro_rms'] = np.sqrt(np.mean(np.square(gyro_data), axis=0))  # 均方根 (3,)
    
    # 计算合加速度和合角速度
    acc_mag = np.sqrt(np.sum(np.square(acc_data), axis=1))  # 合加速度
    gyro_mag = np.sqrt(np.sum(np.square(gyro_data), axis=1))  # 合角速度
    
    # 合加速度特征
    features['acc_mag_mean'] = np.mean(acc_mag)
    features['acc_mag_std'] = np.std(acc_mag)
    features['acc_mag_min'] = np.min(acc_mag)
    features['acc_mag_max'] = np.max(acc_mag)
    
    # 合角速度特征
    features['gyro_mag_mean'] = np.mean(gyro_mag)
    features['gyro_mag_std'] = np.std(gyro_mag)
    features['gyro_mag_min'] = np.min(gyro_mag)
    features['gyro_mag_max'] = np.max(gyro_mag)
    
    # ===== 频域特征 =====
    # 计算加速度的FFT
    acc_fft_x = np.abs(np.fft.fft(acc_data[:, 0]))[:len(acc_data)//2]
    acc_fft_y = np.abs(np.fft.fft(acc_data[:, 1]))[:len(acc_data)//2]
    acc_fft_z = np.abs(np.fft.fft(acc_data[:, 2]))[:len(acc_data)//2]
    
    # 计算角速度的FFT
    gyro_fft_x = np.abs(np.fft.fft(gyro_data[:, 0]))[:len(gyro_data)//2]
    gyro_fft_y = np.abs(np.fft.fft(gyro_data[:, 1]))[:len(gyro_data)//2]
    gyro_fft_z = np.abs(np.fft.fft(gyro_data[:, 2]))[:len(gyro_data)//2]
    
    # 计算频域能量
    features['acc_fft_energy_x'] = np.sum(np.square(acc_fft_x))
    features['acc_fft_energy_y'] = np.sum(np.square(acc_fft_y))
    features['acc_fft_energy_z'] = np.sum(np.square(acc_fft_z))
    
    features['gyro_fft_energy_x'] = np.sum(np.square(gyro_fft_x))
    features['gyro_fft_energy_y'] = np.sum(np.square(gyro_fft_y))
    features['gyro_fft_energy_z'] = np.sum(np.square(gyro_fft_z))
    
    # 主频率（对应振幅最大的频率）
    freq_bins = np.fft.fftfreq(len(acc_data), d=1.0/200)[:len(acc_data)//2]  # 假设采样率为200Hz
    
    # 加速度主频率
    features['acc_dominant_freq_x'] = freq_bins[np.argmax(acc_fft_x)]
    features['acc_dominant_freq_y'] = freq_bins[np.argmax(acc_fft_y)]
    features['acc_dominant_freq_z'] = freq_bins[np.argmax(acc_fft_z)]
    
    # 角速度主频率
    features['gyro_dominant_freq_x'] = freq_bins[np.argmax(gyro_fft_x)]
    features['gyro_dominant_freq_y'] = freq_bins[np.argmax(gyro_fft_y)]
    features['gyro_dominant_freq_z'] = freq_bins[np.argmax(gyro_fft_z)]
    
    # ===== 步态特征 =====
    # 估计步频
    features['cadence'] = estimate_cadence(acc_data[:, 2])  # 使用垂直方向加速度估计步频
    
    # 估计垂直振幅
    features['vertical_oscillation'] = estimate_vertical_oscillation(acc_data[:, 2])
    
    # 计算冲击力指标
    features['impact_force'] = calculate_impact_force(acc_data[:, 2])
    
    # ===== 互相关特征 =====
    # 计算各轴之间的相关性
    features['acc_correlation_xy'] = np.corrcoef(acc_data[:, 0], acc_data[:, 1])[0, 1]
    features['acc_correlation_xz'] = np.corrcoef(acc_data[:, 0], acc_data[:, 2])[0, 1]
    features['acc_correlation_yz'] = np.corrcoef(acc_data[:, 1], acc_data[:, 2])[0, 1]
    
    features['gyro_correlation_xy'] = np.corrcoef(gyro_data[:, 0], gyro_data[:, 1])[0, 1]
    features['gyro_correlation_xz'] = np.corrcoef(gyro_data[:, 0], gyro_data[:, 2])[0, 1]
    features['gyro_correlation_yz'] = np.corrcoef(gyro_data[:, 1], gyro_data[:, 2])[0, 1]
    
    # 计算角速度和加速度的关系
    features['acc_gyro_correlation_x'] = np.corrcoef(acc_data[:, 0], gyro_data[:, 0])[0, 1]
    features['acc_gyro_correlation_y'] = np.corrcoef(acc_data[:, 1], gyro_data[:, 1])[0, 1]
    features['acc_gyro_correlation_z'] = np.corrcoef(acc_data[:, 2], gyro_data[:, 2])[0, 1]
    
    return features

def estimate_cadence(vertical_acc, sampling_rate=200):
    """
    使用垂直加速度估计步频
    
    Args:
        vertical_acc: 垂直方向加速度数据
        sampling_rate: 采样率(Hz)
    
    Returns:
        估计的步频(步/分钟)
    """
    # 去除均值
    data = vertical_acc - np.mean(vertical_acc)
    
    # 计算自相关
    correlation = np.correlate(data, data, mode='full')
    correlation = correlation[correlation.size//2:]  # 只保留正时移部分
    
    # 寻找第一个主要峰值（排除0处的峰值）
    peaks, _ = signal.find_peaks(correlation, height=0.1*np.max(correlation), distance=sampling_rate//4)
    
    if len(peaks) < 1:
        return 0  # 未检测到步频
    
    first_peak = peaks[0]
    
    # 计算步频（步/分钟）
    cadence = (sampling_rate * 60) / first_peak
    
    # 限制步频在合理范围内
    if cadence < 100:  # 正常人步频一般不低于100步/分钟
        # 可能是检测到了两步的周期
        cadence = cadence * 2
    
    if cadence > 250:  # 正常人步频一般不超过250步/分钟
        # 可能是检测到了噪声
        return 0
    
    return cadence

def estimate_vertical_oscillation(vertical_acc, sampling_rate=200, g=9.81):
    """
    估计垂直振幅
    
    Args:
        vertical_acc: 垂直方向加速度数据
        sampling_rate: 采样率(Hz)
        g: 重力加速度(m/s^2)
        
    Returns:
        垂直振幅(cm)
    """
    # 从加速度估计速度（积分）
    # 去除均值（去除重力影响）
    acc_no_gravity = vertical_acc - np.mean(vertical_acc)
    
    # 积分求速度
    velocity = np.cumsum(acc_no_gravity) / sampling_rate
    
    # 去除速度的线性趋势
    velocity = signal.detrend(velocity)
    
    # 再次积分求位移
    displacement = np.cumsum(velocity) / sampling_rate * 100  # 转换为厘米
    
    # 计算位移的峰峰值作为振幅
    oscillation = np.max(displacement) - np.min(displacement)
    
    return oscillation

def calculate_impact_force(vertical_acc, g=9.81):
    """
    计算着地冲击力
    
    Args:
        vertical_acc: 垂直方向加速度数据
        g: 重力加速度(m/s^2)
        
    Returns:
        冲击力(g)
    """
    # 计算加速度峰值与均值的差值，除以重力加速度得到g值
    mean_acc = np.mean(vertical_acc)
    peak_acc = np.max(vertical_acc) 
    
    impact = (peak_acc - mean_acc) / g
    
    return impact

def extract_pressure_features(pressure_data):
    """
    从足压数据中提取特征
    
    Args:
        pressure_data: 形状为(n_samples, 4)的足压数据
                      [前脚掌, 中脚掌, 后脚掌, 外侧]
    
    Returns:
        提取的特征字典
    """
    features = {}
    
    # 计算各区域压力的平均值
    features['forefoot_pressure'] = np.mean(pressure_data[:, 0])
    features['midfoot_pressure'] = np.mean(pressure_data[:, 1])
    features['hindfoot_pressure'] = np.mean(pressure_data[:, 2])
    features['lateral_pressure'] = np.mean(pressure_data[:, 3])
    
    # 计算压力分布
    total_pressure = np.sum(pressure_data, axis=1)
    avg_total_pressure = np.mean(total_pressure)
    features['total_pressure'] = avg_total_pressure
    
    # 各区域所占百分比
    features['forefoot_percentage'] = features['forefoot_pressure'] / avg_total_pressure
    features['midfoot_percentage'] = features['midfoot_pressure'] / avg_total_pressure
    features['hindfoot_percentage'] = features['hindfoot_pressure'] / avg_total_pressure
    features['lateral_percentage'] = features['lateral_pressure'] / avg_total_pressure
    
    # 前后脚掌压力比
    features['forefoot_hindfoot_ratio'] = features['forefoot_pressure'] / (features['hindfoot_pressure'] + 1e-6)
    
    # 内外侧压力比
    medial_pressure = np.mean(pressure_data[:, 0] + pressure_data[:, 1] + pressure_data[:, 2])
    features['medial_lateral_ratio'] = medial_pressure / (features['lateral_pressure'] + 1e-6)
    
    # 压力变化率（标准差）
    features['pressure_std'] = np.std(pressure_data, axis=0)
    
    return features