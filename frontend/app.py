# frontend/app.py
from fastapi import FastAPI
from gradio import Interface
import gradio as gr
import requests

# Create FastAPI app
app = FastAPI()

def add_numbers(a, b):
    try:
        # Make sure a and b are properly converted to numbers
        a_val = float(a) if a is not None else 0
        b_val = float(b) if b is not None else 0
        
        # Use a full URL here to avoid relative path issues
        response = requests.post(
            "http://localhost:8000/add",
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

# Create the Gradio interface
demo = Interface(
    fn=add_numbers,
    inputs=[
        gr.Number(label="Number A", value=0),
        gr.Number(label="Number B", value=0)
    ],
    outputs=gr.Textbox(label="Result"),
    title="Number Addition App",
    description="Enter two numbers to add them using the API",
    # Disable the flag button
    allow_flagging="never"
)

# Mount the Gradio app at the root path
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)