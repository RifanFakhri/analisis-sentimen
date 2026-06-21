# Quick Implementation Guide - UI Wireframe

## 📋 Overview

Panduan cepat untuk implementasi UI wireframe Sistem Analisis Sentimen Pulau Merak. Dokumentasi lengkap ada di `UI_WIREFRAME_LENGKAP.md` dan preview interaktif ada di `wireframe_mockup.html`.

---

## 🚀 Quick Start

### 1. Struktur File

```
templates/
├── base.html                 # Base template dengan navbar
├── index.html               # Halaman utama (prediksi)
├── dashboard.html           # Halaman dashboard
├── train.html              # Halaman training
└── history.html            # Halaman history

static/
├── css/
│   └── main.css            # Main stylesheet
└── js/
    └── components.js       # Reusable JS functions
```

### 2. CSS Framework Recommendation

**Pilih salah satu:**
- **Bootstrap 5**: Cepat, battle-tested, banyak komponen siap pakai
- **Tailwind CSS**: Modern, lightweight, utility-first approach
- **Custom CSS**: Full control (gunakan design tokens di bawah)

### 3. Chart Library

```html
<!-- Chart.js untuk visualisasi data -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- Atau Plotly untuk dashboard yang lebih advanced -->
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
```

### 4. Icons

```html
<!-- Font Awesome untuk icons -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- Atau Feather Icons yang lebih minimalis -->
<script src="https://cdn.jsdelivr.net/npm/feather-icons/dist/feather.min.js"></script>
```

---

## 🎨 Design Tokens CSS

Salin ke `static/css/variables.css`:

```css
:root {
    /* Colors */
    --color-primary: #3B82F6;
    --color-primary-dark: #2563EB;
    --color-primary-light: #DBEAFE;
    
    --color-success: #10B981;
    --color-success-light: #ECFDF5;
    
    --color-danger: #EF4444;
    --color-danger-light: #FEE2E2;
    
    --color-warning: #F59E0B;
    --color-warning-light: #FFFBEB;
    
    --color-neutral: #6B7280;
    --color-neutral-light: #F3F4F6;
    
    --color-text: #1F2937;
    --color-text-secondary: #6B7280;
    --color-text-tertiary: #9CA3AF;
    
    --color-border: #E5E7EB;
    --color-bg: #FFFFFF;
    --color-bg-secondary: #F9FAFB;
    
    /* Spacing */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-2xl: 48px;
    
    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-full: 999px;
    
    /* Shadow */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.2);
    
    /* Typography */
    --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-size-xs: 12px;
    --font-size-sm: 14px;
    --font-size-base: 16px;
    --font-size-lg: 20px;
    --font-size-xl: 24px;
    --font-size-2xl: 32px;
    
    /* Transitions */
    --transition-fast: 200ms ease-in-out;
    --transition-base: 300ms ease-in-out;
}
```

---

## 📄 Template Boilerplate

### base.html

```html
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Analisis Sentimen Pulau Merak{% endblock %}</title>
    
    <!-- Stylesheets -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-island me-2"></i>Analisis Sentimen Pulau Merak
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Beranda</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dashboard">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/train">Training</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/history">History</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="py-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-light py-4 mt-5">
        <div class="container text-center text-muted">
            <p>&copy; 2025 Sistem Analisis Sentimen Pulau Merak. All rights reserved.</p>
        </div>
    </footer>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### index.html (Halaman Utama)

```html
{% extends "base.html" %}

{% block title %}Beranda - Analisis Sentimen{% endblock %}

