# frontend/tabs/add_tab.py
import gradio as gr
import requests

from utils.config import config

def add_numbers(a, b):
    try:
        # Make sure a and b are properly converted to numbers
        a_val = float(a) if a is not None else 0
        b_val = float(b) if b is not None else 0
        
        # Use a full URL here to avoid relative path issues
        response = requests.post(
            f'http://localhost:{config["API"]["Port"]}/add',
            json={"a": a_val, "b": b_val}
        )
        
        if response.status_code == 200:
            result = response.json()["result"]
            return f"{result}"
        else:
            return f"Error from API: {response.json().get('error', 'Unknown error')}"
    except ValueError:
        return "Please enter valid numbers"
    except requests.exceptions.RequestException as e:
        return f"Failed to connect to API: {str(e)}"

def create_add_tab():
    with gr.Group():
        gr.Markdown("## Number Addition")
        gr.Markdown("Enter two numbers to add them using the API")
        
        with gr.Row():
            num_a = gr.Number(label="Number A", value=0)
            num_b = gr.Number(label="Number B", value=0)
        
        submit_btn = gr.Button("Add Numbers")
        result = gr.Textbox(label="Result")
        
        submit_btn.click(
            fn=add_numbers,
            inputs=[num_a, num_b],
            outputs=result
        )