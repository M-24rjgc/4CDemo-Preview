/**
 * 中长跑实时指导系统 - 深度分析页面JavaScript文件
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('深度分析页面初始化完成');
    
    // 初始化图表
    initCharts();
    
    // 绑定按钮事件
    document.getElementById('analyzeBtn').addEventListener('click', analyzeData);
    document.getElementById('exportReportBtn').addEventListener('click', exportReport);
    
    // 绑定下拉框变化事件
    document.getElementById('sessionSelect').addEventListener('change', updateComparisonOptions);
    document.getElementById('comparisonSelect').addEventListener('change', updateComparisonChart);
    
    // 默认加载最新数据
    analyzeData();
});

/**
 * 初始化所有图表
 */
function initCharts() {
    // 初始化姿态评分雷达图
    const radarChart = echarts.init(document.getElementById('radarChart'));
    const radarOption = {
        tooltip: {
            trigger: 'item'
        },
        radar: {
            indicator: [
                { name: '步频', max: 100 },
                { name: '步幅', max: 100 },
                { name: '垂直振幅', max: 100 },
                { name: '着地冲击', max: 100 },
                { name: '足部着地', max: 100 },
                { name: '步态稳定性', max: 100 }
            ],
            shape: 'polygon',
            splitNumber: 5,
            splitArea: {
                show: true,
                areaStyle: {
                    color: ['rgba(210,217,255,0.2)',
                        'rgba(200,207,245,0.4)',
                        'rgba(190,197,235,0.6)',
                        'rgba(180,187,225,0.8)',
                        'rgba(170,177,215,1)']
                }
            }
        },
        series: [{
            name: '姿态评分',
            type: 'radar',
            data: [
                {
                    value: [85, 92, 65, 78, 88, 82],
                    name: '当前表现',
                    symbol: 'circle',
                    symbolSize: 6,
                    lineStyle: {
                        width: 2
                    },
                    areaStyle: {
                        color: 'rgba(54, 162, 235, 0.6)'
                    }
                }
            ]
        }]
    };
    radarChart.setOption(radarOption);

    // 初始化步态周期分析图
    const gaitCycleChart = echarts.init(document.getElementById('gaitCycleChart'));
    const gaitCycleOption = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                label: {
                    backgroundColor: '#6a7985'
                }
            }
        },
        legend: {
            data: ['垂直加速度', '步态相位']
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                boundaryGap: false,
                data: ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%']
            }
        ],
        yAxis: [
            {
                type: 'value',
                name: '加速度 (m/s²)'
            }
        ],
        series: [
            {
                name: '垂直加速度',
                type: 'line',
                stack: 'Total',
                smooth: true,
                lineStyle: {
                    width: 3
                },
                areaStyle: {
                    opacity: 0.3
                },
                emphasis: {
                    focus: 'series'
                },
                markLine: {
                    data: [
                        {
                            name: '着地',
                            xAxis: 2
                        },
                        {
                            name: '起跳',
                            xAxis: 6
                        }
                    ]
                },
                data: [9.5, 10.2, 10.8, 10.5, 10.0, 9.7, 9.5, 10.2, 10.8, 10.1, 9.8]
            },
            {
                name: '步态相位',
                type: 'line',
                stack: 'Total',
                smooth: true,
                lineStyle: {
                    width: 2,
                    type: 'dashed'
                },
                areaStyle: {
                    opacity: 0.1
                },
                emphasis: {
                    focus: 'series'
                },
                markArea: {
                    itemStyle: {
                        opacity: 0.2,
                        color: 'green'
                    },
                    data: [
                        [
                            {
                                name: '支撑相',
                                xAxis: '0%'
                            },
                            {
                                xAxis: '60%'
                            }
                        ],
                        [
                            {
                                name: '摆动相',
                                xAxis: '60%'
                            },
                            {
                                xAxis: '100%'
                            }
                        ]
                    ]
                },
                data: [1.5, 1.2, 0.8, 0.5, 0.3, 0.2, 0.3, 0.8, 1.2, 1.6, 1.8]
            }
        ]
    };
    gaitCycleChart.setOption(gaitCycleOption);

    // 初始化足部着地类型图
    const footStrikeChart = echarts.init(document.getElementById('footStrikeChart'));
    const footStrikeOption = {
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            data: ['前掌着地', '中掌着地', '后掌着地']
        },
        series: [
            {
                name: '着地类型',
                type: 'pie',
                radius: '60%',
                center: ['50%', '60%'],
                data: [
                    { value: 60, name: '前掌着地', itemStyle: { color: '#91cc75' } },
                    { value: 35, name: '中掌着地', itemStyle: { color: '#fac858' } },
                    { value: 5, name: '后掌着地', itemStyle: { color: '#ee6666' } }
                ],
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    };
    footStrikeChart.setOption(footStrikeOption);

    // 初始化足压热力图
    const pressureHeatmap = echarts.init(document.getElementById('pressureHeatmap'));
    // 模拟一个20x10的足压热力图数据
    const data = [];
    const yMax = 10;
    const xMax = 20;
    for (let i = 0; i < xMax; i++) {
        for (let j = 0; j < yMax; j++) {
            // 生成足部形状的压力分布
            let value = 0;
            if (i >= 5 && i < 15) {
                // 足部主体
                if (j >= 1 && j < 9) {
                    const distance = Math.sqrt(Math.pow((i - 10), 2) + Math.pow((j - 5), 2));
                    if (distance < 8) {
                        value = 10 - distance;
                        if (j < 3 && i > 10) {
                            value += 2; // 前掌区域增加压力
                        }
                        if (j > 7 && i < 10) {
                            value += 1; // 后脚跟区域增加压力
                        }
                        value = Math.max(0, Math.min(10, value));
                    }
                }
            }
            data.push([i, j, value]);
        }
    }

    const pressureHeatmapOption = {
        tooltip: {
            position: 'top',
            formatter: (params) => {
                return `压力: ${params.data[2].toFixed(1)}`;
            }
        },
        grid: {
            top: 10,
            bottom: 60
        },
        xAxis: {
            type: 'category',
            show: false
        },
        yAxis: {
            type: 'category',
            show: false
        },
        visualMap: {
            min: 0,
            max: 10,
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            bottom: 10,
            inRange: {
                color: [
                    '#313695',
                    '#4575b4',
                    '#74add1',
                    '#abd9e9',
                    '#e0f3f8',
                    '#ffffbf',
                    '#fee090',
                    '#fdae61',
                    '#f46d43',
                    '#d73027',
                    '#a50026'
                ]
            }
        },
        series: [{
            name: '足压分布',
            type: 'heatmap',
            data: data,
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }]
    };
    pressureHeatmap.setOption(pressureHeatmapOption);

    // 初始化对比图表
    const comparisonChart = echarts.init(document.getElementById('comparisonChart'));
    const comparisonOption = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            },
            formatter: function(params) {
                const current = params[0].value;
                const comparison = params[1].value;
                const diff = ((current - comparison) / comparison * 100).toFixed(1);
                const diffText = diff > 0 ? `+${diff}%` : `${diff}%`;
                return `${params[0].name}<br/>${params[0].seriesName}: ${current}<br/>${params[1].seriesName}: ${comparison}<br/>差异: ${diffText}`;
            }
        },
        legend: {
            data: ['当前训练', '上次训练']
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'value'
        },
        yAxis: {
            type: 'category',
            data: ['步频', '垂直振幅', '冲击力', '姿态评分']
        },
        series: [
            {
                name: '当前训练',
                type: 'bar',
                data: [178, 9.2, 2.8, 87],
                itemStyle: {
                    color: '#5470c6'
                }
            },
            {
                name: '上次训练',
                type: 'bar',
                data: [175, 9.8, 3.1, 85],
                itemStyle: {
                    color: '#91cc75'
                }
            }
        ]
    };
    comparisonChart.setOption(comparisonOption);

    // 适配窗口大小变化
    window.addEventListener('resize', function() {
        radarChart.resize();
        gaitCycleChart.resize();
        footStrikeChart.resize();
        pressureHeatmap.resize();
        comparisonChart.resize();
    });

    // 存储图表对象以便后续更新
    window.charts = {
        radarChart,
        gaitCycleChart,
        footStrikeChart,
        pressureHeatmap,
        comparisonChart
    };
}

