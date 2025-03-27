#!/usr/bin/env python
"""
数据解码工具

用于将设备原始二进制数据转换为CSV或JSON格式
"""
import os
import sys
import argparse
import struct
import json
import csv
import numpy as np
from datetime import datetime

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='解码IMU和足压传感器数据')
    parser.add_argument('--input', '-i', required=True, help='输入二进制数据文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出文件路径')
    parser.add_argument('--format', '-f', choices=['csv', 'json'], default='csv', help='输出格式 (csv 或 json)')
    return parser.parse_args()

def decode_binary_data(binary_file):
    """
    解码二进制数据文件
    
    数据格式:
    - 时间戳 (uint32): 毫秒级Unix时间戳
    - 加速度 (3x float): X, Y, Z轴加速度，单位m/s²
    - 角速度 (3x float): X, Y, Z轴角速度，单位rad/s
    - 足压 (4x float): 四个足压传感器的值，范围0-1
    
    Returns:
        解码后的数据字典
    """
    data = {
        'timestamps': [],
        'acceleration': [],
        'gyroscope': [],
        'pressure': []
    }
    
    # 数据包大小：4字节时间戳 + 3x4字节加速度 + 3x4字节角速度 + 4x4字节足压 = 40字节
    packet_size = 40
    
    with open(binary_file, 'rb') as f:
        while True:
            packet = f.read(packet_size)
            if not packet or len(packet) < packet_size:
                break
                
            # 解析时间戳 (uint32)
            timestamp_ms = struct.unpack('<I', packet[0:4])[0]
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000.0).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
            
            # 解析加速度 (3x float)
            acc_x = struct.unpack('<f', packet[4:8])[0]
            acc_y = struct.unpack('<f', packet[8:12])[0]
            acc_z = struct.unpack('<f', packet[12:16])[0]
            
            # 解析角速度 (3x float)
            gyro_x = struct.unpack('<f', packet[16:20])[0]
            gyro_y = struct.unpack('<f', packet[20:24])[0]
            gyro_z = struct.unpack('<f', packet[24:28])[0]
            
            # 解析足压 (4x float)
            pressure_1 = struct.unpack('<f', packet[28:32])[0]
            pressure_2 = struct.unpack('<f', packet[32:36])[0]
            pressure_3 = struct.unpack('<f', packet[36:40])[0]
            pressure_4 = struct.unpack('<f', packet[40:44])[0] if len(packet) >= 44 else 0
            
            # 存储解析后的数据
            data['timestamps'].append(timestamp)
            data['acceleration'].append([acc_x, acc_y, acc_z])
            data['gyroscope'].append([gyro_x, gyro_y, gyro_z])
            data['pressure'].append([pressure_1, pressure_2, pressure_3, pressure_4])
    
    # 生成步态相位标签（实际应用中应该使用模型推理）
    data['gait_labels'] = estimate_gait_phase(data['acceleration'], data['gyroscope'])
    
    return data

def estimate_gait_phase(acceleration_data, gyroscope_data):
    """
    基于简单规则估计步态相位
    
    实际应用中应使用机器学习模型进行更准确的预测
    
    Args:
        acceleration_data: 加速度数据列表
        gyroscope_data: 陀螺仪数据列表
        
    Returns:
        步态相位标签列表，每个时间点对应的相位标签：'stance'或'swing'
    """
    # 提取垂直方向加速度
    vertical_acc = [acc[2] for acc in acceleration_data]
    
    # 计算加速度平均值作为阈值
    threshold = np.mean(vertical_acc) + 0.5 * np.std(vertical_acc)
    
    # 根据简单规则判断步态相位
    phases = []
    for acc in vertical_acc:
        if acc > threshold:
            phases.append('swing')
        else:
            phases.append('stance')
    
    return phases

def save_as_csv(data, output_file):
    """将数据保存为CSV格式"""
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # 写入表头
        header = ['timestamp', 'acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z',
                  'pressure_1', 'pressure_2', 'pressure_3', 'pressure_4', 'gait_phase']
        writer.writerow(header)
        
        # 写入数据行
        for i in range(len(data['timestamps'])):
            row = [
                data['timestamps'][i],
                data['acceleration'][i][0],
                data['acceleration'][i][1],
                data['acceleration'][i][2],
                data['gyroscope'][i][0],
                data['gyroscope'][i][1],
                data['gyroscope'][i][2],
                data['pressure'][i][0],
                data['pressure'][i][1],
                data['pressure'][i][2],
                data['pressure'][i][3],
                data['gait_labels'][i]
            ]
            writer.writerow(row)
    
    print(f"数据已保存为CSV格式: {output_file}")

def save_as_json(data, output_file):
    """将数据保存为JSON格式"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"数据已保存为JSON格式: {output_file}")

def main():
    args = parse_arguments()
    
    try:
        print(f"正在解码数据文件: {args.input}")
        data = decode_binary_data(args.input)
        
        # 根据指定格式保存数据
        if args.format == 'csv':
            save_as_csv(data, args.output)
        else:
            save_as_json(data, args.output)
            
        print(f"共处理 {len(data['timestamps'])} 条数据记录")
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())