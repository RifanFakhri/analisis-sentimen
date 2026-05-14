// ===== Character Count =====
const inputText = document.getElementById('input-text');
const charCount = document.getElementById('char-count');
if (inputText) {
    inputText.addEventListener('input', () => {
        charCount.textContent = `${inputText.value.length} / 2000`;
    });
}

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

// ===== Predict Sentiment =====
async function predictSentiment() {
    const text = document.getElementById('input-text').value.trim();
    if (!text) { showToast('Masukkan teks terlebih dahulu.', 'error'); return; }

    const loading = document.getElementById('loading-state');
    const error = document.getElementById('error-state');
    const result = document.getElementById('result-section');
    const btn = document.getElementById('btn-predict');

    loading.classList.remove('hidden');
    error.classList.add('hidden');
    result.classList.add('hidden');
    btn.disabled = true;

    try {
        const data = await apiFetch('/predict', {
            method: 'POST',
            body: JSON.stringify({ text }),
        });

        loading.classList.add('hidden');
        displayResult(data.result);
        result.classList.remove('hidden');
        result.scrollIntoView({ behavior: 'smooth', block: 'start' });
        showToast('Analisis sentimen berhasil!');
    } catch (err) {
        loading.classList.add('hidden');
        error.classList.remove('hidden');
        document.getElementById('error-text').textContent = err.message;
    } finally {
        btn.disabled = false;
    }
}

// ===== Display Result =====
function displayResult(result) {
    // Sentiment badge
    const badge = document.getElementById('sentiment-badge');
    const icon = document.getElementById('sentiment-icon');
    const label = document.getElementById('sentiment-label');

    badge.className = `sentiment-badge ${result.sentiment}`;
    const icons = { positif: 'fas fa-smile', negatif: 'fas fa-frown', netral: 'fas fa-meh' };
    const labels = { positif: 'POSITIF', negatif: 'NEGATIF', netral: 'NETRAL' };
    icon.className = `sentiment-icon ${icons[result.sentiment]}`;
    label.textContent = labels[result.sentiment];

    // Confidence ring
    const conf = result.confidence;
    const fill = document.getElementById('confidence-fill');
    const circumference = 2 * Math.PI * 54; // r=54
    const offset = circumference - (conf / 100) * circumference;
    fill.style.strokeDasharray = circumference;
    setTimeout(() => { fill.style.strokeDashoffset = offset; }, 100);
    document.getElementById('confidence-value').textContent = `${conf}%`;

    // Probability bars
    const probs = result.probabilities;
    ['positif', 'netral', 'negatif'].forEach(s => {
        const val = probs[s] || 0;
        document.getElementById(`prob-${s}`).textContent = `${val}%`;
        document.getElementById(`prob-bar-${s}`).style.width = '0%';
        setTimeout(() => {
            document.getElementById(`prob-bar-${s}`).style.width = `${val}%`;
        }, 200);
    });

    // Preprocessing steps
    const steps = result.preprocessing;
    const container = document.getElementById('steps-container');
    const stepData = [
        { label: 'Case Folding', value: steps.case_folding },
        { label: 'Cleaning', value: steps.cleaning },
        { label: 'Normalisasi', value: steps.normalization },
        { label: 'Tokenisasi', value: Array.isArray(steps.tokenization) ? steps.tokenization.join(', ') : steps.tokenization },
        { label: 'Stopword Removal', value: Array.isArray(steps.stopword_removal) ? steps.stopword_removal.join(', ') : steps.stopword_removal },
        { label: 'Stemming', value: Array.isArray(steps.stemming) ? steps.stemming.join(', ') : steps.stemming },
    ];

    container.innerHTML = stepData.map((s, i) => `
        <div class="step-item">
            <div class="step-number">${i + 1}</div>
            <div>
                <div class="step-label">${s.label}</div>
                <div class="step-content">${s.value || '<em>-</em>'}</div>
            </div>
        </div>
    `).join('');
}

// Enter key support
if (inputText) {
    inputText.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); predictSentiment(); }
    });
}