{% block content %}
<div class="container">
    <div class="row mb-4">
        <div class="col-lg-8">
            <h1 class="display-5">Analisis Sentimen Pulau Merak</h1>
            <p class="lead text-muted">
                Masukkan review atau upload dataset untuk analisis sentimen real-time menggunakan model machine learning
            </p>
        </div>
    </div>

    <div class="row">
        <!-- Input Text Section -->
        <div class="col-lg-6 mb-4">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <i class="fas fa-pen"></i> Input Teks
                </div>
                <div class="card-body">
                    <form id="predictionForm" onsubmit="handleTextSubmit(event)">
                        <div class="mb-3">
                            <label class="form-label">Masukkan Review atau Ulasan</label>
                            <textarea class="form-control" id="reviewText" placeholder="Masukkan review tentang Pulau Merak..." maxlength="500" rows="4"></textarea>
                            <small class="text-muted d-block mt-2">
                                <span id="charCount">0</span>/500 karakter
                            </small>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="fas fa-magnifying-glass"></i> Analisis Sentimen
                        </button>
                    </form>
                </div>
            </div>
        </div>

        <!-- Upload CSV Section -->
        <div class="col-lg-6 mb-4">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <i class="fas fa-upload"></i> Upload Dataset
                </div>
                <div class="card-body">
                    <div class="border-2 border-dashed p-4 text-center rounded" id="dropZone">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
                        <p class="fw-bold mb-2">Drag & drop file CSV di sini</p>
                        <p class="text-muted mb-3">atau</p>
                        <input type="file" id="csvFile" accept=".csv" style="display: none;">
                        <button type="button" class="btn btn-secondary" onclick="document.getElementById('csvFile').click()">
                            Pilih File
                        </button>
                        <p class="text-muted small mt-3">Format: CSV dengan kolom 'text' dan 'label'</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Result Section (Hidden by default) -->
    <div id="resultSection" class="row mb-4" style="display: none;">
        <div class="col-lg-12">
            <div class="card border-success">
                <div class="card-header bg-success text-white">
                    <i class="fas fa-check-circle"></i> Hasil Prediksi
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-lg-4">
                            <div class="text-center">
                                <h3 id="sentimentLabel" class="mb-3"></h3>
                                <div id="confidenceRing" style="font-size: 5rem; margin-bottom: 1rem;">😊</div>
                                <p class="h5">Score: <strong id="confidenceScore"></strong></p>
                            </div>
                        </div>
                        <div class="col-lg-8">
                            <div class="mb-3">
                                <strong>Confidence: <span id="confidencePercent"></span>%</strong>
                                <div class="progress">
                                    <div id="confidenceBar" class="progress-bar" role="progressbar" style="width: 0%"></div>
                                </div>
                            </div>

                            <div>
                                <strong>Distribusi Probabilitas:</strong>
                                <div class="mt-2" id="probabilityDistribution"></div>
                            </div>
                        </div>
                    </div>

                    <hr class="my-4">

                    <div>
                        <strong>📚 Langkah Preprocessing:</strong>
                        <div class="mt-2" id="preprocessingSteps"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Character Counter Script -->
<script>
    document.getElementById('reviewText').addEventListener('input', function() {
        document.getElementById('charCount').textContent = this.value.length;
    });

    async function handleTextSubmit(event) {
        event.preventDefault();
        const text = document.getElementById('reviewText').value;
        
        if (!text.trim()) {
            alert('Silakan masukkan review terlebih dahulu');
            return;
        }

        // API Call
        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });
            
            const data = await response.json();
            displayResult(data);
        } catch (error) {
            console.error('Error:', error);
            alert('Terjadi kesalahan dalam prediksi');
        }
    }

    function displayResult(data) {
        // Show result section
        document.getElementById('resultSection').style.display = 'block';
        
        // Set sentiment label dengan warna
        const label = document.getElementById('sentimentLabel');
        label.textContent = data.sentiment.toUpperCase();
        label.className = 'text-' + getSentimentColor(data.sentiment);
        
        // Set confidence
        document.getElementById('confidencePercent').textContent = Math.round(data.confidence * 100);
        document.getElementById('confidenceScore').textContent = data.confidence.toFixed(2);
        document.getElementById('confidenceBar').style.width = (data.confidence * 100) + '%';
        
        // Display probability distribution
        const probDiv = document.getElementById('probabilityDistribution');
        probDiv.innerHTML = Object.entries(data.probabilities).map(([label, prob]) => `
            <div class="mb-2">
                <div class="d-flex justify-content-between mb-1">
                    <span>${capitalize(label)}</span>
                    <span>${Math.round(prob * 100)}%</span>
                </div>
                <div class="progress">
                    <div class="progress-bar" style="width: ${prob * 100}%"></div>
                </div>
            </div>
        `).join('');
        
        // Scroll to result
        document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
    }

    function getSentimentColor(sentiment) {
        const colors = {
            'positif': 'success',
            'negatif': 'danger',
            'netral': 'warning'
        };
        return colors[sentiment] || 'primary';
    }

    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
</script>
{% endblock %}
```

---

## 🔧 Common Components

### Alert Component

```html
<!-- Success -->
<div class="alert alert-success alert-dismissible fade show" role="alert">
    <i class="fas fa-check-circle"></i> Operasi berhasil!
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>

