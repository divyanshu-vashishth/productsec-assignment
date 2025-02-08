import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures

BASE_URL = "https://www.smashingmagazine.com"
ARTICLES_URL = BASE_URL + "/articles/"
OUTPUT_FILE = "smashingMagazineArticles.json"

def get_article_links_from_page(url):
    """
    Extracts article links from a single page of Smashing Magazine articles.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  #
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.select('article.article--post h2.article--post__title a')
        links = [BASE_URL + article['href'] for article in articles]
        return links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return []

def get_all_article_links():
    """
    Scrapes all article links from paginated article pages.
    """
    all_links = []
    current_url = ARTICLES_URL
    page_num = 1
    while current_url:
        print(f"Fetching links from page {page_num}: {current_url}")
        links = get_article_links_from_page(current_url)
        if not links:
            break  
        all_links.extend(links)

        try:
            response = requests.get(current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            next_page_link = soup.select_one('a.next')
            if next_page_link:
                current_url = BASE_URL + next_page_link['href']
                page_num += 1
            else:
                current_url = None 
        except requests.exceptions.RequestException as e:
            print(f"Error fetching next page link from {current_url}: {e}")
            break 
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

        summary_element = soup.find('span', class_='summary__heading', string=lambda text: text and "Quick summary" in text.lower())
        if summary_element:
            summary_text_element = summary_element.find_next_sibling('p')
            article_data["summary"] = summary_text_element.text.strip() if summary_text_element else None
        else:
             # Try to find summary in article teaser if "Quick Summary" is not present
             teaser_element = soup.select_one('.article--post__teaser')
             if teaser_element:
                 article_data["summary"] = teaser_element.text.split('—')[-1].strip() if teaser_element.text.split('—') else None


        content_element = soup.select_one('.article--single__content')
        article_data["content"] = ''.join(p.text.strip() for p in content_element.select('p')) if content_element else None

        return article_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching article {article_url}: {e}")
        return article_data 


def scrape_articles_parallel(article_links):
    """
    Scrapes article data in parallel using ThreadPoolExecutor.
    """
    articles_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor: 
        futures = [executor.submit(scrape_article_data, link) for link in article_links]
        for future in concurrent.futures.as_completed(futures):
            articles_data.append(future.result())
    return articles_data


def save_to_json(data, filename):
    """
    Saves scraped data to a JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    """
    Main function to run the scraper.
    """
    print("Starting to scrape article links...")
    article_links = get_all_article_links()
    print(f"Found {len(article_links)} article links.")

    print("Starting to scrape article data in parallel...")
    articles_data = scrape_articles_parallel(article_links)
    print("Article data scraping complete.")

    print(f"Saving data to {OUTPUT_FILE}...")
    save_to_json(articles_data, OUTPUT_FILE)
    print(f"Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()