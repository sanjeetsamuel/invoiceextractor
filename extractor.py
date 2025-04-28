import pypdf
import re

def extract_text_from_pdf(file_path):
    text = ""
    try:
        # Open the PDF file
        with open(file_path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = pypdf.PdfReader(file)
            
            # Process each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text


def extract_invoice_fields(text):
    fields = {}

    # Each field has multiple patterns to try
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


def process_invoice(file_path):
    text = extract_text_from_pdf(file_path)
    fields = extract_invoice_fields(text)
    return fields

if __name__ == "__main__":
    file_path = "invoice.pdf"
    invoice_data = process_invoice(file_path)
    
    for key, value in invoice_data.items():
        print(f"{key}: {value}")
