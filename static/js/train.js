// ===== Label Selection =====
let selectedLabel = '';

function selectLabel(btn) {
    document.querySelectorAll('.label-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedLabel = btn.dataset.label;
}

// ===== Add Training Data =====
async function addTrainingData() {
    const text = document.getElementById('training-text').value.trim();
    if (!text) { showToast('Masukkan teks ulasan.', 'error'); return; }
    if (!selectedLabel) { showToast('Pilih label sentimen.', 'error'); return; }

    try {
        await apiFetch('/api/training-data', {
            method: 'POST',
            body: JSON.stringify({ text, label: selectedLabel }),
        });
        showToast('Data training berhasil ditambahkan!');
        document.getElementById('training-text').value = '';
        document.querySelectorAll('.label-btn').forEach(b => b.classList.remove('active'));
        selectedLabel = '';
        updateStats();
    } catch (err) { showToast(err.message, 'error'); }
}

// ===== Train Model =====
async function trainModel() {
    const btn = document.getElementById('btn-train');
    const progress = document.getElementById('training-progress');
    const results = document.getElementById('training-results');

    btn.disabled = true;
    progress.classList.remove('hidden');
    results.classList.add('hidden');

    try {
        const data = await apiFetch('/api/train', { method: 'POST' });
        progress.classList.add('hidden');
        displayTrainingResults(data.metrics);
        results.classList.remove('hidden');
        results.scrollIntoView({ behavior: 'smooth' });

        // Update model status in navbar
        const dot = document.getElementById('model-status-dot');
        const txt = document.getElementById('model-status-text');
        if (dot) { dot.className = 'status-dot status-active'; }
        if (txt) { txt.textContent = 'Model Ready'; }

        showToast(`Training selesai! Akurasi: ${data.metrics.accuracy}%`);
    } catch (err) {
        progress.classList.add('hidden');
        showToast(err.message, 'error');
    } finally { btn.disabled = false; }
}

// ===== Display Training Results =====
function displayTrainingResults(metrics) {
    // Accuracy ring
    const circumference = 2 * Math.PI * 54;
    const offset = circumference - (metrics.accuracy / 100) * circumference;
    const fill = document.getElementById('accuracy-fill');
    fill.style.strokeDasharray = circumference;
    setTimeout(() => { fill.style.strokeDashoffset = offset; }, 100);
    document.getElementById('accuracy-value').textContent = `${metrics.accuracy}%`;

    // Classification report table
    const report = metrics.report;
    const labels = metrics.labels;
    let tableHtml = `<table class="metric-table">
        <thead><tr><th>Label</th><th>Precision</th><th>Recall</th><th>F1-Score</th><th>Support</th></tr></thead><tbody>`;
    labels.forEach(label => {
        if (report[label]) {
            const r = report[label];
            tableHtml += `<tr>
                <td><span class="badge badge-${label}">${label}</span></td>
                <td>${(r.precision * 100).toFixed(1)}%</td>
                <td>${(r.recall * 100).toFixed(1)}%</td>
                <td>${(r['f1-score'] * 100).toFixed(1)}%</td>
                <td>${r.support}</td>
            </tr>`;
        }
    });
    tableHtml += `</tbody></table>
        <div style="margin-top:12px;font-size:13px;color:var(--text-secondary)">
            Train: <strong>${metrics.train_size}</strong> data &nbsp;|&nbsp; Test: <strong>${metrics.test_size}</strong> data
        </div>`;
    document.getElementById('metric-details').innerHTML = tableHtml;

    // Confusion matrix
    const cm = metrics.confusion_matrix;
    const cmLabels = metrics.labels;
    const cols = cmLabels.length + 1;
    let cmHtml = `<div class="cm-cell cm-header">Actual ↓ Pred →</div>`;
    cmLabels.forEach(l => { cmHtml += `<div class="cm-cell cm-header">${l}</div>`; });
    cm.forEach((row, i) => {
        cmHtml += `<div class="cm-cell cm-header">${cmLabels[i]}</div>`;
        row.forEach((val, j) => {
            const cls = i === j ? 'cm-diagonal' : 'cm-value';
            cmHtml += `<div class="cm-cell ${cls}">${val}</div>`;
        });
    });
    const matrix = document.getElementById('confusion-matrix');
    matrix.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
    matrix.innerHTML = cmHtml;
}

// ===== Update Stats =====
async function updateStats() {
    try {
        const res = await fetch('/train');
        const html = await res.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        ['stat-total', 'stat-positif', 'stat-netral', 'stat-negatif'].forEach(id => {
            const el = doc.getElementById(id);
            if (el) document.getElementById(id).textContent = el.textContent;
        });
    } catch (e) { /* silent */ }
}
