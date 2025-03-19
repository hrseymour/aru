import base64
import io
import mimetypes
import PyPDF2
import re

from utils.config import config

MIN_PDF_TEXT_LEN = 100
UNKNOWN_TEXT_LEN = 10000
OCR_TAG = "OCR!"


def read_file(file_path):
    with open(file_path, "rb") as file:
        return file.read()


def get_file_type(file_name):
    mime_type, _ = mimetypes.guess_type(file_name)
    
    # Handle case when mime_type is None
    if mime_type is None:
        # Try to guess from extension
        extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
        if extension in ['txt', 'csv', 'json', 'md']:
            return "text"
        elif extension in ['pdf']:
            return "pdf"
        elif extension in ['xls', 'xlsx']:
            return "excel"
        elif extension in ['png', 'jpeg', 'jpg', 'webp', 'gif']:
            return "image"
        else:
            return "unknown"
    
    # Handle when mime_type is available
    if "text" in mime_type:
        return "text"
    elif "pdf" in mime_type:
        return "pdf"
    elif "excel" in mime_type or "spreadsheetml" in mime_type:
        return "excel"
    elif any(img_type in mime_type for img_type in ["png", "jpeg", "jpg", "webp", "gif"]):
        return "image"
    else:
        return "unknown"   


def post_process_csv(input_text):
    # Step 1: Extract content between triple backticks if present
    code_block_pattern = r"```(?:csv)?\s*([\s\S]*?)\s*```"
    code_match = re.search(code_block_pattern, input_text)
    
    if code_match:
        csv_content = code_match.group(1)
    else:
        csv_content = input_text
    
    # Step 2: remove commas + replace bars with commas
    if "^^" in csv_content:
        return csv_content.replace(',', '').replace('^^', ',')
    
    return csv_content

  
def handle_pdf_xls(file_blob, file_type):
    # if type "unknown", and small in size, try treating it as "text"
    if file_type == "text" or (file_type == "unknown" and len(file_blob) < UNKNOWN_TEXT_LEN):
        return file_blob  # text
    
    # Handle PDF files using PyPDF2
    if file_type == "pdf":
        reader = PyPDF2.PdfReader(io.BytesIO(file_blob))
        
        # Extract text with page numbers
        text_parts = []
        text_len = 0
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            text_len += len(page_text)
            text_parts.append(f"--- Page {i+1} ---\n{page_text}")
            
        if text_len < MIN_PDF_TEXT_LEN:
            return OCR_TAG
        
        text = "\n\n".join(text_parts)
        return text

    # Handle Excel files (.xlsx and .xls)
    elif file_type == "excel":
        import pandas as pd
        
        # Read Excel file with all sheets
        excel_file = io.BytesIO(file_blob)
        # Get all sheet names
        xls = pd.ExcelFile(excel_file)
        sheet_names = xls.sheet_names
        
        # Process each sheet
        all_sheets_content = []
        for sheet_name in sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            sheet_content = f"--- Sheet: {sheet_name} ---\n{df.to_string()}"
            all_sheets_content.append(sheet_content)
        
        # Combine all sheets' content
        text = "\n\n".join(all_sheets_content)
        return text
    
    return ""


def load_prompts():
    prompts = []
    prompt_map = {}  # Map of name to full prompt spec
    prompt_pattern = re.compile(r'^prompt:(.+)$')
    
    for section in config.config.sections():
        match = prompt_pattern.match(section)
        if match:
            prompt_id = match.group(1)
            prompt = {
                'id': prompt_id,
                'Name': config[section]['Name'],
                'FileExt': config[section]['FileExt'],
                'Model': config[section]['Model'],
                'Prompt': config[section]['Prompt']
            }
            prompts.append(prompt)
            # Add to our map using Name as the key
            prompt_map[prompt['Name']] = prompt
    
    # Sort prompts by name for the dropdown list
    sorted_names = sorted([p['Name'] for p in prompts])
    
    return sorted_names, prompt_map


def mistral_extract_text(file_blob, file_name, prompt_text):
    from mistralai import Mistral

    api_key = config['Mistral']['API_KEY']
    model = config['Mistral']['Model']
    
    # Initialize the Mistral client
    client = Mistral(api_key=api_key)
    
    if get_file_type(file_name) in ['text', 'unknown']:
        file_blob = file_blob.decode('utf-8')
    
    # Upload the document and get a signed URL
    uploaded_file = client.files.upload(
        file={
            "file_name": file_name,
            "content": file_blob,
        },
        purpose="batch"
    )
    
    signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
    
    # Define the chat message including the prompt and document
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {"type": "document_url", "document_url": signed_url.url}
            ]
        }
    ]
    
    # Get the chat response
    chat_response = client.chat.complete(
        model=model,
        messages=messages
    )
    
    # Return the content of the response
    return post_process_csv(chat_response.choices[0].message.content)


def mistral_extract_text_ocr(file_blob, file_name):
    from mistralai import Mistral

    api_key = config['Mistral']['API_KEY']
    client = Mistral(api_key=api_key)
    
    # Upload document and get signed URL
    uploaded_file = client.files.upload(
        file={"file_name": file_name, "content": file_blob},
        purpose="ocr"
    )
    signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
   
    # Process document with explicit type definitions
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url.url  # Pass URL directly as string
        }
    )
    
    return "\n\n".join(page.markdown for page in ocr_response.pages)


def openai_extract_text(file_blob, file_name, prompt_text):
    from openai import OpenAI

    api_key = config['OpenAI']['API_KEY']
    model = config['OpenAI']['Model']
    client = OpenAI(api_key=api_key)

    # Determine file type
    file_type = get_file_type(file_name)
 
    if file_type == "image":
        base64_blob = base64.b64encode(file_blob).decode('utf-8')
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{file_type};base64,{base64_blob}"
                    }
                }
            ]
        }]
    else:
        text = handle_pdf_xls(file_blob, file_type)

        if text == OCR_TAG:
            text = mistral_extract_text_ocr(file_blob, file_name)
        elif len(text) == 0:
            return "Text NOT FOUND in pdf/xlsx"
        
        messages = [{
            "role": "user",
            "content": f"{prompt_text}\n\nDocument content:\n{text}"
        }]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1
    )    

    return post_process_csv(response.choices[0].message.content)


def gemini_extract_text(file_blob, file_name, prompt_text):
    import google.generativeai as genai

    api_key = config['Gemini']['API_KEY']
    model = config['Gemini']['Model']
    genai.configure(api_key=api_key)
     
    model_instance = genai.GenerativeModel(model_name=model)
    
    file_type = get_file_type(file_name)
    if file_type == "image":
        # For image files, send the image directly to Gemini
        contents = [
            prompt_text,
            {"mime_type": f"image/{file_type.split('.')[-1]}", "data": file_blob}
        ]
        
        response = model_instance.generate_content(contents)
        return post_process_csv(response.text)
    
    elif file_type == "pdf":
        # Gemini can handle PDFs directly
        contents = [
            prompt_text,
            {"mime_type": "application/pdf", "data": file_blob}
        ]
        
        response = model_instance.generate_content(contents)
        return post_process_csv(response.text)
    
    else:
        # For other file types, use the same approach as in openai_extract_text
        text = handle_pdf_xls(file_blob, file_type)
        
        if text == OCR_TAG:
            text = mistral_extract_text_ocr(file_blob, file_name)
        elif len(text) == 0:
            return "Text NOT FOUND in pdf/xlsx"
        
        contents = [f"{prompt_text}\n\nDocument content:\n{text}"]
        
        response = model_instance.generate_content(contents)
        return post_process_csv(response.text)
