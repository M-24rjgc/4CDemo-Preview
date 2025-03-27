#!/usr/bin/env python
"""
模型转换工具

用于将训练好的TensorFlow模型转换为TensorFlow Lite格式，以便在边缘设备上运行
"""
import os
import sys
import argparse
import numpy as np
import tensorflow as tf

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='将TensorFlow模型转换为TensorFlow Lite格式')
    parser.add_argument('--input', '-i', required=True, help='输入模型文件路径 (.h5 或 SavedModel目录)')
    parser.add_argument('--output', '-o', required=True, help='输出TFLite模型文件路径')
    parser.add_argument('--quantize', '-q', action='store_true', help='是否进行int8量化')
    parser.add_argument('--optimize', choices=['none', 'size', 'latency'], default='latency', 
                      help='优化目标: none=不优化, size=优化大小, latency=优化延迟')
    return parser.parse_args()

def load_model(model_path):
    """
    加载TensorFlow模型
    
    Args:
        model_path: 模型文件路径或SavedModel目录
    
    Returns:
        加载的TensorFlow模型
    """
    print(f"加载模型: {model_path}")
    
    try:
        # 尝试加载SavedModel
        if os.path.isdir(model_path):
            model = tf.saved_model.load(model_path)
            print("成功加载SavedModel格式模型")
        else:
            # 尝试加载Keras模型
            model = tf.keras.models.load_model(model_path)
            print("成功加载Keras (.h5)格式模型")
            
        return model
    except Exception as e:
        print(f"模型加载失败: {e}")
        return None

def convert_to_tflite(model, optimize_option, quantize=False):
    """
    将TensorFlow模型转换为TensorFlow Lite格式
    
    Args:
        model: TensorFlow模型
        optimize_option: 优化选项 ('none', 'size', 'latency')
        quantize: 是否进行int8量化
    
    Returns:
        TFLite模型对象
    """
    print("开始转换模型为TensorFlow Lite格式...")
    
    # 创建转换器
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # 设置优化选项
    if optimize_option == 'size':
        print("优化目标: 减小模型大小")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
    elif optimize_option == 'latency':
        print("优化目标: 减少推理延迟")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS
        ]
    
    # 如果需要量化，设置量化参数
    if quantize:
        print("应用int8量化...")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        # 定义代表性数据集用于量化校准
        def representative_dataset():
            # 这里应该使用真实的代表性数据
            # 现在使用随机数据作为示例
            for _ in range(100):
                # 根据模型输入形状调整数据生成
                input_shape = model.inputs[0].shape
                batch_size = 1
                if input_shape[0] is None:  # 批次维度
                    # 创建适配模型输入形状的随机数据
                    shape = (batch_size,) + tuple(dim if dim is not None else 10 for dim in input_shape[1:])
                    yield [np.random.uniform(-1, 1, shape).astype(np.float32)]
                else:
                    yield [np.random.uniform(-1, 1, input_shape).astype(np.float32)]
        
        converter.representative_dataset = representative_dataset
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.inference_input_type = tf.int8
        converter.inference_output_type = tf.int8
    
    # 执行转换
    tflite_model = converter.convert()
    print("模型转换完成")
    
    return tflite_model

def save_model(tflite_model, output_path):
    """
    保存TFLite模型到文件
    
    Args:
        tflite_model: TFLite模型对象
        output_path: 输出文件路径
    """
    with open(output_path, 'wb') as f:
        f.write(tflite_model)
    
    # 获取模型大小
    model_size = os.path.getsize(output_path) / 1024.0
    print(f"模型已保存: {output_path} (大小: {model_size:.2f} KB)")

def main():
    args = parse_arguments()
    
    try:
        # 检查TensorFlow版本
        print(f"TensorFlow版本: {tf.__version__}")
        
        # 加载模型
        model = load_model(args.input)
        if model is None:
            return 1
        
        # 转换模型
        tflite_model = convert_to_tflite(model, args.optimize, args.quantize)
        
        # 保存模型
        save_model(tflite_model, args.output)
        
        print("模型转换成功!")
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())