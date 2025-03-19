# frontend/tabs/ocr_tab.py
import gradio as gr
import os
import requests

from utils.config import config
import utils.md_utils as md_utils
from utils.call_ai import load_prompts

PROCESSED_DIR = "data/processed"


def create_ocr_tab():
    # Load prompts for the dropdown
    sorted_names, prompt_map = load_prompts()
    
    # Create the models list
    models_list = ['Default'] + config['API']['Models'].split('|')
    
    default_prompt_name = config['UI']['DefaultPrompt']
    default_prompt = prompt_map.get(default_prompt_name)
    
    # Handler for when a prompt is selected
    def on_prompt_selected(prompt_name):
        selected_prompt = prompt_map[prompt_name]
        return selected_prompt['Prompt'], selected_prompt['Model'], selected_prompt['FileExt']

    with gr.Group():
        gr.Markdown("## Text Extraction and Processing")
        
        with gr.Row():
            file_input = gr.File(label="Upload File")
            
        with gr.Row():
            prompt_dropdown = gr.Dropdown(
                choices=sorted_names,
                value=default_prompt_name if default_prompt_name in sorted_names else None,
                label="Select Prompt Template"
            )
            model_dropdown = gr.Dropdown(
                choices=models_list,
                value="Default",
                label="Select Model"
            )
        
        # Hidden fields to store selected prompt details
        model_value = gr.Textbox(visible=False, value=default_prompt["Model"])
        file_ext_value = gr.Textbox(visible=False, value=default_prompt["FileExt"])
        
        prompt_text = gr.Textbox(
            label="Prompt Text", 
            placeholder="Enter prompt text to guide the OCR extraction...",
            lines=5,
            value=default_prompt["Prompt"]
        )
        
        with gr.Row():
            process_btn = gr.Button("Process File", size="sm")
        
        # Instead of using scale, we'll use a more compatible approach
        with gr.Row():
            # Use columns to control the width
            with gr.Column(variant="compact"):
                output_file = gr.File(label="Download Output")
            with gr.Column(variant="compact"):
                status_text = gr.Textbox(label="Status")
        
        # Add a preview section with tabs for different view types
        gr.Markdown("### Output")
        with gr.Tabs():
            with gr.TabItem("Plain Text"):
                preview_text = gr.Textbox(
                    label="",
                    value="Processed content will appear here...",
                    lines=12
                )
            with gr.TabItem("Rendered View"):
                preview_html = gr.HTML(
                    label="",
                    value="<div style='height: 300px; overflow-y: auto; padding: 10px; border: 1px solid #ddd;'><p>Processed content will appear here...</p></div>"
                )
        
        # Connect the prompt dropdown to update the prompt text and hidden fields
        prompt_dropdown.change(
            fn=on_prompt_selected,
            inputs=[prompt_dropdown],
            outputs=[prompt_text, model_value, file_ext_value]
        )
        
        # Connect the process button to the processing function with all details
        process_btn.click(
            fn=process_file,
            inputs=[file_input, prompt_text, model_value, file_ext_value, model_dropdown],
            outputs=[output_file, status_text, preview_html, preview_text]
        )

def process_file(file, prompt_text, default_model, file_ext, selected_model):
    try:
        if file is None:
            return None, "Please upload a file to process.", "", ""
        
        # Get the original file name
        original_filename = os.path.basename(file.name)
        file_name, _ = os.path.splitext(original_filename)
        
        # Use the extension from the selected prompt
        output_filename = f"{file_name}.{file_ext}"
        
        # Create output directory if it doesn't exist
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        
        # Full path for the output file
        output_file_path = os.path.join(PROCESSED_DIR, output_filename)
        
        # Read the file content
        with open(file.name, "rb") as f:
            file_blob = f.read()
        
        # Determine which model to use
        model = default_model if selected_model == "Default" else selected_model
        
        # Call the API to extract text
        try:
            # Send request to API endpoint
            response = requests.post(
                f'http://localhost:{config["API"]["Port"]}/ocr',
                files={"file": (original_filename, file_blob)},
                data={
                    "prompt_text": prompt_text,
                    "file_ext": file_ext,
                    "model": model
                }
            )
            
            if response.status_code == 200:
                # Get the text content directly from the response
                text_content = response.content
                
                # Write the content to the file
                with open(output_file_path, 'wb') as f:
                    f.write(text_content)
                
                # Get the content as text for display
                try:
                    text_display = text_content.decode('utf-8')
                except UnicodeDecodeError:
                    text_display = "Binary content cannot be displayed as text."
                
                # Generate HTML preview based on file extension
                html_preview = "<div style='height: 300px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; font-size: 14px;'>"
                
                if file_ext.lower() in ['md', 'markdown']:
                    # Add custom CSS for better table styling
                    html_preview += md_utils.get_table_css()

                    # Convert markdown to HTML with enhanced extensions
                    try:
                        # Try to get the required extensions
                        extensions = ['tables']
                        
                        # Add additional extensions if available
                        try:
                            import markdown.extensions.fenced_code
                            extensions.append('fenced_code')
                        except ImportError:
                            pass
                            
                        # Convert markdown to HTML
                        html_content = markdown.markdown(text_display, extensions=extensions)
                        
                        # If there are no tables rendered but there should be, try fixing the markdown
                        if '<table>' not in html_content and '|' in text_display and '---' in text_display:
                            fixed_text = md_utils.fix_markdown_tables(text_display)
                            html_content = markdown.markdown(fixed_text, extensions=extensions)
                            
                        html_preview += html_content
                    except Exception as e:
                        # Fallback attempt with table fixing if regular rendering fails
                        try:
                            fixed_text = md_utils.fix_markdown_tables(text_display)
                            html_content = markdown.markdown(fixed_text, extensions=['tables'])
                            html_preview += html_content
                        except:
                            # If all else fails, show the raw text
                            html_preview += f"<p>Error rendering markdown: {str(e)}</p><pre>{text_display}</pre>"
                
                elif file_ext.lower() in ['html', 'htm']:
                    # Directly use HTML (with basic sanitization)
                    html_preview += text_display
                
                elif file_ext.lower() in ['txt', 'csv', 'json', 'xml']:
                    # Preformatted text for code-like content
                    html_preview += f"<pre style='white-space: pre-wrap;'>{text_display}</pre>"
                
                else:
                    # Default to preformatted text for unknown types
                    html_preview += f"<pre style='white-space: pre-wrap;'>{text_display}</pre>"
                
                html_preview += "</div>"
                
                # Return the path to the file, success message, and preview content
                return output_file_path, f"Text successfully extracted and processed.", html_preview, text_display
            else:
                # Handle error response
                error_msg = "Unknown error"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown error')
                except:
                    error_msg = f"Error code: {response.status_code}"
                
                error_html = f"Error from API: {error_msg}"
                return None, error_html, error_html, f"Error from API: {error_msg}"
                
        except requests.exceptions.RequestException as e:
            error_html = f"Failed to connect to API: {str(e)}"
            return None, error_html, error_html, f"Failed to connect to API: {str(e)}"
    
    except Exception as e:
        error_html = f"Error processing file: {str(e)}"
        return None, error_html, error_html, f"Error processing file: {str(e)}"