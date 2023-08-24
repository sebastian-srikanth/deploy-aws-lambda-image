import pdftables_api
import pandas as pd
import base64
import fitz
import os

class Operations:

    def __init__(self) -> None:
        output_folder = 'output'
        self.CUR_WRK_DIR = os.getcwd()
        self.PASSWORD_PROTECTED_PDF_FILES_DIR = 'protected_pdf_files'
        self.DECODED_PDF_FILES_DIR = 'decoded_pdf_files'
        self.EXCEL_FILES_DIR = 'excel_files'
        self.FINAL_CSV_DIR = 'csv_files'

        # Check if output dir exists first, if not, create the folder
        directories = [
            [self.CUR_WRK_DIR, output_folder],
            [self.CUR_WRK_DIR, output_folder, self.PASSWORD_PROTECTED_PDF_FILES_DIR],
            [self.CUR_WRK_DIR, output_folder, self.DECODED_PDF_FILES_DIR],
            [self.CUR_WRK_DIR, output_folder, self.EXCEL_FILES_DIR],
            [self.CUR_WRK_DIR, output_folder, self.FINAL_CSV_DIR],
        ]
        for dir in directories:
            if not os.path.exists(os.path.join("/".join(dir))):
                os.mkdir(os.path.join("/".join(dir)))
            self.OUTPUT_DIR = os.path.join(self.CUR_WRK_DIR,output_folder)

    def extract_pdf_from_message(self, message, gmail_service):
        msg = gmail_service.users().messages().get(userId='me', id=message['id']).execute()
        for part in msg['payload']['parts']:
            if part['filename'] and part['filename'].endswith('.pdf'):
                attachment_id = part['body']['attachmentId']
                attachment = gmail_service.users().messages().attachments().get(userId='me', messageId=message['id'], id=attachment_id).execute()
                # Decode and save attachment
                file_data = base64.urlsafe_b64decode(attachment['data'])
                file_name = part['filename']
                return file_name, file_data

    def save_the_attachment(self, file_name, file_data):
        output_path = os.path.join(self.OUTPUT_DIR,self.PASSWORD_PROTECTED_PDF_FILES_DIR,file_name)
        with open(output_path, 'wb') as f:
            f.write(file_data)
        print(f'Saved attachment: {file_name}')

    def decode_pdf_with_password(self, file_name):
        input_path = os.path.join(self.OUTPUT_DIR,self.PASSWORD_PROTECTED_PDF_FILES_DIR,file_name)
        output_path = os.path.join(self.OUTPUT_DIR,self.DECODED_PDF_FILES_DIR,file_name)
        PDF_PASSWORD = os.getenv('BANK_STMNT_PDF_PASSWORD')
        
        pdf = fitz.open(input_path)

        if pdf.authenticate(PDF_PASSWORD):
            pdf.save(output_path)
            if pdf.save:
                print("PDF decrypted")

    def convert_to_excel(self, file_name):
        input_path = os.path.join(self.OUTPUT_DIR,self.DECODED_PDF_FILES_DIR,file_name)
        excel_file_name = file_name.split('.')[0] + '.xlsx'
        output_path = os.path.join(self.OUTPUT_DIR,self.EXCEL_FILES_DIR,excel_file_name)

        # using pdfTables API
        API_KEY = os.getenv("PDF_TABLES_API_KEY")
        c = pdftables_api.Client(API_KEY)
        c.xlsx(input_path, output_path)

    def convert_to_csv(self, file_name):
        # Provide the path to your Excel file
        excel_file_path = os.path.join(self.OUTPUT_DIR,self.EXCEL_FILES_DIR,file_name)

        dfs = pd.read_excel(excel_file_path,sheet_name=None)

        # Create an empty list to store DataFrames
        all_dataframes = []

        for sheet_name, df in dfs.items():
            try:
                # Find the index where "DATE" is located in the first column
                start_index = df[df.iloc[:,0].str.contains("DATE", case=False, na=False)].index[0]

                # Find the index where "Total:" is located in the first column
                end_index = df[df.iloc[:,0].str.contains("Total:", case=False, na=False)].index[0]
                filtered_df = df.iloc[start_index:end_index+1]
            except IndexError as e:
                print("Warning: Index error arrived may be no record found for last page")

            # Append the filtered DataFrame to the list
            all_dataframes.append(filtered_df)

        # Combine all DataFrames into a single DataFrame
        combined_df = pd.concat(all_dataframes, ignore_index=True)

        # Save the clean file as csv file
        combined_df.to_csv('output.csv', sep='|', header=False, index=False)

        # Save the clean file as excel for review
        combined_df.to_excel('cleaned_output.xlsx',header=False, index=False)
