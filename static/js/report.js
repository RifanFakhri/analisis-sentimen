/**
 * Report Page JavaScript
 * Load and display sentiment analysis report data
 */

document.addEventListener('DOMContentLoaded', function() {
    loadReportData();
});

async function loadReportData() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (!data.summary || !data.metrics) {
            console.error('Invalid data format:', data);
            showEmptyState();
            return;
        }
        
        updateSummaryCards(data.summary);
        updateDistributionTab(data.summary);
        updateDetailsTab(data);
        
    } catch (error) {
        console.error('Error loading report data:', error);
        showEmptyState();
    }
}

function updateSummaryCards(summary) {
    // Total Dataset
    const totalElements = document.querySelectorAll('.summary-card p[style*="28px"]');
    if (totalElements[0]) {
        totalElements[0].textContent = summary.total_reviews || 0;
    }
    
    // Positif
    if (totalElements[1]) {
        totalElements[1].textContent = summary.pos_count || 0;
    }
    
    // Netral
    if (totalElements[2]) {
        totalElements[2].textContent = summary.netral_count || 0;
    }
    
    // Negatif
    if (totalElements[3]) {
        totalElements[3].textContent = summary.neg_count || 0;
    }
}

function updateDistributionTab(summary) {
    const positifPercent = summary.pos_percent || 0;
    const netralPercent = summary.netral_percent || 0;
    const negatifPercent = summary.neg_percent || 0;
    
    // Update atau buat elemen untuk distribusi
    let distributionContent = document.getElementById('distribution-content');
    if (distributionContent) {
        distributionContent.innerHTML = `
            <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 8px;">
                <h3 style="margin-top: 0;">Distribusi Sentimen</h3>
                <p style="opacity: 0.7; margin-bottom: 1.5rem;">Persentase data berdasarkan klasifikasi sentimen</p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 32px; font-weight: 700; color: #10b981; margin-bottom: 0.5rem;">${positifPercent.toFixed(1)}%</div>
                        <p style="margin: 0; opacity: 0.8;">Positif (${summary.pos_count} data)</p>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; font-weight: 700; color: #f59e0b; margin-bottom: 0.5rem;">${netralPercent.toFixed(1)}%</div>
                        <p style="margin: 0; opacity: 0.8;">Netral (${summary.netral_count} data)</p>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; font-weight: 700; color: #ef4444; margin-bottom: 0.5rem;">${negatifPercent.toFixed(1)}%</div>
                        <p style="margin: 0; opacity: 0.8;">Negatif (${summary.neg_count} data)</p>
                    </div>
                </div>
                
                <!-- Progress Bars -->
                <div style="margin-top: 2rem;">
                    <div style="margin-bottom: 1.5rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="opacity: 0.8;">Positif</span>
                            <span style="color: #10b981;">${positifPercent.toFixed(1)}%</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #10b981, #34d399); height: 100%; width: ${positifPercent}%; transition: width 0.5s ease;"></div>
                        </div>
                    </div>
                    <div style="margin-bottom: 1.5rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="opacity: 0.8;">Netral</span>
                            <span style="color: #f59e0b;">${netralPercent.toFixed(1)}%</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #f59e0b, #fbbf24); height: 100%; width: ${netralPercent}%; transition: width 0.5s ease;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="opacity: 0.8;">Negatif</span>
                            <span style="color: #ef4444;">${negatifPercent.toFixed(1)}%</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #ef4444, #f87171); height: 100%; width: ${negatifPercent}%; transition: width 0.5s ease;"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

function updateDetailsTab(data) {
    let detailsContent = document.getElementById('details-content');
    if (!detailsContent) return;
    
    const trainingData = data.samples || [];
    console.log('Training data:', trainingData);
    console.log('Data received:', data);
    
    if (!Array.isArray(trainingData) || trainingData.length === 0) {
        detailsContent.innerHTML = `
            <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 8px; overflow-x: auto;">
                <h3 style="margin-top: 0;">Sampel Data Hasil Klasifikasi</h3>
                <p style="opacity: 0.7; margin-bottom: 1.5rem;">Contoh data dari setiap kategori sentimen</p>
                <div style="text-align: center; padding: 2rem; opacity: 0.6;">
                    Belum ada data untuk ditampilkan
                </div>
            </div>
        `;
        return;
    }
    
    // Generate table rows
    let tableHTML = `
        <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 8px; overflow-x: auto;">
            <h3 style="margin-top: 0;">Sampel Data Hasil Klasifikasi</h3>
            <p style="opacity: 0.7; margin-bottom: 1.5rem;">Contoh data dari setiap kategori sentimen</p>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <thead>
                    <tr style="border-bottom: 2px solid rgba(255,255,255,0.2);">
                        <th style="text-align: left; padding: 1rem; color: rgba(255,255,255,0.8); width: 60%;">Teks</th>
                        <th style="text-align: center; padding: 1rem; color: rgba(255,255,255,0.8); width: 20%;">Sentimen</th>
                        <th style="text-align: center; padding: 1rem; color: rgba(255,255,255,0.8); width: 20%;">Kepercayaan</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    trainingData.forEach((sample, index) => {
        // Handle both object and string formats
        let sampleText = '';
        let sampleSentiment = 'netral';
        let sampleConfidence = 0;
        
        if (typeof sample === 'object' && sample !== null) {
            sampleText = sample.text || '';
            sampleSentiment = (sample.sentiment || 'netral').toLowerCase();
            sampleConfidence = (sample.confidence || 0);
        } else {
            sampleText = sample.toString();
        }
        
        const text = (sampleText).substring(0, 100);
        const sentiment = sampleSentiment;
        const confidence = ((sampleConfidence || 0) * 100).toFixed(1);
        
        let sentimentColor = '#10b981';
        if (sentiment === 'negatif') sentimentColor = '#ef4444';
        if (sentiment === 'netral') sentimentColor = '#f59e0b';
        
        tableHTML += `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 1rem; word-wrap: break-word;">${text}</td>
                <td style="text-align: center; padding: 1rem;"><span style="color: ${sentimentColor}; font-weight: 600;">${sentiment.toUpperCase()}</span></td>
                <td style="text-align: center; padding: 1rem;">${confidence}%</td>
            </tr>
        `;
    });
    
    tableHTML += `
                </tbody>
            </table>
        </div>
    `;
    
    detailsContent.innerHTML = tableHTML;
}

function showEmptyState() {
    const cards = document.querySelectorAll('.summary-card p[style*="28px"]');
    cards.forEach(card => {
        card.textContent = '-';
    });
    
    let distributionContent = document.getElementById('distribution-content');
    if (distributionContent) {
        distributionContent.innerHTML = `
            <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 8px; text-align: center; opacity: 0.6;">
                <p>Data belum tersedia. Silakan latih model terlebih dahulu.</p>
            </div>
        `;
    }
    
    let detailsContent = document.getElementById('details-content');
    if (detailsContent) {
        detailsContent.innerHTML = `
            <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 8px; text-align: center; opacity: 0.6;">
                <p>Data belum tersedia. Silakan latih model terlebih dahulu.</p>
            </div>
        `;
    }
}

// Export Functions
function exportReportPDF() {
    fetch('/api/export-report?format=pdf')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Laporan_Sentimen_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showExportSuccess('PDF');
        })
        .catch(error => {
            console.error('Error exporting PDF:', error);
            showExportError('PDF');
        });
}

function exportReportExcel() {
    fetch('/api/export-report?format=excel')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Laporan_Sentimen_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showExportSuccess('Excel');
        })
        .catch(error => {
            console.error('Error exporting Excel:', error);
            showExportError('Excel');
        });
}

function exportReportCSV() {
    fetch('/api/export-report?format=csv')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Laporan_Sentimen_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showExportSuccess('CSV');
        })
        .catch(error => {
            console.error('Error exporting CSV:', error);
            showExportError('CSV');
        });
}

function showExportSuccess(format) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'success',
            title: 'Berhasil!',
            text: `Laporan ${format} berhasil diunduh.`,
            timer: 3000
        });
    } else {
        alert(`Laporan ${format} berhasil diunduh.`);
    }
}

function showExportError(format) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'error',
            title: 'Gagal!',
            text: `Gagal mengunduh laporan ${format}. Silakan coba lagi.`,
            timer: 3000
        });
    } else {
        alert(`Gagal mengunduh laporan ${format}.`);
    }
}
