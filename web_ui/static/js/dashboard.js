/**
 * 中长跑实时指导系统 - 仪表盘JavaScript文件
 * 负责实时数据可视化和交互
 */

// 全局变量
let isCollecting = false;
let updateInterval;
let charts = {};
let dataHistory = {
    timestamps: [],
    acceleration: [],
    gyroscope: [],
    pressure: [],
    gaitPhase: [],
    postureScore: []
};

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化图表
    initCharts();
    
    // 绑定按钮事件
    document.getElementById('startBtn').addEventListener('click', startDataCollection);
    document.getElementById('stopBtn').addEventListener('click', stopDataCollection);
    document.getElementById('exportBtn').addEventListener('click', exportData);
    
    // 初始化一次数据更新，显示初始状态
    updateDashboard();
});

/**
 * 初始化所有图表
 */
function initCharts() {
    // 初始化姿态评分仪表盘
    charts.scoreGauge = echarts.init(document.getElementById('scoreGauge'));
    const scoreGaugeOption = {
        series: [{
            type: 'gauge',
            startAngle: 180,
            endAngle: 0,
            min: 0,
            max: 100,
            splitNumber: 10,
            axisLine: {
                lineStyle: {
                    width: 30,
                    color: [
                        [0.3, '#ff4500'],
                        [0.7, '#ffcc00'],
                        [1, '#5cb85c']
                    ]
                }
            },
            pointer: {
                itemStyle: {
                    color: 'auto'
                }
            },
            axisTick: {
                distance: -30,
                length: 8,
                lineStyle: {
                    color: '#fff',
                    width: 2
                }
            },
            splitLine: {
                distance: -30,
                length: 30,
                lineStyle: {
                    color: '#fff',
                    width: 4
                }
            },
            axisLabel: {
                color: 'auto',
                distance: -40,
                fontSize: 14
            },
            detail: {
                valueAnimation: true,
                formatter: '{value}',
                color: 'auto',
                fontSize: 30,
                offsetCenter: [0, '30%']
            },
            data: [{
                value: 85,
                name: '姿态评分',
                title: {
                    offsetCenter: [0, '70%']
                }
            }]
        }]
    };
    charts.scoreGauge.setOption(scoreGaugeOption);

    // 初始化步态相位饼图
    charts.phasePie = echarts.init(document.getElementById('phasePieChart'));
    const phasePieOption = {
        tooltip: {
            trigger: 'item'
        },
        series: [{
            type: 'pie',
            radius: '70%',
            data: [
                { value: 60, name: '支撑相', itemStyle: { color: '#5cb85c' } },
                { value: 40, name: '摆动相', itemStyle: { color: '#5bc0de' } }
            ],
            label: {
                show: false
            }
        }]
    };
    charts.phasePie.setOption(phasePieOption);

    // 初始化加速度图表
    charts.accChart = echarts.init(document.getElementById('accChart'));
    const accChartOption = {
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['X轴', 'Y轴', 'Z轴']
        },
        xAxis: {
            type: 'time',
            axisLabel: {
                formatter: '{HH}:{mm}:{ss}'
            }
        },
        yAxis: {
            type: 'value',
            name: '加速度 (m/s²)'
        },
        series: [{
            name: 'X轴',
            type: 'line',
            showSymbol: false,
            data: [],
            lineStyle: { width: 1 }
        }, {
            name: 'Y轴',
            type: 'line',
            showSymbol: false,
            data: [],
            lineStyle: { width: 1 }
        }, {
            name: 'Z轴',
            type: 'line',
            showSymbol: false,
            data: [],
            lineStyle: { width: 1 }
        }]
    };
    charts.accChart.setOption(accChartOption);

    // 初始化角速度图表
    charts.gyroChart = echarts.init(document.getElementById('gyroChart'));
    const gyroChartOption = {
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['X轴', 'Y轴', 'Z轴']
        },
        xAxis: {
            type: 'time',
            axisLabel: {
                formatter: '{HH}:{mm}:{ss}'
            }
        },
        yAxis: {
            type: 'value',
            name: '角速度 (rad/s)'
        },
        series: [{
            name: 'X轴',
            type: 'line',
            showSymbol: false,
            data: [],
            lineStyle: { width: 1 }
        }, {
            name: 'Y轴',
            type: 'line',
            showSymbol: false,
            data: [],
            lineStyle: { width: 1 }
        }, {
            name: 'Z轴',
            type: 'line',
            showSymbol: false,
            data: [],
            lineStyle: { width: 1 }
        }]
    };
    charts.gyroChart.setOption(gyroChartOption);

    // 初始化足压图表
    charts.pressureChart = echarts.init(document.getElementById('pressureChart'));
    const pressureChartOption = {
        tooltip: {
            trigger: 'item'
        },
        radar: {
            indicator: [
                { name: '前脚掌', max: 1 },
                { name: '中脚掌', max: 1 },
                { name: '后脚掌', max: 1 },
                { name: '外侧', max: 1 }
            ]
        },
        series: [{
            type: 'radar',
            data: [{
                value: [0.3, 0.2, 0.4, 0.1],
                name: '足压分布',
                areaStyle: {
                    color: 'rgba(54, 162, 235, 0.6)'
                }
            }]
        }]
    };
    charts.pressureChart.setOption(pressureChartOption);

    // 调整窗口大小时重绘图表
    window.addEventListener('resize', function() {
        Object.values(charts).forEach(chart => chart.resize());
    });
}

