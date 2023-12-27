from dotenv import load_dotenv
from document_processing import online_process
from data_transformation import transform_and_save_data
import os

load_dotenv()

PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = "us"
PROCESSOR_ID = os.environ.get("PARSER_PROCESSOR_ID")
FILE_PATH = "PdfFiles/demo.pdf"
MIME_TYPE = "application/pdf"

document, table_titles = online_process(
    project_id=PROJECT_ID,
    location=LOCATION,
    processor_id=PROCESSOR_ID,
    file_path=FILE_PATH,
    mime_type=MIME_TYPE,
)

transform_and_save_data(document, table_titles)

# a function that take the json file and return a list of dictionaries

