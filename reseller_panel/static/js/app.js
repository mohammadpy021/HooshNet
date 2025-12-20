// Reseller Panel JS

document.addEventListener('DOMContentLoaded', function () {
    // Mobile Menu Toggle
    const menuToggle = document.getElementById('menu-toggle');
    const menuClose = document.getElementById('menu-close');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    function toggleMenu() {
        sidebar.classList.toggle('active');
        if (overlay) overlay.classList.toggle('active');
    }

    if (menuToggle) {
        menuToggle.addEventListener('click', toggleMenu);
    }

    if (menuClose) {
        menuClose.addEventListener('click', toggleMenu);
    }

    if (overlay) {
        overlay.addEventListener('click', toggleMenu);
    }

    // Initialize Charts if on dashboard
    if (document.getElementById('salesChart')) {
        initDashboardCharts();
    }
});

function initDashboardCharts() {
    fetch('/reseller/api/chart-data')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('salesChart').getContext('2d');

            // Gradient for chart
            const gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, 'rgba(229, 9, 20, 0.5)');
            gradient.addColorStop(1, 'rgba(229, 9, 20, 0.0)');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه'], // Mock labels
                    datasets: [{
                        label: 'درآمد (تومان)',
                        data: [120000, 190000, 300000, 50000, 200000, 300000, 450000], // Mock data
                        borderColor: '#E50914',
                        backgroundColor: gradient,
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#000000',
                        pointBorderColor: '#E50914',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        pointHoverBackgroundColor: '#E50914',
                        pointHoverBorderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(20, 20, 20, 0.95)',
                            titleColor: '#fff',
                            bodyColor: '#a3a3a3',
                            borderColor: 'rgba(255, 255, 255, 0.1)',
                            borderWidth: 1,
                            padding: 12,
                            displayColors: false,
                            titleFont: {
                                family: 'Vazirmatn',
                                size: 14
                            },
                            bodyFont: {
                                family: 'Vazirmatn',
                                size: 13
                            },
                            cornerRadius: 12
                        }
                    },
                    scales: {
                        y: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.05)',
                                borderDash: [5, 5],
                                drawBorder: false
                            },
                            ticks: {
                                color: '#808080',
                                font: {
                                    family: 'Inter',
                                    size: 11
                                },
                                padding: 10
                            },
                            border: {
                                display: false
                            }
                        },
                        x: {
                            grid: {
                                display: false,
                                drawBorder: false
                            },
                            ticks: {
                                color: '#808080',
                                font: {
                                    family: 'Vazirmatn',
                                    size: 12
                                },
                                padding: 10
                            },
                            border: {
                                display: false
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading charts:', error));
}
