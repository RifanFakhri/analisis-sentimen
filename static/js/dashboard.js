/**
 * Dashboard JavaScript for Sentiment Analysis
 * Handles fetching stats and rendering premium dashboard components.
 */

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();

    // Add filter listeners
    const sentimentFilter = document.getElementById('dataset-sentiment-filter');
    if (sentimentFilter) {
        sentimentFilter.addEventListener('change', () => loadDashboardData());
    }

    const rangeFilter = document.getElementById('trend-range-filter');
    if (rangeFilter) {
        rangeFilter.addEventListener('change', () => loadDashboardData());
    }
});

async function loadDashboardData() {
    try {
        const sentiment = document.getElementById('dataset-sentiment-filter').value;
        const range = document.getElementById('trend-range-filter').value;
        
        const response = await fetch(`/api/stats?sentiment=${sentiment}&range=${range}`);
        const data = await response.json();

        if (data.error) {
            console.error('Error fetching stats:', data.error);
            return;
        }

        renderStats(data.summary, data.metrics);
        renderCharts(data);
        renderAspects(data.aspects);
        renderWordClouds(data.top_pos, data.top_neg);
        renderSamples(data.samples);

    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

function renderStats(summary, metrics) {
    document.getElementById('sum-total').textContent = summary.total_reviews.toLocaleString();
    document.getElementById('sum-pos-count').textContent = summary.pos_count.toLocaleString();
    document.getElementById('sum-neg-count').textContent = summary.neg_count.toLocaleString();
    
    document.getElementById('sum-pos-percent').textContent = summary.pos_percent + '%';
    document.getElementById('sum-neg-percent').textContent = summary.neg_percent + '%';

    const accEl = document.getElementById('sum-accuracy');
    if (metrics.is_trained) {
        accEl.textContent = metrics.accuracy + '%';
        document.getElementById('metric-precision').textContent = metrics.precision + '%';
        document.getElementById('metric-recall').textContent = metrics.recall + '%';
        document.getElementById('metric-f1').textContent = metrics.f1 + '%';
    } else {
        accEl.textContent = 'N/A';
    }
}

function renderAspects(aspects) {
    const list = document.getElementById('aspects-list');
    list.innerHTML = '';

    aspects.forEach(asp => {
        const item = document.createElement('div');
        // Dynamic colors based on frequency like the reference
        let barColor = '#10b981'; // Green
        if (asp.percent < 60) barColor = '#f59e0b'; // Orange
        if (asp.percent < 35) barColor = '#ef4444'; // Red
        
        item.innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.85rem;">
                <span style="color: #cbd5e1;">${asp.aspect}</span>
                <span style="color: white; font-weight: 700;">${asp.percent}%</span>
            </div>
            <div style="height: 8px; background: rgba(255,255,255,0.05); border-radius: 4px; overflow: hidden;">
                <div style="width: ${asp.percent}%; height: 100%; background: ${barColor}; border-radius: 4px;"></div>
            </div>
        `;
        list.appendChild(item);
    });
}

function renderWordClouds(topPos, topNeg) {
    const posList = document.getElementById('pos-keywords-list');
    posList.innerHTML = '';
    topPos.forEach(kw => {
        const span = document.createElement('span');
        span.className = 'tag tag-pos';
        span.textContent = kw.word;
        posList.appendChild(span);
    });

    // Also add negative word cloud if the container exists
    const negList = document.getElementById('neg-keywords-list');
    if (negList) {
        negList.innerHTML = '';
        topNeg.forEach(kw => {
            const span = document.createElement('span');
            span.className = 'tag tag-neg';
            span.textContent = kw.word;
            negList.appendChild(span);
        });
    }
}

function renderCharts(data) {
    // 1. Trend Chart
    const ctxTrend = document.getElementById('trendChart').getContext('2d');
    if (window.myTrendChart) window.myTrendChart.destroy();
    
    window.myTrendChart = new Chart(ctxTrend, {
        type: 'bar',
        data: {
            labels: data.trend.labels,
            datasets: [
                {
                    label: 'Positif',
                    data: data.trend.positif,
                    backgroundColor: '#10b981',
                    borderRadius: 4,
                    barPercentage: 0.8,
                    categoryPercentage: 0.7
                },
                {
                    label: 'Negatif',
                    data: data.trend.negatif,
                    backgroundColor: '#ef4444',
                    borderRadius: 4,
                    barPercentage: 0.8,
                    categoryPercentage: 0.7
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', align: 'end', labels: { boxWidth: 10, usePointStyle: true, color: '#94a3b8', font: { size: 10 } } }
            },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8', font: { size: 9 } } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 9 } } }
            }
        }
    });

    // 2. Distribution Chart
    const ctxDist = document.getElementById('distributionChart').getContext('2d');
    if (window.myDistChart) window.myDistChart.destroy();
    
    window.myDistChart = new Chart(ctxDist, {
        type: 'doughnut',
        data: {
            labels: data.distribution.labels,
            datasets: [{
                data: data.distribution.values,
                backgroundColor: ['#ef4444', '#475569', '#10b981'],
                borderWidth: 2,
                borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderSamples(samples) {
    const list = document.getElementById('neg-samples-list');
    list.innerHTML = '';
    samples.forEach(sample => {
        const div = document.createElement('div');
        div.className = 'sample-box';
        div.textContent = `"${sample}"`;
        list.appendChild(div);
    });
}