/**
 * 开始数据采集
 */
function startDataCollection() {
    if (isCollecting) return;
    
    console.log('开始数据采集');
    isCollecting = true;
    
    // 更新按钮状态
    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
    
    // 发送开始采集请求
    fetch('/api/start_collection', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        
        // 开始定时更新仪表盘
        updateInterval = setInterval(updateDashboard, 100);  // 10Hz更新率
    })
    .catch(error => {
        console.error('启动数据采集失败:', error);
        stopDataCollection();
    });
}

/**
 * 停止数据采集
 */
function stopDataCollection() {
    if (!isCollecting) return;
    
    console.log('停止数据采集');
    isCollecting = false;
    
    // 更新按钮状态
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    
    // 清除更新定时器
    clearInterval(updateInterval);
    
    // 发送停止采集请求
    fetch('/api/stop_collection', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
    })
    .catch(error => {
        console.error('停止数据采集失败:', error);
    });
}

/**
 * 导出数据
 */
function exportData() {
    console.log('导出数据');
    
    // 显示导出选项弹窗（实际应用中可以使用模态框）
    const format = window.confirm('选择导出格式：\n确定 - CSV格式\n取消 - PDF报告') ? 'csv' : 'pdf';
    
    // 发送导出请求
    fetch('/api/export_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            format: format
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log(data.message);
            // 下载文件
            window.location.href = data.file_url;
        } else {
            console.error(data.message);
        }
    })
    .catch(error => {
        console.error('导出数据失败:', error);
    });
}

/**
 * 更新仪表盘数据
 */
function updateDashboard() {
    // 从API获取实时数据
    fetch('/real-time-data')
    .then(response => response.json())
    .then(data => {
        // 更新历史数据数组
        updateDataHistory(data);
        
        // 更新姿态评分仪表盘
        updateScoreGauge(data.posture_score);
        
        // 更新步态相位显示
        updateGaitPhase(data.gait_phase);
        
        // 更新当前状态指标
        updateStatusMetrics(data);
        
        // 更新传感器图表
        updateSensorCharts(data);
        
        // 更新建议列表
        updateRecommendations(data.recommendations);
    })
    .catch(error => {
        console.error('获取实时数据失败:', error);
    });
}

/**
 * 更新数据历史记录
 */
function updateDataHistory(data) {
    const timestamp = new Date(data.timestamp);
    
    dataHistory.timestamps.push(timestamp);
    dataHistory.acceleration.push(data.acceleration);
    dataHistory.gyroscope.push(data.gyroscope);
    dataHistory.pressure.push(data.pressure);
    dataHistory.gaitPhase.push(data.gait_phase);
    dataHistory.postureScore.push(data.posture_score);
    
    // 只保留最近100个数据点
    if (dataHistory.timestamps.length > 100) {
        dataHistory.timestamps.shift();
        dataHistory.acceleration.shift();
        dataHistory.gyroscope.shift();
        dataHistory.pressure.shift();
        dataHistory.gaitPhase.shift();
        dataHistory.postureScore.shift();
    }
}

