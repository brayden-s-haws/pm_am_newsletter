import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def group_by_number(urls, titles, descs):
    """ Product Hunt stores the data for specific products in a somewhat odd manner. So you have to grab all the elements separately and then match them up afterward
    :param str urls:
    :param str titles:
    :param str descs:
    :return: dict
    """
    numbers = ['one', 'two', 'three', 'four', 'five']
    grouped_data = {}

    for i, number in enumerate(numbers):
        grouped_data[number] = {
            'link': urls[i],
            'title': titles[i],
            'desc': descs[i]
        }

    return grouped_data


def ph_scrape_urls(url):
    """ This gets the URLs for the top 5 products on the Product Hunt home page
    :param str url: Url to the home page of product hunt
    :return: list
    """
    # TODO: refactor this to not require the passing in of the URL
    # Send a GET request to the webpage
    response = requests.get(url)

    # If the GET request is successful, the status code will be 200
    if response.status_code == 200:
        # Get the content of the response
        content = response.content

        # Create a BeautifulSoup object and specify the parser
        soup = BeautifulSoup(content, 'html.parser')

        # Find all 'a' tags in the soup object
        a_tags = soup.find_all('a', class_=lambda x: x and x.startswith('styles'), href = lambda x: x and x.startswith('/posts'))

        # Extract the URLs from the 'href' attribute of the 'a' tags
        urls = []
        for a in a_tags:
            href = a.get('href')
            if href not in urls:
                urls.append(href)
            if len(urls) == 5:
                break

        return urls


def ph_scrape_text(url):
    """ This gets the name and description for the top 5 products on the Product Hunt home page
    :param str url: Url to the home page of product hunt
    :return: list
    """
    # TODO: refactor this to not require the passing in of the URL
    # Send a GET request to the webpage
    response = requests.get(url)

    # If the GET request is successful, the status code will be 200
    if response.status_code == 200:
        # Get the content of the response
        content = response.content

        # Create a BeautifulSoup object and specify the parser
        soup = BeautifulSoup(content, 'html.parser')

        # Find all 'a' tags in the soup object
        a_tags = soup.find_all('a', class_=lambda x: x and x.startswith('styles'), href=lambda x: x and x.startswith('/posts'))

        #  Extract the associated text from the 'a' tags. This is where it gets funky. Both the product name text and the description for product get stored in the same DIV but different a tag. So
        #  you grab them both here and then match them up later using group_by_number
        text = []
        for a in a_tags:
            href = a.get('href')
            if href not in text:
                text.append((a.text))
            if len(text) == 10:  # Due to how PH stores this data this needs to be twice as much as the value in ph_scrape_urls
                break

        return text


def get_ph_grouped_products():
    """ This gets the desired elements from Product Hunt and then matches the URLs, Names, and Descriptions up
    :return: dict
    """
    base_url = 'https://www.producthunt.com'

    scraped_urls = ph_scrape_urls(base_url)
    scraped_texts = ph_scrape_text(base_url)

    # Only the path is stored in the a_tag so you need to join it with the base url
    ph_urls_final = [urljoin(base_url, url) for url in scraped_urls]

    # Splitting titles and descriptions from scraped_texts
    titles = scraped_texts[::2]
    descs = scraped_texts[1::2]

    return group_by_number(ph_urls_final, titles, descs)


if __name__ == "__main__":
    ph_grouped_products = get_ph_grouped_products()


