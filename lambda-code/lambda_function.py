import base64
import os

import dotenv

from google_apis import create_service
from operations import Operations


dotenv.load_dotenv()

CLIENT_FILE = 'client-secret.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']
QUERY_FETCH_ATTACHMENT_FROM = os.getenv('FROM_EMAIL')
PDF_PASSWORD = os.getenv('BANK_STMNT_PDF_PASSWORD')


def handler():
    # create gmail api service
    gmail_service = create_service(CLIENT_FILE, API_NAME, API_VERSION, SCOPES)

    # using gmail api fetch messages
    results = gmail_service.users().messages().list(userId='me', q=QUERY_FETCH_ATTACHMENT_FROM).execute()
    messages = results.get('messages', [])

    # extract the pdf from messages and perform operations
    operate = Operations()
    for message in messages:
        
        # Fetch pdf from message
        filename, filedata = operate.extract_pdf_from_message(message, gmail_service)
        
        # Save file locally
        operate.save_the_attachment(filename, filedata)
        
        # Decode the PDF
        operate.decode_pdf_with_password(filename)
        
        # Convert to Excel
        # operate.convert_to_excel(file_name)
        
        # Excel to CSV
        # operate.convert_to_csv(file_name)
