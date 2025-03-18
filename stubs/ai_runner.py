import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import config
import utils.call_ai as ai
    

# Example usage
if __name__ == "__main__":
    data_dir = "data/Loss Run"
    prompt = config['prompt:ocr']['Prompt']

    # # file_path = "Company 1 - Cargo Chart.pdf"
    # # file_path = "Company 3 - Loss Run.pdf"
    # file_path = "Company 1 - Loss Run 11 13 2024.pdf"
    # file_blob = read_file(os.path.join(data_dir, file_path))
    # # result = mistral_extract_text_ocr(file_blob, os.path.basename(file_path))  # , prompt)
    # result = gemini_extract_text(file_blob, os.path.basename(file_path), prompt)  # openai_extract_text
    # result = process_csv(result)
    # print(result)
    
    sorted_names, prompt_map = ai.load_prompts()

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