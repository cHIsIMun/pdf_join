import os
import time
import zipfile
from PyPDF2 import PdfReader, PdfWriter

def extract_and_merge_pdfs(zip_path, output_pdf_path):
    temp_dir = 'temp_pdf'
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    pdf_writer = PdfWriter()

    for item in os.listdir(temp_dir):
        if item.endswith('.pdf'):
            pdf_path = os.path.join(temp_dir, item)
            pdf_reader = PdfReader(pdf_path)
            for page in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page])

    with open(output_pdf_path, 'wb') as out:
        pdf_writer.write(out)

    for item in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, item))
    os.rmdir(temp_dir)

def main():
    processed_files = set()
    zip_log = './ZIP_FILES/zip_log.txt'

    # Carregar os arquivos já processados do log
    if os.path.exists(zip_log):
        with open(zip_log, 'r') as file:
            processed_files.update(file.read().splitlines())

    while True:
        for zip_file in os.listdir('./ZIP_FILES'):
            if zip_file.endswith('.zip') and zip_file not in processed_files:
                zip_file_path = f'./ZIP_FILES/{zip_file}'
                output_pdf_path = f'./PDF_FILES/{zip_file.replace(".zip", ".pdf")}'
                extract_and_merge_pdfs(zip_file_path, output_pdf_path)

                with open(zip_log, 'a') as file:
                    file.write(zip_file + '\n')
                processed_files.add(zip_file)

        # Verificar novos arquivos a cada 60 segundos
        time.sleep(2)

if __name__ == '__main__':
    main()
