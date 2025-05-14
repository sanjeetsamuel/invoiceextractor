import React, { useState } from 'react';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [invoiceData, setInvoiceData] = useState(null);  // to store extracted fields
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setInvoiceData(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
  
    const formData = new FormData();
    formData.append('file', selectedFile);
  
    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
  
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Upload failed:', errorText);
        setError('Upload failed.');
        return;
      }
  
      const data = await response.json();
      setInvoiceData(data.extracted_fields);
    } catch (err) {
      console.error('Error uploading file:', err);
      setError('Error uploading file.');
    }
  };

  const handleDownloadCSV = async () => {
    if (!selectedFile) return;
  
    const formData = new FormData();
    formData.append('file', selectedFile);
  
    try {
      const response = await fetch('http://localhost:8000/upload-csv', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'invoice_data.csv';
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        setError('CSV download failed.');
      }
    } catch (err) {
      setError('Error downloading CSV.');
      console.error(err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Invoice Uploader</h1>
      </header>

      <input type="file" accept=".pdf" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!selectedFile}>Upload</button>

      {selectedFile && (
        <div>
          <p><strong>Filename:</strong> {selectedFile.name}</p>
          <p><strong>Size:</strong> {selectedFile.size} bytes</p>
        </div>
      )}

      {invoiceData && (
        <div style={{ marginTop: '1em' }}>
          <h3>Extracted Invoice Fields:</h3>
          <ul>
            {Object.entries(invoiceData).map(([key, value]) => (
              <li key={key}><strong>{key}:</strong> {value || 'Not found'}</li>
            ))}
          </ul>
          <button onClick={handleDownloadCSV}>Download CSV</button>
        </div>
      )}


      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default App;