/**
 * 分析选中的数据
 */
function analyzeData() {
    const sessionId = document.getElementById('sessionSelect').value;
    const comparisonType = document.getElementById('comparisonSelect').value;
    
    console.log(`分析数据: 训练ID=${sessionId}, 对比类型=${comparisonType}`);
    
    // 这里应该从API获取实际数据
    // 现在只是简单地展示加载状态
    document.getElementById('analyzeBtn').textContent = '分析中...';
    
    // 模拟API请求延迟
    setTimeout(() => {
        // 更新各项指标（实际中应从API获取）
        updateMetrics();
        
        // 更新对比图表
        if (comparisonType !== 'none') {
            updateComparisonChart();
        }
        
        document.getElementById('analyzeBtn').textContent = '分析数据';
    }, 1000);
}

/**
 * 根据选中的训练更新对比选项
 */
function updateComparisonOptions() {
    const sessionId = document.getElementById('sessionSelect').value;
    const comparisonSelect = document.getElementById('comparisonSelect');
    
    // 如果选择了最新训练，则上一次训练选项可用
    if (sessionId === 'latest') {
        Array.from(comparisonSelect.options).forEach(option => {
            option.disabled = false;
        });
    } else {
        // 禁用"上一次训练"选项
        const previousOption = Array.from(comparisonSelect.options).find(option => option.value === 'previous');
        if (previousOption) {
            previousOption.disabled = true;
            
            // 如果当前选择的是"上一次训练"，则切换到"不对比"
            if (comparisonSelect.value === 'previous') {
                comparisonSelect.value = 'none';
            }
        }
    }
}

