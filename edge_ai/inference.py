"""
边缘AI推理模块

负责加载TensorFlow Lite模型并执行推理
"""
import os
import numpy as np
import tensorflow as tf
import time

class GaitAnalysisModel:
    """
    步态分析模型类
    
    用于加载TensorFlow Lite模型并执行步态分析推理
    """
    
    def __init__(self, model_path=None):
        """
        初始化步态分析模型
        
        Args:
            model_path: TensorFlow Lite模型路径，如果为None，则使用默认模型
        """
        if model_path is None:
            # 使用默认模型路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, 'models', 'gait_model.tflite')
        
        self.model_path = model_path
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.is_initialized = False
        
        # 加载模型
        self._load_model()
    
    def _load_model(self):
        """
        加载TensorFlow Lite模型
        """
        try:
            # 加载模型
            self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            
            # 获取输入和输出详情
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            # 输出模型信息
            print(f"模型加载成功: {self.model_path}")
            print(f"输入形状: {self.input_details[0]['shape']}")
            print(f"输出形状: {self.output_details[0]['shape']}")
            
            self.is_initialized = True
        
        except Exception as e:
            print(f"模型加载失败: {e}")
            self.is_initialized = False
    
    def preprocess_features(self, features):
        """
        预处理特征数据，将特征字典转换为模型输入格式
        
        Args:
            features: 特征字典，由特征提取器生成
            
        Returns:
            处理后的特征数据，形状为模型输入要求的形状
        """
        if not self.is_initialized:
            print("模型未初始化，无法预处理特征")
            return None
        
        # 获取模型输入形状
        input_shape = self.input_details[0]['shape']
        
        # 创建特征向量
        feature_vector = []
        
        # 添加加速度特征
        feature_vector.extend(features['acc_mean'])
        feature_vector.extend(features['acc_std'])
        feature_vector.extend(features['acc_rms'])
        
        # 添加角速度特征
        feature_vector.extend(features['gyro_mean'])
        feature_vector.extend(features['gyro_std'])
        feature_vector.extend(features['gyro_rms'])
        
        # 添加合加速度和合角速度特征
        feature_vector.extend([
            features['acc_mag_mean'],
            features['acc_mag_std'],
            features['gyro_mag_mean'],
            features['gyro_mag_std']
        ])
        
        # 添加频域特征
        feature_vector.extend([
            features['acc_dominant_freq_x'],
            features['acc_dominant_freq_y'],
            features['acc_dominant_freq_z'],
            features['gyro_dominant_freq_x'],
            features['gyro_dominant_freq_y'],
            features['gyro_dominant_freq_z']
        ])
        
        # 添加步态特征
        feature_vector.extend([
            features['cadence'],
            features['vertical_oscillation'],
            features['impact_force']
        ])
        
        # 添加相关性特征
        feature_vector.extend([
            features['acc_correlation_xy'],
            features['acc_correlation_xz'],
            features['acc_correlation_yz'],
            features['acc_gyro_correlation_x'],
            features['acc_gyro_correlation_y'],
            features['acc_gyro_correlation_z']
        ])
        
        # 转换为numpy数组
        feature_vector = np.array(feature_vector, dtype=np.float32)
        
        # 根据模型输入形状调整
        if len(input_shape) == 2:
            # 单个样本输入，增加batch维度
            feature_vector = feature_vector.reshape(1, -1)
        elif len(input_shape) == 3:
            # 时序数据输入，增加序列和batch维度
            feature_vector = feature_vector.reshape(1, 1, -1)
        
        # 特征缩放（假设模型期望的输入范围是[-1, 1]）
        # 注意：在实际应用中，应该使用与训练时相同的缩放方法
        # feature_vector = feature_vector / np.max(np.abs(feature_vector))
        
        return feature_vector
    
    def infer(self, features):
        """
        执行步态分析推理
        
        Args:
            features: 特征字典，由特征提取器生成
            
        Returns:
            推理结果字典，包含步态相位和姿态评分
        """
        if not self.is_initialized:
            print("模型未初始化，无法执行推理")
            return None
        
        # 预处理特征
        input_data = self.preprocess_features(features)
        if input_data is None:
            return None
        
        try:
            # 设置输入张量
            self.interpreter.set_tensor(
                self.input_details[0]['index'],
                input_data
            )
            
            # 记录推理开始时间
            start_time = time.time()
            
            # 执行推理
            self.interpreter.invoke()
            
            # 记录推理结束时间
            end_time = time.time()
            inference_time = (end_time - start_time) * 1000  # 毫秒
            
            # 获取输出张量
            # 假设输出有两个：步态相位和姿态评分
            if len(self.output_details) >= 2:
                gait_phase = self.interpreter.get_tensor(self.output_details[0]['index'])
                posture_score = self.interpreter.get_tensor(self.output_details[1]['index'])
                
                # 后处理结果
                gait_phase = gait_phase.flatten()
                posture_score = float(posture_score.flatten()[0])
                
                # 将步态相位概率转换为标签
                phase_labels = ['stance', 'swing']
                phase_idx = np.argmax(gait_phase)
                phase_label = phase_labels[phase_idx]
                phase_confidence = float(gait_phase[phase_idx])
                
                # 确保姿态评分在0-100范围内
                posture_score = max(0, min(100, posture_score * 100))
            else:
                # 如果模型只有一个输出，假设是姿态评分
                output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
                
                # 后处理结果
                output_data = output_data.flatten()
                posture_score = float(output_data[0]) * 100  # 缩放到0-100
                phase_label = None
                phase_confidence = None
            
            # 返回结果
            result = {
                'posture_score': posture_score,
                'gait_phase': phase_label,
                'phase_confidence': phase_confidence,
                'inference_time_ms': inference_time,
                'features': {
                    'cadence': features['cadence'],
                    'vertical_oscillation': features['vertical_oscillation'],
                    'impact_force': features['impact_force']
                }
            }
            
            return result
        
        except Exception as e:
            print(f"推理执行失败: {e}")
            return None
    
    def analyze_pressure(self, pressure_features):
        """
        分析足压数据
        
        Args:
            pressure_features: 足压特征字典
            
        Returns:
            足压分析结果
        """
        # 计算前后足压比
        forefoot_hindfoot_ratio = pressure_features['forefoot_hindfoot_ratio']
        
        # 根据前后足压比判断着地类型
        if forefoot_hindfoot_ratio > 1.5:
            foot_strike_type = 'forefoot'  # 前脚掌着地
        elif forefoot_hindfoot_ratio < 0.7:
            foot_strike_type = 'rearfoot'  # 后脚掌着地
        else:
            foot_strike_type = 'midfoot'  # 中脚掌着地
        
        # 计算内外侧压力平衡，判断是否过度内翻或外翻
        medial_lateral_ratio = pressure_features['medial_lateral_ratio']
        if medial_lateral_ratio > 2.0:
            pronation_type = 'overpronation'  # 过度内翻
        elif medial_lateral_ratio < 1.0:
            pronation_type = 'supination'  # 外翻
        else:
            pronation_type = 'neutral'  # 中性
        
        # 返回足压分析结果
        result = {
            'foot_strike_type': foot_strike_type,
            'pronation_type': pronation_type,
            'pressure_distribution': {
                'forefoot': pressure_features['forefoot_percentage'] * 100,
                'midfoot': pressure_features['midfoot_percentage'] * 100,
                'hindfoot': pressure_features['hindfoot_percentage'] * 100,
                'lateral': pressure_features['lateral_percentage'] * 100
            }
        }
        
        return result
    
    def generate_recommendations(self, gait_result, pressure_result):
        """
        基于分析结果生成改进建议
        
        Args:
            gait_result: 步态分析结果
            pressure_result: 足压分析结果
            
        Returns:
            改进建议列表
        """
        recommendations = []
        
        # 步频建议
        cadence = gait_result['features']['cadence']
        if cadence < 160:
            recommendations.append({
                'type': 'cadence',
                'title': '增加步频',
                'description': '您的步频较低，可以尝试增加步频至170-180步/分钟以提高跑步效率。'
            })
        elif cadence > 200:
            recommendations.append({
                'type': 'cadence',
                'title': '适当降低步频',
                'description': '您的步频较高，可以尝试稍微减小步频并增加步幅，以找到更舒适的节奏。'
            })
        
        # 垂直振幅建议
        oscillation = gait_result['features']['vertical_oscillation']
        if oscillation > 10.0:  # 大于10厘米
            recommendations.append({
                'type': 'oscillation',
                'title': '减小垂直振幅',
                'description': '您的垂直振幅较大，容易消耗额外能量。尝试减少上下起伏，保持重心稳定向前推进。'
            })
        
        # 冲击力建议
        impact = gait_result['features']['impact_force']
        if impact > 3.5:  # 大于3.5g
            recommendations.append({
                'type': 'impact',
                'title': '减少着地冲击',
                'description': '您的着地冲击力较大，可能增加受伤风险。尝试改进着地方式，增强核心稳定性。'
            })
        
        # 足部着地方式建议
        foot_strike = pressure_result['foot_strike_type']
        if foot_strike == 'rearfoot':
            recommendations.append({
                'type': 'foot_strike',
                'title': '优化足部着地方式',
                'description': '您主要使用后脚跟着地，可能会增加膝关节压力。尝试渐进式地调整为中脚掌着地。'
            })
        elif foot_strike == 'forefoot':
            recommendations.append({
                'type': 'foot_strike',
                'title': '平衡足部着地方式',
                'description': '您主要使用前脚掌着地，这对小腿肌肉要求较高。在长距离跑步中可能导致过度疲劳，适当调整为中脚掌着地。'
            })
        
        # 足部内外翻建议
        pronation = pressure_result['pronation_type']
        if pronation == 'overpronation':
            recommendations.append({
                'type': 'pronation',
                'title': '控制过度内翻',
                'description': '您的足部存在过度内翻现象，考虑使用支撑型跑鞋或足部稳定训练来改善。'
            })
        elif pronation == 'supination':
            recommendations.append({
                'type': 'pronation',
                'title': '改善足部外翻',
                'description': '您的足部倾向于外翻，考虑使用缓震型跑鞋和提高足部灵活性的练习。'
            })
        
        return recommendations