<!-- Error -->
<div class="alert alert-danger alert-dismissible fade show" role="alert">
    <i class="fas fa-exclamation-circle"></i> Terjadi kesalahan!
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

### Loading Spinner

```html
<div class="spinner-border" role="status">
    <span class="visually-hidden">Loading...</span>
</div>

<!-- Or with text -->
<div class="d-flex align-items-center">
    <div class="spinner-border spinner-border-sm me-2" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>
    <span>Sedang memproses...</span>
</div>
```

### Stat Card

```html
<div class="card">
    <div class="card-body text-center">
        <h2 class="card-title text-primary">1,250</h2>
        <p class="card-text text-muted mb-2">Total Reviews</p>
        <small class="badge bg-success">↑ 5% dari bulan lalu</small>
    </div>
</div>
```

### Result Badge

```html
<!-- Positive -->
<span class="badge bg-success">✓ Positif</span>

<!-- Negative -->
<span class="badge bg-danger">✗ Negatif</span>

<!-- Neutral -->
<span class="badge bg-warning">⚠ Netral</span>
```

---

## 📊 Chart Examples

### Line Chart (Trend)

```javascript
const ctx = document.getElementById('trendChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [
            {
                label: 'Positif',
                data: [300, 320, 280, 350, 400, 420],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
            },
            {
                label: 'Netral',
                data: [200, 210, 220, 230, 250, 280],
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                tension: 0.4,
            },
            {
                label: 'Negatif',
                data: [250, 260, 270, 280, 300, 350],
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
            }
        ]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Trend Sentimen'
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
```

### Pie Chart (Distribution)

```javascript
const ctx = document.getElementById('distributionChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Positif', 'Netral', 'Negatif'],
        datasets: [{
            data: [36, 28, 36],
            backgroundColor: [
                '#10b981',
                '#f59e0b',
                '#ef4444'
            ],
            borderColor: '#ffffff',
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom'
            }
        }
    }
});
```

---

## ✅ Implementation Checklist

### Phase 1: Setup & Base
- [ ] Create base.html template
- [ ] Setup CSS variables dan main stylesheet
- [ ] Configure Bootstrap/Tailwind
- [ ] Setup icon library (Font Awesome/Feather)
- [ ] Create main.js dengan reusable functions

### Phase 2: Home Page
- [ ] Create index.html template
- [ ] Implement text input component
- [ ] Implement CSV upload dengan drag-drop
- [ ] Create result card styling
- [ ] Add character counter
- [ ] Implement API integration

### Phase 3: Training Page
- [ ] Create train.html template
- [ ] Stat cards untuk dataset overview
- [ ] Parameter configuration form
- [ ] Training progress bar
- [ ] Results visualization
- [ ] Confusion matrix display

### Phase 4: Dashboard
- [ ] Create dashboard.html template
- [ ] Filter section (date, sentiment)
- [ ] Key metrics cards
- [ ] Line chart untuk trend
- [ ] Pie chart untuk distribution
- [ ] Aspects analysis table
- [ ] Sample reviews display

### Phase 5: History
- [ ] Create history.html template
- [ ] Search & filter functionality
- [ ] Paginated table
- [ ] Row actions (view, delete)
- [ ] Detail modal
- [ ] Bulk operations

### Phase 6: Polish
- [ ] Responsive testing (mobile, tablet, desktop)
- [ ] Loading states untuk semua API calls
- [ ] Error handling dengan user-friendly messages
- [ ] Success toast/alerts
- [ ] Keyboard navigation
- [ ] Browser compatibility testing

---

## 🚨 Common Issues & Solutions

| Issue | Solusi |
|-------|--------|
| Chart tidak responsive | Gunakan `responsive: true` dan container dengan `max-width` |
| Form validation error | Tambahkan `required` attribute dan validasi di backend |
| API timeout | Implement loading spinner dan increase timeout |
| Mobile layout broken | Test di DevTools, gunakan CSS media queries |
| Font/Icon tidak tampil | Check CDN links dan CORS settings |
| Color tidak sesuai | Verify hex codes, test di berbagai browser |

---

## 📚 Resources

- **Bootstrap Docs**: https://getbootstrap.com/docs/5.3/
- **Chart.js Docs**: https://www.chartjs.org/docs/latest/
- **Font Awesome Icons**: https://fontawesome.com/icons
- **MDN CSS Guide**: https://developer.mozilla.org/en-US/docs/Web/CSS

---

**Terakhir Update**: Desember 2025
**Next Review**: Januari 2026

