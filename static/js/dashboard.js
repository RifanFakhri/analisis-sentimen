/**
 * Dashboard JavaScript for Sentiment Analysis
 * Handles fetching stats and rendering interactive charts.
 */

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();

    // Add filter listener
    const filter = document.getElementById('dataset-sentiment-filter');
    if (filter) {
        filter.addEventListener('change', (e) => {
            loadDashboardData(e.target.value);
        });
    }
});

async function loadDashboardData(sentiment = 'all') {
    try {
        const response = await fetch(`/api/stats?sentiment=${sentiment}`);
        const data = await response.json();

        if (data.error) {
            console.error('Error fetching stats:', data.error);
            return;
        }

        renderDatasetTable(data.dataset);
        
        // Only render charts on first load (all) or if needed
        // For simplicity, always render but could be optimized
        renderCharts(data);
        renderComplaints(data.complaints);
        renderSummary(data.summary);

    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

function renderDatasetTable(dataset) {
    const tbody = document.getElementById('dataset-tbody');
    tbody.innerHTML = '';

    dataset.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${item.tahun}</strong></td>
            <td>${item.rating} Bintang</td>
            <td><span class="badge-sentiment badge-${item.sentimen}">${item.sentimen}</span></td>
            <td>${item.ulasan}</td>
        `;
        tbody.appendChild(row);
    });
}

function renderCharts(data) {
    // 1. Trend Chart (Bar)
    const ctxTrend = document.getElementById('trendChart').getContext('2d');
    new Chart(ctxTrend, {
        type: 'bar',
        data: {
            labels: data.trend.years,
            datasets: [
                {
                    label: 'Positif',
                    data: data.trend.positif,
                    backgroundColor: '#10b981',
                    borderRadius: 8
                },
                {
                    label: 'Netral',
                    data: data.trend.netral,
                    backgroundColor: '#6b7280',
                    borderRadius: 8
                },
                {
                    label: 'Negatif',
                    data: data.trend.negatif,
                    backgroundColor: '#ef4444',
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { display: false } }
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8' } }
            }
        }
    });

    // 2. Distribution Chart (Doughnut)
    const ctxDist = document.getElementById('distributionChart').getContext('2d');
    new Chart(ctxDist, {
        type: 'doughnut',
        data: {
            labels: data.distribution.labels,
            datasets: [{
                data: data.distribution.values,
                backgroundColor: ['#ef4444', '#6b7280', '#10b981'],
                borderWidth: 0,
                cutout: '70%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8' } }
            }
        }
    });
}

function renderComplaints(complaints) {
    // Top Keywords
    const keywordList = document.getElementById('neg-keywords-list');
    keywordList.innerHTML = '';
    complaints.top_keywords.forEach(kw => {
        const item = document.createElement('div');
        item.className = 'keyword-item';
        item.innerHTML = `
            <span class="keyword-name">${kw.word}</span>
            <span class="keyword-count">${kw.count}</span>
        `;
        keywordList.appendChild(item);
    });

    // Sample Reviews
    const sampleList = document.getElementById('neg-samples-list');
    sampleList.innerHTML = '';
    complaints.samples.forEach(sample => {
        const item = document.createElement('div');
        item.className = 'sample-item';
        item.innerHTML = `
            <div class="sample-icon"><i class="fas fa-exclamation"></i></div>
            "${sample}"
        `;
        sampleList.appendChild(item);
    });
}

function renderSummary(summary) {
    document.getElementById('sum-total').textContent = summary.total_reviews;
    document.getElementById('sum-neg').textContent = summary.neg_percent + '%';
    document.getElementById('sum-worst').textContent = summary.worst_year;

    const summaryText = document.getElementById('summary-text');
    summaryText.innerHTML = `
        Berdasarkan analisis data ulasan tahun ${summary.worst_year - 2}-${summary.worst_year + 1}, 
        destinasi wisata menghadapi tantangan signifikan terutama pada tahun <strong>${summary.worst_year}</strong>. 
        Sentimen negatif didominasi oleh masalah kebersihan dan fasilitas umum. Namun, mayoritas wisatawan tetap memberikan respon positif terhadap keindahan alam.
    `;
}
