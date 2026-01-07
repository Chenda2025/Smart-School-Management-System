// static/js/student/dashboard-chart.js
// (or static/js/dashboard-chart.js if no 'student' folder)

document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById('performanceChart');
    if (!canvas) {
        console.warn('Performance chart canvas not found!');
        return;
    }

    const ctx = canvas.getContext('2d');

    // Use real data passed from Django if available, otherwise fallback
    const labels = window.chartLabels || ['No exams recorded yet'];
    const myScores = window.chartScores || [0];
    const classAverages = window.chartClassAverages || [0];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Your Score',
                    data: myScores,
                    borderColor: '#10b981',           // Emerald Green
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    tension: 0.4,
                    borderWidth: 4,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 10,
                    fill: true
                },
                {
                    label: 'Class Average',
                    data: classAverages,
                    borderColor: '#3b82f6',           // Indigo Blue
                    backgroundColor: 'rgba(59, 130, 246, 0.15)',
                    tension: 0.4,
                    borderWidth: 3,
                    borderDash: [10, 5],
                    pointRadius: 4,
                    pointHoverRadius: 8,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.9)',
                        font: {
                            size: 14,
                            family: "'Space Grotesk', sans-serif",
                            weight: '500'
                        },
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    cornerRadius: 12,
                    displayColors: true,
                    borderColor: '#6366f1',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.8)',
                        stepSize: 20,
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        borderDash: [5, 5]
                    }
                },
                x: {
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.8)',
                        maxRotation: 45,
                        minRotation: 0
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            },
            hover: {
                animationDuration: 300
            }
        }
    });
});