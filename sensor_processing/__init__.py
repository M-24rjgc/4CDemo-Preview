"""
传感器处理模块初始化文件
"""

from sensor_processing.filter import (
    lowpass_filter, highpass_filter, bandpass_filter, 
    median_filter, moving_average_filter, kalman_filter_1d
)

from sensor_processing.feature_extractor import (
    extract_features, extract_pressure_features,
    estimate_cadence, estimate_vertical_oscillation, calculate_impact_force
)

from sensor_processing.data_processor import DataProcessor

__all__ = [
    'lowpass_filter', 'highpass_filter', 'bandpass_filter',
    'median_filter', 'moving_average_filter', 'kalman_filter_1d',
    'extract_features', 'extract_pressure_features',
    'estimate_cadence', 'estimate_vertical_oscillation', 'calculate_impact_force',
    'DataProcessor'
]

__version__ = '1.0.0'