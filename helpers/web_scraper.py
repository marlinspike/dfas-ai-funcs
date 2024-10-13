import os
from typing import List, Dict, Any, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import argparse

class WebScraper:
    def __init__(self):
        load_dotenv()
        self.port = os.getenv('SELENIUM_SCRAPER_PORT', '4444')
        self.timeout = int(os.getenv('TIMEOUT', '20'))
        self.selenium_url = os.getenv('SELENIUM_SCRAPER_URL', f'http://localhost:{self.port}/wd/hub')#f'http://localhost:{self.port}/wd/hub'

    def _create_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Remote(
            command_executor=self.selenium_url,
            options=options
        )


    def scrape_url(self, url: str) -> str:
        """
        Scrapes the webpage for its text content in the body tag.
        """        
        driver = None
        try:
            driver = self._create_driver()
            driver.get(url)

            # Wait until the body tag is present, indicating the page has fully loaded
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Once loaded, extract the entire page text
            page_text = driver.find_element(By.TAG_NAME, "body").text
            return page_text

        except (TimeoutException, WebDriverException) as e:
            print(f"Error occurred while scraping {url}: {e}")
            return ""  # Return a blank string in case of an error

        finally:
            if driver:
                driver.quit()



    def scrape_url_and_extract_links(self, url: str) -> Tuple[str, List[str]]:
        """
        Scrapes the webpage for its text content and extracts all URLs from <a> tags.
        
        Returns a tuple where the first element is the text and the second is a list of URLs.
        """
        driver = None
        try:
            driver = self._create_driver()
            driver.get(url)

            # Wait until the body tag is present, indicating the page has fully loaded
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Extract the entire page text
            page_text = driver.find_element(By.TAG_NAME, "body").text

            # Extract all URLs from <a> tags
            anchor_elements = driver.find_elements(By.TAG_NAME, "a")
            urls = [anchor.get_attribute("href") for anchor in anchor_elements if anchor.get_attribute("href")]

            return page_text, urls

        except (TimeoutException, WebDriverException) as e:
            print(f"Error occurred while scraping {url}: {e}")
            return "", []

        finally:
            if driver:
                driver.quit()


    def bulk_scrape(self, urls: List[str]) -> List[Dict[str, Any]]:
        results = []
        for url in urls:
            content = self.scrape_url(url)
            results.append({
                "url": url,
                "content": content
            })
        return results

    def set_timeout(self, timeout: int) -> None:
        self.timeout = timeout

    def set_port(self, port: str) -> None:
        self.port = port
        self.selenium_url = f'http://localhost:{self.port}/wd/hub'


def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Web scraper with Selenium")
    
    # Add arguments for the URL and output type
    parser.add_argument("url", help="The URL to scrape")
    parser.add_argument(
        "--output", 
        choices=["text", "length", "urls", "text_and_urls"], 
        default="text", 
        help="Specify the type of output: text (default), length, urls, or text_and_urls"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Create the WebScraper instance
    scraper = WebScraper()

    # Handle the different output options
    if args.output == "length":
        # Scrape only the text and print the length
        content = scraper.scrape_url(args.url)
        print(f"Total length of characters: {len(content)}")
    elif args.output == "urls":
        # Scrape the page and print the number of URLs found
        _, urls = scraper.scrape_url_and_extract_links(args.url)
        print(f"Total number of URLs found: {len(urls)}")
        for url in urls:
            print(url)
    elif args.output == "text_and_urls":
        # Scrape the page and print both the text and the URLs found
        content, urls = scraper.scrape_url_and_extract_links(args.url)
        print(f"Scraped content:\n{content}")
        print(f"\nTotal number of URLs found: {len(urls)}")
        for url in urls:
            print(url)
    else:
        # Default behavior: scrape only the text
        content = scraper.scrape_url(args.url)
        print(f"Scraped content:\n{content}")

if __name__ == "__main__":
    main()
