// ===== History State =====
let currentPage = 1;
let currentSearch = '';
let currentFilter = '';
let debounceTimer;

document.addEventListener('DOMContentLoaded', () => loadHistory());

// ===== Load History =====
async function loadHistory() {
    const tbody = document.getElementById('history-tbody');
    const empty = document.getElementById('empty-state');
    const loading = document.getElementById('table-loading');
    const table = document.getElementById('history-table');

    loading.classList.remove('hidden');
    table.querySelector('thead').style.display = 'none';
    tbody.innerHTML = '';
    empty.classList.add('hidden');

    try {
        const params = new URLSearchParams({
            page: currentPage, per_page: 10,
            search: currentSearch, sentiment: currentFilter
        });
        const data = await apiFetch(`/api/history?${params}`);

        loading.classList.add('hidden');

        if (data.data.length === 0) {
            empty.classList.remove('hidden');
            table.querySelector('thead').style.display = 'none';
            document.getElementById('pagination').innerHTML = '';
            return;
        }

        table.querySelector('thead').style.display = '';
        const startNum = (data.current_page - 1) * 10;
        tbody.innerHTML = data.data.map((item, i) => `
            <tr>
                <td>${startNum + i + 1}</td>
                <td class="text-cell" title="${escapeHtml(item.original_text)}">${escapeHtml(item.original_text)}</td>
                <td><span class="badge badge-${item.sentiment}">${item.sentiment}</span></td>
                <td><strong>${item.confidence}%</strong></td>
                <td style="white-space:nowrap">${item.created_at}</td>
                <td>
                    <button class="btn-delete" onclick="deleteHistory(${item.id})" title="Hapus">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        renderPagination(data);
    } catch (err) {
        loading.classList.add('hidden');
        showToast(err.message, 'error');
    }
}

// ===== Pagination =====
function renderPagination(data) {
    const container = document.getElementById('pagination');
    if (data.pages <= 1) { container.innerHTML = ''; return; }

    let html = `<button class="page-btn" onclick="goToPage(${data.current_page - 1})" ${!data.has_prev ? 'disabled' : ''}><i class="fas fa-chevron-left"></i></button>`;
    for (let p = 1; p <= data.pages; p++) {
        html += `<button class="page-btn ${p === data.current_page ? 'active' : ''}" onclick="goToPage(${p})">${p}</button>`;
    }
    html += `<button class="page-btn" onclick="goToPage(${data.current_page + 1})" ${!data.has_next ? 'disabled' : ''}><i class="fas fa-chevron-right"></i></button>`;
    container.innerHTML = html;
}

function goToPage(page) { currentPage = page; loadHistory(); }

// ===== Search & Filter =====
function debounceSearch() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        currentSearch = document.getElementById('search-input').value;
        currentPage = 1;
        loadHistory();
    }, 400);
}

function filterSentiment(btn, sentiment) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = sentiment;
    currentPage = 1;
    loadHistory();
}

// ===== Delete =====
async function deleteHistory(id) {
    if (!confirm('Hapus data ini?')) return;
    try {
        await apiFetch(`/api/history/${id}`, { method: 'DELETE' });
        showToast('Data berhasil dihapus.');
        loadHistory();
    } catch (err) { showToast(err.message, 'error'); }
}

async function clearAllHistory() {
    if (!confirm('Hapus semua histori prediksi?')) return;
    try {
        await apiFetch('/api/history/clear', { method: 'DELETE' });
        showToast('Semua histori berhasil dihapus.');
        loadHistory();
    } catch (err) { showToast(err.message, 'error'); }
}

// ===== Escape HTML =====
function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}
