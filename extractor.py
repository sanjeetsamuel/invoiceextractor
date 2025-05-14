import pypdf
import re
import io
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def extract_text_from_pdf(file_bytes):
    text = ""
    try:
        pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def extract_invoice_fields(text):
    fields = {}

    fields['Invoice Number'] = find_with_patterns(text, [
        r'Invoice\s*No\.?:?\s*([A-Z0-9-]+)',
        r'Invoice\s*Number\s*:?\s*([A-Z0-9-]+)',
        r'No\.?\s*([A-Z0-9-]+)'
    ])

    fields['Invoice Date'] = find_with_patterns(text, [
        r'Invoice\s*Date\s*:?\s*(\d{2}[./-]\d{2}[./-]\d{4})',
        r'Invoice\s*Date\s*:?\s*(\d{4}[./-]\d{2}[./-]\d{2})',
        r'Date\s*:?\s*(\d{2}[./-]\d{2}[./-]\d{4})',
        r'Date\s*:?\s*(\d{4}[./-]\d{2}[./-]\d{2})'
    ])

    fields['Vendor Name'] = find_with_patterns(text, [
        r'Issued\s*To:?\s*(.+)',
        r'Bill\s*To:?\s*(.+)',
        r'Customer\s*Name:?\s*(.+)',
        r'Vendor\s*Name:?\s*(.+)',
        r'Vendor\s*:?\s*(.+)'
    ])

    fields['Amount Due'] = find_with_patterns(text, [
        r'Amount\s*Due\s*:?\s*([$]?\d+[.,]?\d*)',
        r'Total\s*Due\s*:?\s*([$]?\d+[.,]?\d*)',
        r'Total\s*:?\s*([$]?\d+[.,]?\d*)',
        r'Total\s*Amount\s*Due\s*:?\s*([$]?\d+[.,]?\d*)'
    ])

    return fields

def find_with_patterns(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_bytes = await file.read()
    extracted_text = extract_text_from_pdf(file_bytes)
    fields = extract_invoice_fields(extracted_text)

    return JSONResponse(content={
        "filename": file.filename,
        "extracted_fields": fields
    })


from fastapi.responses import StreamingResponse
import csv
import io

@app.post("/upload-csv")
async def upload_and_return_csv(file: UploadFile = File(...)):
    file_bytes = await file.read()
    extracted_text = extract_text_from_pdf(file_bytes)
    fields = extract_invoice_fields(extracted_text)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields.keys())
    writer.writeheader()
    writer.writerow(fields)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=invoice_data.csv"}
    )