async function apiFetch(url, opts={}){
  const res = await fetch(url, opts);
  if(!res.ok) throw new Error((await res.json()).error || 'HTTP error');
  return res.json();
}

// Dummy preview behavior for prototype
function handleFileSelect(input){
  const label = document.getElementById('file-name');
  if(input.files && input.files[0]) label.textContent = input.files[0].name;
}

function predictPrototype(){
  const text = document.getElementById('input-text').value.trim();
  if(!text){alert('Masukkan teks terlebih dahulu');return}
  // Simple heuristics demo
  const lower = text.toLowerCase();
  let sentiment='netral';
  if(/(bagus|mantap|bagus|baik|recommended|love)/.test(lower)) sentiment='positif';
  if(/(buruk|jelek|tidak|problem|sampah|mahal|mengecewakan)/.test(lower)) sentiment='negatif';
  const prob = sentiment==='positif'? 85 : sentiment==='negatif'? 78: 62;
  document.getElementById('sentiment-label').textContent = sentiment.toUpperCase();
  const badge = document.getElementById('sentiment-badge');
  badge.className = 'badge '+sentiment;
  document.getElementById('confidence').textContent = prob + '%';
  document.getElementById('preproc').textContent = 'case folding -> cleaning -> normalize -> tokenize -> stemming';
}

document.addEventListener('DOMContentLoaded', ()=>{
  const fileInput = document.getElementById('csv-file');
  if(fileInput) fileInput.addEventListener('change', ()=>handleFileSelect(fileInput));
});