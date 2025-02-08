import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures
import time
from threading import Lock
import os

BASE_URL = "https://www.smashingmagazine.com"
ARTICLES_URL = BASE_URL + "/articles/"
OUTPUT_FILE = "smashingMagazineArticles.json"
file_lock = Lock()  

def get_article_links_from_page(page_num):
    """
    Extracts article links from a single page of Smashing Magazine articles.
    Returns tuple of (page_num, links)
    """
    current_url = f"{ARTICLES_URL}page/{page_num}/" if page_num > 1 else ARTICLES_URL
    try:
        time.sleep(0.5) 
        response = requests.get(current_url)
        if response.status_code == 404:
            return (page_num, None)  
            
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.select('article.article--post h2.article--post__title a')
        links = [BASE_URL + article['href'] for article in articles]
        print(f"Page {page_num}: Found {len(links)} articles")
        return (page_num, links)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL for page {page_num}: {e}")
        return (page_num, [])

def get_all_article_links_parallel(max_pages=100):
    """
    Scrapes article links from all pages in parallel.
    """
    all_links = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_page = {executor.submit(get_article_links_from_page, page_num): page_num 
                         for page_num in range(1, max_pages + 1)}
        
        for future in concurrent.futures.as_completed(future_to_page):
            page_num, links = future.result()
            if links is None:  
                break
            if links:
                all_links.extend(links)
                
    return list(set(all_links))  

def scrape_article_data(article_url):
    """
    Scrapes detailed data from a single article page.
    """
    article_data = {
        "url": article_url,
        "title": None,
        "author": None,
        "date": None,
        "categories": [],
        "summary": None,
        "content": None
    }
    
    try:
        time.sleep(0.5)  # Polite delay
        response = requests.get(article_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        title_element = soup.select_one('h1.article-header--title')
        article_data["title"] = title_element.text.strip() if title_element else None

        author_element = soup.select_one('a.author-post__author-title')
        article_data["author"] = author_element.text.strip() if author_element else None

        date_element = soup.select_one('time.article-header--date')
        article_data["date"] = date_element.text.strip() if date_element else None

        category_elements = soup.select('.meta-box--tags a')
        article_data["categories"] = [cat.text.strip() for cat in category_elements]

        return article_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching article {article_url}: {e}")
        return article_data

def update_json_file(article_data):
    """
    Updates the JSON file with new article data in a thread-safe way.
    """
    with file_lock:
        try:
            # Read existing data
            if os.path.exists(OUTPUT_FILE):
                with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        existing_data = []
            else:
                existing_data = []

            existing_data.append(article_data)
            
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error updating JSON file: {e}")

def process_article(article_url):
    """
    Process a single article and update the JSON file.
    """
    article_data = scrape_article_data(article_url)
    update_json_file(article_data)
    return article_data

def scrape_articles_parallel(article_links):
    """
    Scrapes article data in parallel and continuously updates the JSON file.
    """
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

    articles_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_article, link) for link in article_links]
        total = len(futures)
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            article_data = future.result()
            articles_data.append(article_data)
            print(f"Processed {i}/{total} articles")
    
    return articles_data

def main():
    """
    Main function to run the parallel scraper.
    """
    print("Starting to scrape article links in parallel...")
    article_links = get_all_article_links_parallel()
    print(f"Found {len(article_links)} unique article links.")

    print("Starting to scrape article data in parallel with continuous updates...")
    articles_data = scrape_articles_parallel(article_links)
    print("Article data scraping complete.")
    print(f"Final data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()