import time
import requests
from bs4 import BeautifulSoup
from datetime import date
from urllib.parse import urlparse

# Exclude domains that commonly cause errors, do not allow for scraping, or post content that is low-quality/not relevant. I was trying limit the amount of urls that would ultimately be rejected
# but the internet is too big and this is a losing battle. I just rely on the scrape_articles scrape check functionality to filter things now.
excluded_domains = ['twitter.com', 'mastodon.social', 'blueskyweb.xyz', 'reddit.com', 'forbes.com', 'searchenginejournal.com', 'mas.to', 'socialmediatoday.com',
                            'cryptonews.com',
                            'techcrunch.com', 'theinformation.com', 'businessinsider.com', 'indiatimes.com', 'threads.net', 'javascript:tgd','mastodon.online','siliconangle.com','pocket-lint.com',
                            'androidpolice', "cointelegraph.com",'coindesk.com','bsky.app', 'cryptobriefing.com','cryptopolitan.com','nngroup.com','thehill.com','bizjournals.com',
                    'techdirt.com', 'theblock.co','nbcbayarea.com','usatoday.com', 'coinpedia.org','unchainedcrypto.com','bitcoinist.com','wsj.com','pymnts.com','americanbanker.com',
                    'collabora.com', 'barrons.com', 'france24.com','washingtonpost.com','latimes.com','banger.show','awsdocsgpt','lightning.engineering','blockworks.co', 'sci-hub.se','ibtimes.com',
                    'cnn.com','neowin.net','archive.org','journa.host','phonearena.com','qz.com','lwn.net','appuals.com','inews.co','dealstreetasia.com','bankautomationnews.com','gizchina.com',
                    'ethereumworldnews.com', 'livemint.com', 'cryptopotato.com','decrypt.co','crypto.news','cryptoslate.com', 'bbcnews.com','ign.com','benshoof.org','github.io', 'slashdot.org',
                    'nypost.com', 'nytimes.com', 'newsbtc.com', 'substack.com', 'pingwest.com', 'youtube.com', 'github.com', 'play.google.com', 'cnbc.com', 'afb.org', 'techlusive.in']

source_url_limit = 30 # Hackernews paginates at 30 links so this simulates the first page from them. And should cover enough of the links on the front page of other sources.


def has_path_after_domain(url):
    """ Check if there is a path after the domain in the url, we only want urls that link to content rather than a top level domain. PHP also does odd things in the flow so we exclude those"""
    parsed_url = urlparse(url)
    return bool(parsed_url.path) and parsed_url.path != '/' and not parsed_url.path.endswith('.php') and '.php/' not in parsed_url.path

### GET URL FUNCTIONS ###


def get_hn_links():
    """ This uses the hackernews API to retrieve URLS posted in the last 24 hours
    :return: list
    """
    response = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json')
    story_ids = response.json()

    hn_urls = []

    one_day_ago = time.time() - 24 * 60 * 60

    for story_id in story_ids[:source_url_limit]:  # Only the top 30 to simulate the first page
        response = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json')
        story_data = response.json()

        # Not all items are stories (some might be job postings, for example), and not all stories have URLs.
        # Also check that the story was posted in the last 24 hours.
        if (story_data['type'] == 'story' and
                'url' in story_data and
                story_data['time'] >= one_day_ago):

            parsed_url = urlparse(story_data['url'])
            domain = parsed_url.netloc

            if domain not in excluded_domains and has_path_after_domain(story_data['url']):
                hn_urls.append(story_data['url'])

    return hn_urls


def get_register_urls():
    """ This gets all the links posted to The Register in the last 24 hours
    :return: list
    """

    def scrape_register(url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            content = response.content

            soup = BeautifulSoup(content, 'html.parser')

            a_tags = soup.find_all('a', class_='story_link')

            urls = []
            for a in a_tags:
                href = a.get('href')
                if not any(domain in href for domain in excluded_domains) and has_path_after_domain(href):
                    urls.append(href)
                if len(urls) >= source_url_limit:
                    break
            return urls

    scrape_register_urls = scrape_register('https://www.theregister.com')

    register_urls_final = []
    prefix = 'https://www.theregister.com'
    for url in scrape_register_urls:
        url = f'{prefix}{url}'
        register_urls_final.append(url)

    register_urls_final = list(set(register_urls_final))

    today = date.today()

    date_string = today.strftime("%Y/%m/%d")

    register_urls_final = [url for url in register_urls_final if date_string in url]

    return register_urls_final


def get_techmeme_urls():
    """ This gets all the links posted to Techmeme in the last 24 hours
    :return: list
    """

    def scrape_techmeme(url):
        today = date.today()
        date_string = today.strftime("%y%m%d")

        response = requests.get(url)

        if response.status_code == 200:
            content = response.content

            soup = BeautifulSoup(content, 'html.parser')

            divs = soup.find_all('div', class_='itc2', id=lambda id: id and id.startswith(date_string))

            urls = []
            for div in divs:
                for a in div.find_all('a'):
                    url = a.get('href')
                    if url and not any(domain in url for domain in excluded_domains) and has_path_after_domain(url):
                        urls.append(url)
                    if len(urls) >= source_url_limit:
                        break
                if len(urls) >= source_url_limit:
                    break

            return urls

    techmeme_urls_final = set(list(scrape_techmeme('https://techmeme.com')))

    return techmeme_urls_final


def get_all_urls():
    """ Gets all urls from various sources and combines them into a single list
    :return: list
    """
    # TODO: Combine all scrapers into a single class and make it easy to add more sources
    ### CALL URL FUNCTIONS ###
    hn_links = get_hn_links()
    register_links = get_register_urls()
    techmeme_links = get_techmeme_urls()

    ### COMBINE ALL URLS INTO SINGLE LIST ###
    all_urls = []
    all_urls.extend(hn_links)
    all_urls.extend(register_links)
    all_urls.extend(techmeme_links)
    all_urls = list(set(all_urls))
    # Ensure all URLs end with a trailing '/', this ensures consistency of format when we later need to match URLs for deduplication
    all_urls = [url if url.endswith('/') else url + '/' for url in all_urls]
    print(f'all_urls:{all_urls}')
    return all_urls

if __name__ == "__main__":
    get_all_urls()



