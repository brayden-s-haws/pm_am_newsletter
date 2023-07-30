from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from newspaper import Article
from current_news_scrapers import get_all_urls
import requests

request_timeout = 5


def can_fetch(url):
    """ For each URL we check if it's robot.txt file allows for scraping
    :param str url:
    :return:
    """
    parsed_url = urlparse(url)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc  # Get the base of the url from the full URL
    robots_url = base_url + "/robots.txt"  # Join the base URL with the robots.txt path to get the full URL for robots.txt

    rp = RobotFileParser()
    try:
        response = requests.get(robots_url, timeout=request_timeout)
        response.raise_for_status()  # raise exception if invalid response
        rp.parse(response.text.splitlines())
    except requests.exceptions.RequestException as e:  # Catch requests exceptions including Timeout
        print(f"Could not fetch robots.txt from {url} due to {e}")
        return False

    return rp.can_fetch("*", url)

def scrape_articles():
    """ This takes the URLS that pass the can_fetch check and scrapes the URL, article title, and article text from the page using Newspaper3k
    :return: dict
    """
    urls = get_all_urls()

    scrape_list = {}

    for url in urls:
        try:
            if can_fetch(url):
                scrape_list[url] = True
        except requests.exceptions.Timeout:
            print(f"Timeout occurred while checking robots.txt for {url}")

    valid_list = [key for key, val in scrape_list.items() if val != False]

    print(f'valid_list:{valid_list}')

    scraped_articles = {}
    for item in valid_list:
        url = item
        article = Article(url)
        try:
            article.download()
            article.parse()
            article_title = article.title
            article_text = article.text
            scraped_articles[item] = {'url':url, 'title':article_title, 'text':article_text}
        except Exception as e:
            print(f"Failed to download or parse article from {url}. Error: {e}")
            continue

    # Filter out articles with no title or text
    scraped_articles = {k: v for k, v in scraped_articles.items() if v['title'] and v['text']}

    return scraped_articles


if __name__ == "__main__":
    articles = scrape_articles()