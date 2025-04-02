import email
from email import policy
from email.parser import BytesParser, Parser
import html2text
import io
from bs4 import BeautifulSoup
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
# import pytz
from dateutil import parser as date_parser

def clean_text(text):
    """
    Clean up text by removing links, extra whitespace, etc.
    
    Args:
        text (str): The text to clean
        
    Returns:
        str: The cleaned text
    """
    # 1. Remove <https://...> links
    text = re.sub(r'<https?://[^>]+>', '', text)
    
    # 2. Clean up square brackets with links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # 3. Remove any remaining URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # 4. Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    # 5. Remove empty lines consisting only of whitespace
    text = re.sub(r'^\s*$\n', '', text, flags=re.MULTILINE)
    
    return text

def format_date(date_str):
    """
    Format date string to a more human-readable format
    
    Args:
        date_str (str): The date string from the email
        
    Returns:
        str: Formatted date string
    """
    try:
        # Parse the date using email.utils for handling email date formats
        dt = parsedate_to_datetime(date_str)
        
        # Format it in the desired way
        formatted_date = dt.strftime('%A, %B %d, %Y %I:%M %p')
        
        return formatted_date
    except Exception:
        # If parsing fails, try dateutil's parser which is more flexible
        try:
            dt = date_parser.parse(date_str)
            formatted_date = dt.strftime('%A, %B %d, %Y %I:%M %p')
            return formatted_date
        except Exception:
            # If all parsing attempts fail, return the original string
            return date_str

def extract_email_headers(msg):
    """
    Extract and format email headers
    
    Args:
        msg (email.message.EmailMessage): The parsed email message
        
    Returns:
        list: List of formatted header strings
    """
    headers = []
    headers.append(f"From:\t{msg.get('From', '')}")
    
    # Format the date nicely
    date_str = msg.get('Date', '')
    formatted_date = format_date(date_str) if date_str else ''
    headers.append(f"Sent:\t{formatted_date}")
    
    headers.append(f"To:\t{msg.get('To', '')}")
    if msg.get('Cc'):
        headers.append(f"Cc:\t{msg.get('Cc', '')}")
    headers.append(f"Subject:\t{msg.get('Subject', '')}")
    return headers

def extract_email_body(msg):
    """
    Extract the body content from an email message
    
    Args:
        msg (email.message.EmailMessage): The parsed email message
        
    Returns:
        list: List of text content from each part of the message
    """
    extracted_text = []
    
    def extract_part(part):
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition", ""))
        
        # Skip attachments
        if "attachment" in content_disposition:
            return
            
        if part.is_multipart():
            for subpart in part.iter_parts():
                extract_part(subpart)
        elif content_type == 'text/plain':
            extracted_text.append(part.get_content())
        elif content_type == 'text/html':
            html_content = part.get_content()
            
            # Use html2text for HTML parsing
            h = html2text.HTML2Text()
            h.ignore_links = False  # Still process links but we'll clean them later
            h.ignore_images = True
            h.ignore_tables = False
            h.unicode_snob = True
            text_content = h.handle(html_content)
            
            extracted_text.append(text_content)
    
    # Extract content from all parts of the email
    extract_part(msg)
    return extracted_text

def extract_email_chain(eml_blob):
    """
    Extract text content from an email blob (string or bytes) and clean up links.
    
    Args:
        eml_blob (str or bytes): The email content as a string or bytes
        
    Returns:
        str: The extracted readable text content with cleaned up links
    """
    # Convert string to bytes if needed
    if isinstance(eml_blob, str):
        eml_blob = eml_blob.encode('utf-8')
    
    # Parse the email
    msg = BytesParser(policy=policy.default).parse(io.BytesIO(eml_blob))
    
    # Extract headers
    headers = extract_email_headers(msg)
    
    # Extract body content
    body_content = extract_email_body(msg)
    
    # Combine all extracted content
    all_content = "\n".join(headers) + "\n\n" + "\n\n".join(body_content)
    
    # Clean up the text
    cleaned_content = clean_text(all_content)
    
    return cleaned_content