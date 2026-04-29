document.addEventListener('DOMContentLoaded', () => {
    // Fetch data from API
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            updateSummaryCards(data.summary);
            renderProgressChart(data.monthly_progress);
            renderRegionalTable(data.regional_status);
        })
        .catch(error => {
            console.error('Error fetching dashboard data:', error);
        });
});

// Function to animate numbers
const animateValue = (obj, start, end, duration) => {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        
        // Easing function for smooth stop
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        
        const currentVal = Math.floor(easeOutQuart * (end - start) + start);
        obj.innerHTML = currentVal.toLocaleString('id-ID');
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.innerHTML = end.toLocaleString('id-ID');
        }
    };
    window.requestAnimationFrame(step);
};

const updateSummaryCards = (summary) => {
    const targetEl = document.getElementById('val-target-area');
    const realizedEl = document.getElementById('val-realized-area');
    const activeEl = document.getElementById('val-active-projects');
    const progressEl = document.getElementById('val-overall-progress');
    const progressBar = document.getElementById('progress-bar-realized');

    animateValue(targetEl, 0, summary.total_area_target, 1500);
    animateValue(realizedEl, 0, summary.total_area_realized, 1800);
    animateValue(activeEl, 0, summary.active_projects, 1200);
    
    // For percentage
    let startTimestamp = null;
    const duration = 2000;
    const finalProg = summary.overall_progress;
    
    const stepProg = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const currentVal = (progress * finalProg).toFixed(1);
        progressEl.innerHTML = currentVal;
        if (progress < 1) {
            window.requestAnimationFrame(stepProg);
        } else {
            progressEl.innerHTML = finalProg;
        }
    };
    window.requestAnimationFrame(stepProg);

    // Decorative bar
    setTimeout(() => {
        const percent = (summary.total_area_realized / summary.total_area_target) * 100;
        progressBar.style.width = percent + '%';
    }, 500);
};

const renderProgressChart = (data) => {
    const ctx = document.getElementById('progressChart').getContext('2d');
    
    // Chart.js default font
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = '#64748b';

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Target Kumulatif',
                    data: data.target,
                    borderColor: '#cbd5e1',
                    borderDash: [5, 5],
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4
                },
                {
                    label: 'Realisasi Kumulatif',
                    data: data.realized,
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#4f46e5',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    fill: true,
                    tension: 0.4
                }
            ]
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
                    position: 'top',
                    align: 'end',
                    labels: {
                        usePointStyle: true,
                        boxWidth: 8,
                        boxHeight: 8
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleFont: { size: 13 },
                    bodyFont: { size: 13 },
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#f1f5f9',
                        drawBorder: false,
                    },
                    border: { display: false }
                },
                x: {
                    grid: {
                        display: false
                    },
                    border: { display: false }
                }
            }
        }
    });
};

const renderRegionalTable = (regions) => {
    const tbody = document.getElementById('regional-table-body');
    tbody.innerHTML = '';

    regions.forEach(item => {
        const tr = document.createElement('tr');
        tr.className = 'transition hover:bg-slate-50/50';
        
        let statusClass = 'status-on-track';
        if (item.status === 'Delayed') {
            statusClass = 'status-delayed';
        }

        const percent = ((item.realized / item.target) * 100).toFixed(1);

        tr.innerHTML = `
            <td class="px-4 py-4">
                <div class="font-medium text-slate-800">${item.region}</div>
                <div class="text-xs text-slate-400">Target: ${item.target.toLocaleString('id-ID')} Ha</div>
            </td>
            <td class="px-4 py-4">
                <div class="flex items-center">
                    <span class="mr-2 font-medium text-slate-700 w-10 text-right">${percent}%</span>
                    <div class="w-full bg-slate-100 rounded-full h-2 max-w-[5rem]">
                        <div class="bg-indigo-500 h-2 rounded-full" style="width: ${percent}%"></div>
                    </div>
                </div>
            </td>
            <td class="px-4 py-4">
                <span class="status-badge ${statusClass}">
                    ${item.status === 'On Track' ? '<i class="fa-solid fa-check mr-1"></i> On Track' : '<i class="fa-solid fa-triangle-exclamation mr-1"></i> Terlambat'}
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });
};

// Function for Sidebar Accordions
window.toggleDropdown = function(id, event) {
    if(event) {
        // Prevent default only if event exists
        event.preventDefault();
        event.stopPropagation();
    }
    const el = document.getElementById(id);
    const icon = document.getElementById('icon-' + id);
    if (!el) return;
    
    if (el.classList.contains('hidden')) {
        el.classList.remove('hidden');
        el.classList.add('flex');
        if(icon) icon.classList.add('rotate-180');
    } else {
        el.classList.add('hidden');
        el.classList.remove('flex');
        if(icon) icon.classList.remove('rotate-180');
    }
};
