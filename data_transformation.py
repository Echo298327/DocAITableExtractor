"""
data_transformation.py Overview

Functions:

1. transform_and_save_data Function:
   - Purpose: Transforms the extracted table data from a Document AI Document into a structured JSON format and saves
    it to a file.
   - Parameters:
     - document: The Document AI Document object containing the processed document data.
     - table_titles: A list of titles for each table extracted from the document.
   - Function Workflow:
     - Initializes an empty list to store the JSON representation of each table.
     - Iterates through each page and table in the document.
     - Uses get_table_data to extract header and body rows from each table.
     - Creates a Pandas DataFrame with the extracted data.
     - Flattens MultiIndex column headers if present.
     - Converts the DataFrame into a dictionary and adds the corresponding table title.
     - Appends the table's JSON object to a list.
   - Saving to JSON:
     - Writes the list of table JSON objects to a file named 'table_data.json', using json.dump to serialize the data.
"""
from document_processing import get_table_data
import pandas as pd
import json


def transform_and_save_data(document, table_titles):
    json_data = []

    for page in document.pages:
        for i, table in enumerate(page.tables):
            header_row_values = get_table_data(table.header_rows, document.text)
            body_row_values = get_table_data(table.body_rows, document.text)

            # Create a Pandas DataFrame
            df = pd.DataFrame(
                data=body_row_values,
                columns=pd.MultiIndex.from_arrays(header_row_values),
            )

            # Flatten MultiIndex if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]

            # Convert DataFrame to a dictionary and add the table title
            table_data = df.to_dict(orient='records')
            table_json = {
                "Table Title": table_titles[i],
                "Data": table_data
            }
            
            # Append this table's JSON to the list
            json_data.append(table_json)

    # Write the JSON data to a file
    json_file_path = "table_data.json"
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)
