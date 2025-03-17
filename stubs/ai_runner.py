import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils.call_ai as ai
    

# Example usage
if __name__ == "__main__":
    prompt = """
        Extract the table in the document as a CSV with header followed by data.
        Use the '|' character as your CSV separator instead of comma, ','.
        Keep the empty cells, but don't put zeros in them.
        Make sure all rows in the CSV have the same number of cells.

        Extract cells as numbers, not text, when possible.
        For example, extract "$10,000.00" as 10000.00 and "20%" as 20.
        Be extra careful to identify % columns, recognizing % characters.
        Our single table may span multiple tables on multiple pages: append them all together into a single table.
        Do not extract text outside the CSV.
        Do not add any explanatory text outside of the CSV.
    """
    
    data_dir = "data/Loss Run"

    # # file_path = "Company 1 - Cargo Chart.pdf"
    # # file_path = "Company 3 - Loss Run.pdf"
    # file_path = "Company 1 - Loss Run 11 13 2024.pdf"
    # file_blob = read_file(os.path.join(data_dir, file_path))
    # # result = mistral_extract_text_ocr(file_blob, os.path.basename(file_path))  # , prompt)
    # result = gemini_extract_text(file_blob, os.path.basename(file_path), prompt)  # openai_extract_text
    # result = process_csv(result)
    # print(result)

    for file_name in os.listdir(data_dir):
        if not file_name.lower().endswith(".pdf"):
            continue
        
        file_path = os.path.join(data_dir, file_name)
        file_blob = ai.read_file(file_path)
 
        # Process the document
        result = ai.gemini_extract_text(file_blob, file_name, prompt)
        result = ai.post_process_csv(result)
        
        # Define the CSV output filename
        output_file_name = os.path.splitext(file_name)[0] + ".csv"
        output_file_path = os.path.join(data_dir, output_file_name)
        
        # Save the result to the CSV file
        with open(output_file_path, "w", encoding="utf-8") as csv_file:
            csv_file.write(result)
        
        print(f"Processed and saved: {output_file_path}")