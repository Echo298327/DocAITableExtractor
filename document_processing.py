"""
document_processing.py Overview

Functions:

1. online_process Function:
   - Purpose: Processes a document using Google Cloud's Document AI Online Processing API.
     It extracts tables and their titles from the document.
   - Parameters:
     - project_id (str): The Google Cloud Project ID.
     - location (str): The location/region of the Document AI processor.
     - processor_id (str): The ID of the Document AI processor to use.
     - file_path (str): The local path to the document file.
     - mime_type (str): The MIME type of the document.
   - Returns: A tuple containing the processed Document AI Document object and a list of extracted table titles.
   - How it Works:
     - Initializes a Document AI client.
     - Constructs the full resource name of the processor.
     - Reads the document file and converts it into a binary format.
     - Sends a request to Document AI to process the document.
     - Iterates through pages and tables in the document, finding the closest text preceding each table, assumed to be
        the table's title.

2. get_table_data Function:
   - Purpose: Extracts the textual data from the rows of a table in a Document AI Document.
   - Parameters:
     - rows (Sequence[documentai.Document.Page.Table.TableRow]): The rows of a table.
     - text (str): The entire text of the document.
   - Returns: A list of lists, where each inner list contains the text of each cell in a row.
   - How it Works:
     - Iterates through each row and cell in the given table rows.
     - For each cell, extracts the text based on its position in the document using the text_anchor_to_text function.

3. text_anchor_to_text Function:
   - Purpose: Converts text anchors (positions of text in the document) to actual text strings.
   - Parameters:
     - text_anchor (documentai.Document.TextAnchor): The text anchor object.
     - text (str): The entire text of the document.
   - Returns: A string extracted from the document based on the given text anchor's positions.
   - How it Works:
     - Goes through each text segment in the text anchor.
     - Extracts the text from the document based on the start and end indices of each segment.
     - Combines these text pieces, removing line breaks and returning a clean, concatenated string.
"""
from typing import List, Sequence, Tuple
from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai


def online_process(
        project_id: str,
        location: str,
        processor_id: str,
        file_path: str,
        mime_type: str,
) -> Tuple[documentai.Document, List[str]]:
    """
    Processes a document using the Document AI Online Processing API and extracts table titles.
    """
    # Instantiates a client
    docai_client = documentai.DocumentProcessorServiceClient(
        client_options=ClientOptions(
            api_endpoint=f"{location}-documentai.googleapis.com"
        )
    )

    resource_name = docai_client.processor_path(project_id, location, processor_id)

    with open(file_path, "rb") as file:
        file_content = file.read()

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)

    # Configure the process request
    request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)

    # Use the Document AI client to process the sample form
    result = docai_client.process_document(request=request)

    table_titles = []
    for page in result.document.pages:
        for table in page.tables:
            # Find the closest preceding text block to the table
            table_start_y = table.layout.bounding_poly.normalized_vertices[0].y
            closest_preceding_text = ""
            min_distance = float('inf')
            for paragraph in page.paragraphs:
                paragraph_end_y = paragraph.layout.bounding_poly.normalized_vertices[2].y
                distance = table_start_y - paragraph_end_y
                if 0 < distance < min_distance:
                    min_distance = distance
                    closest_preceding_text = text_anchor_to_text(paragraph.layout.text_anchor, result.document.text)
            table_titles.append(closest_preceding_text)

    return result.document, table_titles


def get_table_data(
        rows: Sequence[documentai.Document.Page.Table.TableRow], text: str
) -> List[List[str]]:
    """
    Get Text data from table rows
    """
    all_values: List[List[str]] = []
    for row in rows:
        current_row_values: List[str] = []
        for cell in row.cells:
            current_row_values.append(
                text_anchor_to_text(cell.layout.text_anchor, text)
            )
        all_values.append(current_row_values)
    return all_values


def text_anchor_to_text(text_anchor: documentai.Document.TextAnchor, text: str) -> str:
    """
    Document AI identifies table data by their offsets in the entirity of the
    document's text. This function converts offsets to a string.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in text_anchor.text_segments:
        start_index = int(segment.start_index)
        end_index = int(segment.end_index)
        response += text[start_index:end_index]
    return response.strip().replace("\n", " ")
