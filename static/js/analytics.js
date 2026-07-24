// LifeTrack Chart.js Dashboard Visualizations

document.addEventListener('DOMContentLoaded', function() {
    const trendCanvas = document.getElementById('trend-chart');
    if (!trendCanvas) return; // Exit if not on analytics page

    const taskCanvas = document.getElementById('task-chart');
    const weekdayCanvas = document.getElementById('weekday-chart');
    const pieCanvas = document.getElementById('pie-chart');
    
    const noDataPlaceholder = document.getElementById('analytics-no-data');
    const chartsContainer = document.getElementById('analytics-charts-container');

    // Load datasets
    fetch('/api/chart-data')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.data && Object.keys(data.data).length > 0 && data.data.trend_dates.length > 0) {
                if (noDataPlaceholder) noDataPlaceholder.style.display = 'none';
                if (chartsContainer) chartsContainer.style.display = 'block';
                renderCharts(data.data);
            } else {
                if (noDataPlaceholder) noDataPlaceholder.style.display = 'block';
                if (chartsContainer) chartsContainer.style.display = 'none';
            }
        })
        .catch(err => {
            console.error("Failed to load chart data:", err);
            if (noDataPlaceholder) noDataPlaceholder.style.display = 'block';
        });

    function renderCharts(dataset) {
        // Global Chart Defaults for Dark Theme
        Chart.defaults.color = '#94a3b8'; // text-muted
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.06)';
        Chart.defaults.font.family = "'Outfit', sans-serif";

        // 1. Line Trend Chart (Daily Scores)
        const trendCtx = trendCanvas.getContext('2d');
        const trendGradient = trendCtx.createLinearGradient(0, 0, 0, 300);
        trendGradient.addColorStop(0, 'rgba(99, 102, 241, 0.35)'); // Indigo Glow
        trendGradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');
        
        new Chart(trendCanvas, {
            type: 'line',
            data: {
                labels: dataset.trend_dates,
                datasets: [{
                    label: 'Score (/5)',
                    data: dataset.trend_scores,
                    borderColor: '#6366f1',
                    borderWidth: 3,
                    pointBackgroundColor: '#6366f1',
                    pointBorderColor: '#fff',
                    pointHoverRadius: 7,
                    tension: 0.35, // Smooth cubic interpolation
                    fill: true,
                    backgroundColor: trendGradient
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        min: 0,
                        max: 5,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });

        // 2. Horizontal Bar Chart (Task Completion Rate)
        const taskLabels = Object.keys(dataset.task_percentages);
        const taskValues = Object.values(dataset.task_percentages);
        
        new Chart(taskCanvas, {
            type: 'bar',
            data: {
                labels: taskLabels,
                datasets: [{
                    data: taskValues,
                    backgroundColor: [
                        '#6366f1', // Study - Indigo
                        '#06b6d4', // Project - Cyan
                        '#10b981', // Exercise - Emerald
                        '#a855f7', // Career - Purple
                        '#fbbf24'  // Social Media - Amber
                    ],
                    borderRadius: 8,
                    barThickness: 18
                }]
            },
            options: {
                indexAxis: 'y', // Make it horizontal bar chart
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        min: 0,
                        max: 100,
                        ticks: { callback: value => `${value}%` }
                    }
                }
            }
        });

        // 3. Weekly Heatmap (Weekday Average Scores)
        new Chart(weekdayCanvas, {
            type: 'bar',
            data: {
                labels: dataset.weekday_labels,
                datasets: [{
                    data: dataset.weekday_scores,
                    backgroundColor: 'rgba(99, 102, 241, 0.2)',
                    borderColor: '#6366f1',
                    borderWidth: 2,
                    borderRadius: 6,
                    barThickness: 24
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        min: 0,
                        max: 5,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });

        // 4. Pie Chart (Completions vs Partials vs Zero days)
        new Chart(pieCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Perfect Days (5/5)', 'Partial Days (1-4/5)', 'Zero Days (0/5)'],
                datasets: [{
                    data: dataset.pie_data,
                    backgroundColor: [
                        '#10b981', // Emerald
                        '#f59e0b', // Amber
                        '#ef4444'  // Rose
                    ],
                    borderWidth: 2,
                    borderColor: '#0f172a'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, padding: 15 }
                    }
                },
                cutout: '65%' // Sleek donut shape
            }
        });
    }
});
