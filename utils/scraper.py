import os
import requests
from datetime import datetime, timedelta

from utils.config import config


def is_file_newish(file_path, days=7, minutes=0):
    # Check if file exists
    if not os.path.isfile(file_path):
        return False
    
    # Get the last modification time of the file
    mod_time = os.path.getmtime(file_path)
    
    # Convert to datetime object
    mod_datetime = datetime.fromtimestamp(mod_time)
    
    # Calculate the cutoff date using both days and minutes
    cutoff_date = datetime.now() - timedelta(days=days, minutes=minutes)
    
    # Return True if file was modified after the cutoff date
    return mod_datetime > cutoff_date
        

def site_scraper(url):
    # URL to scrape (URL encoded if it contains special characters)
    url = url.lower()
    if url[:4] != "http":
        target_url = f'https://{url}'
    else:
        target_url = url
        url = url.split('//')[1]
        
    dir = config['UI']['CrawlerDir']
    file_path = os.path.join(dir, url + '.txt')

    if is_file_newish(file_path):
        with open(file_path, 'r') as f:
           return f.read()       
        
    # Construct the API request URL
    api_key = config["ScrapingFish"]["API_KEY"]
    api_url = config["ScrapingFish"]["API_URL"].format(api_key=api_key, target_url=target_url)

    # Make the request
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Get the HTML content
        html_content = response.text
        
        # Process the HTML content as needed
        # For example, you could use BeautifulSoup to extract text
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract all text from the page
        text = soup.get_text(separator=' ', strip=True)
        
        os.makedirs(dir, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(text)        
        
        return text
    else:
        print(f"Error: {response.status_code}")
        return None
