import requests
import urllib.parse

from utils.config import config

def site_scraper(url):
    # URL to scrape (URL encoded if it contains special characters)
    target_url = urllib.parse.quote_plus(url)

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
        return text
    else:
        print(f"Error: {response.status_code}")
        return None
