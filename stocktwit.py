import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from pprint import pprint
import re
import json
import os

from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline

nltk.download('vader_lexicon')

def scroll_to_end(driver):
    # Scroll to the end of the page
    last_height = driver.execute_script("return document.body.scrollHeight")
    count = 0
    while count < 50:
        # Scroll to the bottom using JavaScript
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for some time to load content (you can adjust the sleep duration as needed)
        time.sleep(1)

        # Check if reaching the end of the page
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        count += 1

def get_articles_from_url(url):
    # Configure Selenium options
    options = Options()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    # options.add_argument("--headless")  # Run Chrome in headless mode, without opening a browser window

    # Start the Selenium webdriver
    driver = webdriver.Chrome(options=options)

    # Load the URL
    driver.get(url)

    # Scroll until the end of the page
    scroll_to_end(driver)

    # Get the page source after it has been fully loaded
    html_source = driver.page_source

    # Close the Selenium webdriver
    driver.quit()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_source, 'html.parser')

    # Find all articles on the page
    articles = soup.find_all('article')

    # Return the list of articles
    return articles

def analyze_sentiment(text):
    sentiment_scores = {}
    print(text)
    # TextBlob sentiment analysis
    blob = TextBlob(text)
    sentiment_scores['TextBlob'] = blob.sentiment.polarity

    # NLTK sentiment analysis
    sid = SentimentIntensityAnalyzer()
    nltk_scores = sid.polarity_scores(text)
    sentiment_scores['NLTK'] = nltk_scores['compound']

    # Hugging Face Transformers sentiment analysis
    classifier = pipeline('sentiment-analysis', model="distilbert-base-uncased-finetuned-sst-2-english")
    hf_scores = classifier(text, truncation=True)[0]
    sentiment_scores['HuggingFace'] = hf_scores

    return sentiment_scores

def extract_article_info(article_html):
    sid = SentimentIntensityAnalyzer()
    soup = BeautifulSoup(article_html, 'html.parser')

    # Extract username
    username_elem = soup.find('span', class_='StreamMessage_username-default__gka83')
    username = username_elem.text.strip() if username_elem else ''

    # Extract timestamp
    timestamp_elem = soup.find('time', class_='StreamMessage_timestamp__CP2QT')
    timestamp = timestamp_elem['datetime'] if timestamp_elem else ''

    # Extract message content
    content_elem = soup.find('div', class_='RichTextMessage_body__Fa2W1')
    content = content_elem.text.strip() if content_elem else ''

    # Extract image URL
    image_elem = soup.find('img', class_='StreamMessage_avatarImage__AStmd')
    image_url = image_elem['src'] if image_elem else ''

    # Find stock ticker symbols using regex
    tickers = re.findall(r'\$[A-Za-z.]+', content)

    if tickers:
        # Perform sentiment analysis on the content
        sentiment_scores = analyze_sentiment(content)
    else:
        return None

    return {
        'username': username,
        'timestamp': timestamp,
        'content': content,
        'sentiment': sentiment_scores,
        'image_url': image_url
    }

# Example usage
def get_stock_info(user):
    url = f'https://stocktwits.com/{user}'
    all_articles = get_articles_from_url(url)
    article_list = []  # Create an empty list

    for article in all_articles:
        article_html = str(article)  # Convert the article to a string
        article_info = extract_article_info(article_html)
        if article_info is not None:
            article_list.append(article_info)  # Append article_info to the list

    # Create the directory if it doesn't exist
    os.makedirs('./user_articles', exist_ok=True)

    # Dump the article_list into a JSON file
    json_file = os.path.join('./user_articles', f'{user}_articles.json')
    with open(json_file, 'w') as f:
        json.dump(article_list, f, indent=4)

    pprint(article_list)

def get_users_from_url(url):
    options = Options()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    scroll_to_end(driver)

    html_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html_source, 'html.parser')
    user_elements = soup.find_all(class_='UserPageFollows_userInfo__u_zRE')

    users = []
    for user_element in user_elements:
        username_element = user_element.select_one('[class*="UserPageFollows_username__"]')
        if username_element:
            username = username_element.text.strip()
            users.append(username)

    return users

url = 'https://stocktwits.com/ttspps/following'
url_list = []
url_list_dup = []
url_list.append(url)
url_list_dup.append(url)
while url_list:
    link = url_list.pop()
    all_users = get_users_from_url(link)
    pprint(all_users)
    for user in all_users:
        if not os.path.exists(os.path.join('./user_articles', f'{user}_articles.json')):
            link = f'https://stocktwits.com/{user}/following'
            if link not in url_list_dup:
                url_list.append(link)
                url_list_dup.append(url)
            article_list = get_stock_info(user)


    pprint(url_list)