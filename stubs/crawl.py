import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import config
from utils.scraper import site_scraper
import utils.call_ai as ai

if __name__ == "__main__":
    URL = "https://ARUcaptiveinsurance.com"
    text = site_scraper(URL)

    prompt_text = config["prompt:summary"]["Prompt"]
    overview = ai.gemini_extract_text(text, "ARU_overview.txt", prompt_text)
   
    print(overview)
    