
// ===== Update Training Stats =====
async function updateTrainStats() {
    try {
        const res = await fetch('/api/train-stats');
        const data = await res.json();
        
        // Update stat cards
        document.getElementById('stat-total').textContent = data.total_data;
        document.getElementById('stat-positif').textContent = data.label_stats.positif || 0;
        document.getElementById('stat-netral').textContent = data.label_stats.netral || 0;
        document.getElementById('stat-negatif').textContent = data.label_stats.negatif || 0;
    } catch (e) {
        console.error('Failed to update train stats:', e);
    }
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

        // Update training stats with NB predictions
        await updateTrainStats();

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

// ===== Training Logs =====
async function loadTrainingLogs() {
    const body = document.getElementById('training-logs-body');
    if (!body) return;

    try {
        const response = await fetch('/api/training-logs');
        const logs = await response.json();

        if (logs.length === 0) {
            body.innerHTML = `<tr><td colspan="3" style="text-align: center; padding: 2rem; color: var(--text-muted);">Belum ada riwayat aktivitas.</td></tr>`;
            return;
        }

        body.innerHTML = logs.map(log => `
            <tr>
                <td style="white-space: nowrap; font-size: 0.85rem;">${log.created_at}</td>
                <td>
                    <span class="badge badge-${log.activity_type === 'upload' ? 'warning' : 'success'}">
                        ${log.activity_type.toUpperCase()}
                    </span>
                </td>
                <td style="font-size: 0.9rem;">${log.details}</td>
            </tr>
        `).join('');
    } catch (err) {
        body.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--danger-color);">Gagal memuat riwayat.</td></tr>`;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadTrainingLogs();
});

// Update trainModel to refresh logs
const originalTrainModel = trainModel;
trainModel = async function() {
    await originalTrainModel();
    loadTrainingLogs();
};

// ===== CSV Upload Logic =====
let selectedFile = null;

function handleFileSelect(input) {
    if (input.files && input.files[0]) {
        selectedFile = input.files[0];
        document.getElementById('file-name').textContent = selectedFile.name;
        document.getElementById('btn-upload').classList.remove('hidden');
        document.getElementById('upload-area').style.borderColor = 'var(--accent-color)';
    }
}

async function uploadCSV() {
    if (!selectedFile) return;

    const btn = document.getElementById('btn-upload');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses...';

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/api/upload-dataset', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.success) {
            showToast(data.message);
            // Reload after short delay to update model status in template
            setTimeout(() => window.location.reload(), 1500);
        } else {
            showToast(data.error || 'Gagal mengupload dataset.', 'error');
        }
    } catch (err) {
        showToast('Terjadi kesalahan koneksi.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}
// ===== Reset System =====
async function resetSystem() {
    const result = await Swal.fire({
        title: 'Apakah Anda yakin?',
        text: "Seluruh data training, riwayat, dan model akan dihapus secara permanen!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#475569',
        confirmButtonText: 'Ya, Reset Sekarang!',
        cancelButtonText: 'Batal',
        background: '#1e293b',
        color: '#fff'
    });

    if (result.isConfirmed) {
        try {
            Swal.fire({
                title: 'Sedang Mereset...',
                allowOutsideClick: false,
                didOpen: () => { Swal.showLoading(); }
            });

            const res = await fetch('/api/reset', { method: 'POST' });
            const data = await res.json();
            
            if (res.ok) {
                await Swal.fire({
                    icon: 'success',
                    title: 'Berhasil!',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false
                });
                window.location.reload();
            } else {
                Swal.fire('Gagal!', data.error || 'Gagal meriset sistem', 'error');
            }
        } catch (err) {
            Swal.fire('Error!', 'Terjadi kesalahan koneksi', 'error');
        }
    }
}
