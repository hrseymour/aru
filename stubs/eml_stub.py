import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.eml_extractor import extract_email_chain

# Example usage:
if __name__ == "__main__":
    # From a file (for testing)
    with open("data/Enhancements.eml", "rb") as f:
        eml_content = f.read()
    
    # Extract the text
    text_content = extract_email_chain(eml_content)
    print(text_content)
