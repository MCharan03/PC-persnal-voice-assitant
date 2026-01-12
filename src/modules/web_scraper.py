import requests
from bs4 import BeautifulSoup
from langchain.tools import tool

@tool
def scrape_website(url: str) -> str:
    """
    Useful for scraping the content of a specific website url. 
    Use this when the search tool provides a URL and you need to read the actual page content.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    

        text = soup.get_text()

        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text[:5000] # Return first 5000 chars to avoid context limit
    except Exception as e:
        return f"Error scraping website: {str(e)}"