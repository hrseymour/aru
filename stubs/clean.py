import re

def clean_llm_csv(input_text):
    """
    Clean up CSV output from an LLM:
    1. Extract content between triple backticks if present
    2. Remove commas not in the header
    
    Args:
        input_text (str): Raw LLM output containing CSV data
        
    Returns:
        str: Cleaned CSV text
    """
    # Step 1: Extract content between triple backticks if present
    code_block_pattern = r"```(?:csv)?\s*([\s\S]*?)\s*```"
    code_match = re.search(code_block_pattern, input_text)
    
    if code_match:
        csv_content = code_match.group(1)
    else:
        csv_content = input_text
    
    return csv_content.replace(',', '').replace('|', ',')

# Example usage
if __name__ == "__main__":
    # Example input with markdown code blocks and commas
    sample_input = """
Here's the CSV data you requested:

```csv
Name|Age|Location
John Doe|30,000|New York
Jane Smith|25|San Francisco
Alex Johnson|40|Chicago
```

Hope this helps!
"""
    
    cleaned_output = clean_llm_csv(sample_input)
    print(cleaned_output)