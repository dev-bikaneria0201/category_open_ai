


import openai
from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os
import logging

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = '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'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text


def summarize_paragraph(user_text):
    prompt = f"which type of document it is answer in one word 1. Legal Documents: Documents related to legal contracts, agreements, court cases, or any content associated with the legal domain.\n2. Medical Records: Patient records, medical reports, prescriptions, and other healthcare-related documents fall into this category.\n3. Financial Statements: Documents containing financial data, such as balance sheets, income statements, and financial reports.\n4. Educational Materials: Textbooks, academic papers, lesson plans, and any content related to education and learning.\n5. Business Correspondence: Emails, business letters, and other communication documents related to corporate affairs and professional interactions.\n6. News Articles: Articles, press releases, and news reports covering current events and news from various sources.\n7. Technical Manuals: Instruction manuals, technical guides, and documentation providing information about the operation or use of a product or system.\n8. Creative Writing: Fictional works, poetry, creative essays, and any content created for artistic expression.\n9. Scientific Research Papers: Documents reporting on scientific experiments, research findings, and academic papers in various scientific disciplines.\n10. Government Documents: Documents released by government agencies, including policies, regulations, and official reports. :\n{user_text}\n"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    summary = response['choices'][0]['message']['content']

    return summary


    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    summary = response['choices'][0]['message']['content']

    return summary




@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files and request.files['file']:
            # User uploaded a file
            pdf_file = request.files['file']
            if pdf_file and allowed_file(pdf_file.filename):
                # Save the uploaded PDF temporarily
                pdf_file_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
                pdf_file.save(pdf_file_path)

                # Extract text from the PDF
                user_text = extract_text_from_pdf(pdf_file_path)

                # Close the file after extracting text
                pdf_file.close()

                # Delete the temporary PDF file
                os.remove(pdf_file_path)
            else:
                return "Invalid file type. Please upload a PDF file."
        else:
            # User entered text directly
            user_text = request.form.get('user_text', '')

        logging.debug(f"User text: {user_text}")

        

        summary = summarize_paragraph(user_text)
        logging.debug(f"Summary: {summary}")

        return render_template('index.html',
                               user_text=user_text,
                               
                               summary=summary)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    # Create the 'uploads' folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    app.run(debug=True)
