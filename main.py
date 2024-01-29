import os
import time
import zipfile
import shutil
from PyPDF2 import PdfReader, PdfWriter

def add_pdfs_to_zip(pdf_paths, zip_path):
    with zipfile.ZipFile(zip_path, 'a') as zipf:
        for pdf in pdf_paths:
            zipf.write(pdf, os.path.basename(pdf))

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

def process_documents(doc_folder, zip_folder, output_pdf_folder, log_file):
    processed_zips = set()
    # Carregar os arquivos já processados do log
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            processed_zips.update(file.read().splitlines())

    while True:
        file_groups = {}
        for file in os.listdir(doc_folder):
            if file.endswith('.pdf') and file not in processed_zips:
                parts = file[:-4].split('-')
                if len(parts) == 2:
                    doc_type, name = parts
                    if name not in file_groups:
                        file_groups[name] = []
                    file_groups[name].append(file)

        for name, files in file_groups.items():
            if len(files) == 2:  # Se ambos os arquivos (TERMO e LAUDO) estiverem presentes
                zip_name = f"DOSSIE-{name}.zip"
                zip_path = os.path.join(doc_folder, zip_name)
                if os.path.exists(zip_path) and zip_name not in processed_zips:
                    add_pdfs_to_zip([os.path.join(doc_folder, f) for f in files], zip_path)
                    new_zip_path = os.path.join(zip_folder, f"{name}.zip")
                    shutil.copy2(zip_path, new_zip_path)  # Copia o ZIP para a pasta ZIP_FILES
                    output_pdf_path = os.path.join(output_pdf_folder, f"{name}.pdf")
                    extract_and_merge_pdfs(new_zip_path, output_pdf_path)
                    processed_zips.add(zip_name)

                    # Atualizar o arquivo de log
                    with open(log_file, 'a') as log:
                        log.write(zip_name + '\n')

        time.sleep(2)


if __name__ == '__main__':
    DOCUMENTS_FOLDER = '../../Documentos'
    ZIP_FOLDER = './ZIP_FILES'
    OUTPUT_PDF_FOLDER = './PDF_FILES'
    LOG_FILE = './processed_zips.log'
    process_documents(DOCUMENTS_FOLDER, ZIP_FOLDER, OUTPUT_PDF_FOLDER, LOG_FILE)