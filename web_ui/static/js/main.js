/**
 * 中长跑实时指导系统 - 主JavaScript文件
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('中长跑实时指导系统初始化完成');
    
    // 平滑滚动效果
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // 检测设备连接状态
    checkDeviceConnection();
    
    // 其他全局功能初始化
    setupTooltips();
});

/**
 * 检查设备连接状态
 */
function checkDeviceConnection() {
    // 这里可以添加实际的设备检测逻辑
    console.log('检查设备连接状态');
    
    // 模拟设备检测
    setTimeout(() => {
        console.log('设备检测完成');
    }, 1000);
}

/**
 * 设置页面工具提示
 */
function setupTooltips() {
    // 如果使用Bootstrap的工具提示，可以在这里初始化
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}