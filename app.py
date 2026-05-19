from flask import Flask, request, jsonify
import re
import PyPDF2
import requests
from io import BytesIO

app = Flask(__name__)

# ===============================
# CORE HELPERS (FROM YOUR CODE)
# ===============================

def extract_field(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else ''


def extract_pdf_text(file_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(file_bytes)
        text = ""

        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        return text

    except Exception as e:
        return ""


def extract_iv_data(text):

    data = {}

    data['Date'] = extract_field(text, r'Date:\s*([^\n]+)')
    data['Dt'] = extract_field(text, r'Dt:\s*([^\n]+)')
    data['Issue No'] = extract_field(text, r'Issue No:\s*([^\n]+)')
    data['Status'] = extract_field(text, r'Status:\s*([^\n]+)')
    data['Indent No'] = extract_field(text, r'Indent No:\s*([^\n]+)')
    data['Indent Dt'] = extract_field(text, r'Indent Dt:\s*([^\n]+)')
    data['Remarks'] = extract_field(text, r'Remarks:\s*([^\n]+)')

    store_match = re.search(r'AV Store \((.*?)\)', text)
    data['Store Location'] = store_match.group(1) if store_match else ''

    data['Document Type'] = 'IV'

    return data


# ===============================
# HEALTH CHECK
# ===============================
@app.route('/')
def home():
    return "Python PDF API Running"


# ===============================
# MAIN PDF PROCESSING API
# ===============================
@app.route('/process-pdf', methods=['POST'])
def process_pdf():

    try:
        data = request.json
        pdf_url = data.get("pdf_url")

        if not pdf_url:
            return jsonify({"error": "No PDF URL provided"}), 400

        # download PDF from Google Drive / URL
        response = requests.get(pdf_url)
        file_bytes = BytesIO(response.content)

        # extract text
        text = extract_pdf_text(file_bytes)

        if not text:
            return jsonify({"error": "Could not read PDF"}), 500

        # extract data
        result = extract_iv_data(text)

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)