/**
 * 更新姿态评分仪表盘
 */
function updateScoreGauge(score) {
    charts.scoreGauge.setOption({
        series: [{
            data: [{
                value: score
            }]
        }]
    });
}

/**
 * 更新步态相位显示
 */
function updateGaitPhase(phase) {
    const gaitPhaseElement = document.getElementById('gaitPhase');
    
    // 更新文本和样式
    if (phase === 'stance') {
        gaitPhaseElement.textContent = '支撑相';
        gaitPhaseElement.className = 'gait-phase stance';
        
        // 更新饼图数据
        charts.phasePie.setOption({
            series: [{
                data: [
                    { value: 60, name: '支撑相', itemStyle: { color: '#5cb85c' } },
                    { value: 40, name: '摆动相', itemStyle: { color: '#5bc0de' } }
                ]
            }]
        });
    } else {
        gaitPhaseElement.textContent = '摆动相';
        gaitPhaseElement.className = 'gait-phase swing';
        
        // 更新饼图数据
        charts.phasePie.setOption({
            series: [{
                data: [
                    { value: 40, name: '支撑相', itemStyle: { color: '#5cb85c' } },
                    { value: 60, name: '摆动相', itemStyle: { color: '#5bc0de' } }
                ]
            }]
        });
    }
}

/**
 * 更新状态指标
 */
function updateStatusMetrics(data) {
    // 这里应该从特征数据中提取指标，现在只是模拟数据
    // 在实际应用中，这些值应该从后端API返回
    
    // 模拟计算步频 (假设可以从acc_z的周期性变化计算)
    const cadence = Math.round(170 + Math.random() * 20);
    document.getElementById('cadence').textContent = `${cadence} 步/分钟`;
    
    // 模拟计算垂直振幅
    const oscillation = (8 + Math.random() * 3).toFixed(1);
    document.getElementById('oscillation').textContent = `${oscillation} 厘米`;
    
    // 模拟计算着地冲击
    const impact = (2.5 + Math.random() * 1.5).toFixed(1);
    document.getElementById('impact').textContent = `${impact} g`;
    
    // 模拟计算前后足比例
    const ratio = (1 + Math.random() * 0.5).toFixed(1);
    document.getElementById('footRatio').textContent = `${ratio}:1`;
}

/**
 * 更新传感器图表
 */
function updateSensorCharts(data) {
    // 更新加速度图表
    const accData = dataHistory.timestamps.map((time, index) => {
        const acc = dataHistory.acceleration[index];
        return [
            [time, acc[0]], // X轴
            [time, acc[1]], // Y轴
            [time, acc[2]]  // Z轴
        ];
    });
    
    charts.accChart.setOption({
        series: [{
            data: accData.map(item => item[0])
        }, {
            data: accData.map(item => item[1])
        }, {
            data: accData.map(item => item[2])
        }]
    });
    
    // 更新角速度图表
    const gyroData = dataHistory.timestamps.map((time, index) => {
        const gyro = dataHistory.gyroscope[index];
        return [
            [time, gyro[0]], // X轴
            [time, gyro[1]], // Y轴
            [time, gyro[2]]  // Z轴
        ];
    });
    
    charts.gyroChart.setOption({
        series: [{
            data: gyroData.map(item => item[0])
        }, {
            data: gyroData.map(item => item[1])
        }, {
            data: gyroData.map(item => item[2])
        }]
    });
    
    // 更新足压图表
    charts.pressureChart.setOption({
        series: [{
            data: [{
                value: data.pressure,
                name: '足压分布'
            }]
        }]
    });
}

/**
 * 更新建议列表
 */
function updateRecommendations(recommendations) {
    const container = document.getElementById('recommendationsContainer');
    
    // 清空容器
    container.innerHTML = '';
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<div class="recommendation-item">当前没有建议</div>';
        return;
    }
    
    // 添加所有建议
    recommendations.forEach(recommendation => {
        const div = document.createElement('div');
        div.className = 'recommendation-item';
        div.textContent = recommendation;
        container.appendChild(div);
    });
}