/**
 * 更新指标卡片
 */
function updateMetrics() {
    // 这里应该用实际数据更新指标
    // 现在使用的是模拟数据
    document.getElementById('cadenceValue').textContent = '178';
    document.getElementById('oscillationValue').textContent = '9.2';
    document.getElementById('impactValue').textContent = '2.8';
}

/**
 * 更新对比图表
 */
function updateComparisonChart() {
    const comparisonType = document.getElementById('comparisonSelect').value;
    if (comparisonType === 'none') {
        document.getElementById('comparisonChart').parentElement.querySelector('p').style.display = 'block';
        return;
    }
    
    document.getElementById('comparisonChart').parentElement.querySelector('p').style.display = 'none';
    
    // 根据对比类型获取不同的数据
    let comparisonData;
    let comparisonLabel;
    
    switch (comparisonType) {
        case 'previous':
            comparisonData = [175, 9.8, 3.1, 85];
            comparisonLabel = '上次训练';
            break;
        case 'best':
            comparisonData = [182, 7.5, 2.5, 92];
            comparisonLabel = '个人最佳';
            break;
        case 'average':
            comparisonData = [176, 8.9, 2.9, 84];
            comparisonLabel = '个人平均';
            break;
    }
    
    // 更新对比图表
    window.charts.comparisonChart.setOption({
        legend: {
            data: ['当前训练', comparisonLabel]
        },
        series: [
            {
                // 当前训练数据不变
                name: '当前训练'
            },
            {
                name: comparisonLabel,
                data: comparisonData
            }
        ]
    });
}

/**
 * 导出PDF报告
 */
function exportReport() {
    console.log('导出PDF报告');
    
    const sessionId = document.getElementById('sessionSelect').value;
    
    // 显示导出中提示
    const exportBtn = document.getElementById('exportReportBtn');
    const originalText = exportBtn.textContent;
    exportBtn.textContent = '导出中...';
    exportBtn.disabled = true;
    
    // 发送导出请求
    fetch('/api/export_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            format: 'pdf',
            sessionId: sessionId,
            reportType: 'detailed'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // 下载文件
            window.location.href = data.file_url;
        } else {
            console.error(data.message);
            alert('导出失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('导出报告失败:', error);
        alert('导出失败: ' + error.message);
    })
    .finally(() => {
        // 恢复按钮状态
        exportBtn.textContent = originalText;
        exportBtn.disabled = false;
    });
}