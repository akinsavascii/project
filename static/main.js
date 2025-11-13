const form = document.getElementById('uploadForm')
const resultDiv = document.getElementById('result')

form.addEventListener('submit', async (e) => {
  e.preventDefault()
  const fileInput = document.getElementById('fileInput')
  if (!fileInput.files.length) return alert('Lütfen bir dosya seçin')
  const formData = new FormData()
  formData.append('file', fileInput.files[0])
  const length = document.getElementById('length').value
  formData.append('length', length)

  resultDiv.innerText = 'Yükleniyor ve işleniyor... Lütfen bekleyin.'

  try {
    const resp = await fetch('/upload', {
      method: 'POST',
      body: formData
    })
    const json = await resp.json()
    console.log('Response:', json)
    if (!resp.ok) {
      resultDiv.innerText = 'Hata: ' + (json.details || json.error || JSON.stringify(json))
      console.error('Error details:', json)
      return
    }
    
    const summary = json.summary_text || 'Özet hazırlanmış.'
    
    // Show summary and PDF download button
    resultDiv.innerHTML = `
      <div style="margin: 20px 0; padding: 15px; border: 1px solid #ccc; border-radius: 5px;">
        <h3>Özet:</h3>
        <p style="white-space: pre-wrap; font-family: Arial;">${escapeHtml(summary)}</p>
        <button id="downloadBtn" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
          PDF Olarak İndir
        </button>
      </div>
    `
    
    // Add PDF download handler
    document.getElementById('downloadBtn').addEventListener('click', () => {
      const element = resultDiv.querySelector('p')
      const opt = {
        margin: 10,
        filename: 'ozet.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { orientation: 'portrait', unit: 'mm', format: 'a4' }
      }
      html2pdf().set(opt).from(element).save()
    })
    
  } catch (err) {
    console.error('Fetch error:', err)
    resultDiv.innerText = 'Sunucuya bağlanırken hata oluştu: ' + err.message
  }
})

function escapeHtml(text) {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}
