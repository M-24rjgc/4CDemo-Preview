/**
 * 中长跑实时指导系统 - 历史数据页面JavaScript文件
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('历史数据页面初始化完成');
    
    // 初始化日期范围选择器
    initDateRangePicker();
    
    // 初始化图表
    initCharts();
    
    // 绑定按钮事件
    document.getElementById('filterBtn').addEventListener('click', applyFilters);
    document.getElementById('exportBtn').addEventListener('click', exportData);
    
    // 加载历史数据
    loadHistoryData();
});

/**
 * 初始化日期范围选择器
 */
function initDateRangePicker() {
    $('#dateRange').daterangepicker({
        startDate: moment().subtract(30, 'days'),
        endDate: moment(),
        locale: {
            format: 'YYYY-MM-DD',
            applyLabel: '确定',
            cancelLabel: '取消',
            customRangeLabel: '自定义范围',
            daysOfWeek: ['日', '一', '二', '三', '四', '五', '六'],
            monthNames: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
        },
        ranges: {
           '最近7天': [moment().subtract(6, 'days'), moment()],
           '最近30天': [moment().subtract(29, 'days'), moment()],
           '本月': [moment().startOf('month'), moment().endOf('month')],
           '上个月': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    });
}

/**
 * 初始化图表
 */
function initCharts() {
    // 初始化姿态评分趋势图
    const scoreChart = echarts.init(document.getElementById('scoreChart'));
    const scoreOption = {
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['姿态评分']
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: ['2024-02-18', '2024-02-20', '2024-02-23', '2024-02-25']
        },
        yAxis: {
            type: 'value',
            min: 60,
            max: 100
        },
        series: [
            {
                name: '姿态评分',
                type: 'line',
                data: [82, 89, 85, 87],
                markLine: {
                    data: [
                        {
                            name: '良好水平',
                            yAxis: 80
                        }
                    ]
                },
                lineStyle: {
                    color: '#5470c6',
                    width: 4
                },
                itemStyle: {
                    color: '#5470c6',
                    borderWidth: 3
                },
                symbol: 'circle',
                symbolSize: 10,
                smooth: true
            }
        ]
    };
    scoreChart.setOption(scoreOption);

    // 初始化步频变化图
    const cadenceChart = echarts.init(document.getElementById('cadenceChart'));
    const cadenceOption = {
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['步频']
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: ['2024-02-18', '2024-02-20', '2024-02-23', '2024-02-25']
        },
        yAxis: {
            type: 'value',
            name: '步/分钟',
            min: 160,
            max: 190
        },
        series: [
            {
                name: '步频',
                type: 'line',
                data: [175, 181, 182, 183],
                markArea: {
                    itemStyle: {
                        color: 'rgba(84, 112, 198, 0.1)'
                    },
                    data: [
                        [
                            {
                                name: '理想范围',
                                yAxis: 170
                            },
                            {
                                yAxis: 185
                            }
                        ]
                    ]
                },
                lineStyle: {
                    color: '#91cc75',
                    width: 3
                },
                symbol: 'circle',
                symbolSize: 8,
                smooth: true
            }
        ]
    };
    cadenceChart.setOption(cadenceOption);

    // 初始化步态相位分布图
    const phaseDistChart = echarts.init(document.getElementById('phaseDistChart'));
    const phaseDistOption = {
        tooltip: {
            trigger: 'item'
        },
        legend: {
            top: '5%',
            left: 'center'
        },
        series: [
            {
                name: '步态相位',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: false,
                    position: 'center'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: '18',
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: false
                },
                data: [
                    { value: 60, name: '支撑相', itemStyle: { color: '#5cb85c' } },
                    { value: 40, name: '摆动相', itemStyle: { color: '#5bc0de' } }
                ]
            }
        ]
    };
    phaseDistChart.setOption(phaseDistOption);

    // 适配窗口大小变化
    window.addEventListener('resize', function() {
        scoreChart.resize();
        cadenceChart.resize();
        phaseDistChart.resize();
    });
}

/**
 * 加载历史数据
 */
function loadHistoryData() {
    // 从API获取历史数据
    const startDate = $('#dateRange').data('daterangepicker').startDate.format('YYYY-MM-DD');
    const endDate = $('#dateRange').data('daterangepicker').endDate.format('YYYY-MM-DD');
    
    fetch(`/api/history?start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
            updateStatistics(data);
            updateCharts(data);
            updateHistoryTable(data);
        })
        .catch(error => {
            console.error('获取历史数据失败:', error);
        });
}

/**
 * 应用筛选条件
 */
function applyFilters() {
    console.log('应用筛选条件');
    loadHistoryData();
}

/**
 * 更新统计信息
 */
function updateStatistics(data) {
    // 这里应该使用实际数据更新统计信息
    // 现在使用示例数据
    document.getElementById('totalSessions').textContent = '12';
    document.getElementById('totalDuration').textContent = '18h';
    document.getElementById('avgScore').textContent = '83';
    document.getElementById('avgCadence').textContent = '178';
}

/**
 * 更新图表数据
 */
function updateCharts(data) {
    // 这里应该使用实际数据更新图表
    // 现在图表已在初始化时设置了示例数据
}

/**
 * 更新历史表格
 */
function updateHistoryTable(data) {
    // 这里应该使用实际数据更新历史表格
    // 现在表格已包含示例数据
}

/**
 * 导出数据
 */
function exportData() {
    console.log('导出数据');
    
    // 显示导出选项弹窗
    const format = window.confirm('选择导出格式：\n确定 - CSV格式\n取消 - PDF报告') ? 'csv' : 'pdf';
    
    // 发送导出请求
    fetch('/api/export_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            format: format,
            startDate: $('#dateRange').data('daterangepicker').startDate.format('YYYY-MM-DD'),
            endDate: $('#dateRange').data('daterangepicker').endDate.format('YYYY-MM-DD')
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
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