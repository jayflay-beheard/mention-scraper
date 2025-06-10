import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import snscrape.modules.twitter as sntwitter
from datetime import datetime

st.set_page_config(page_title="Mention Scraper", layout="wide")
st.title("🔍 Company Mention Scraper")
st.markdown("This tool pulls raw mentions of a company from Twitter, Reddit, and G2. Paste a company name or G2 URL below.")

company_name = st.text_input("Enter Company Name (for Twitter & Reddit)")
g2_url = st.text_input("Enter G2 Reviews URL (optional)")

@st.cache_data(show_spinner=False)
def scrape_twitter(company_name, max_tweets=25):
    results = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'"{company_name}" lang:en').get_items()):
        if i >= max_tweets:
            break
        results.append({
            "source": "Twitter",
            "content": tweet.content,
            "timestamp": tweet.date.strftime("%Y-%m-%d %H:%M:%S"),
            "url": tweet.url
        })
    return results

@st.cache_data(show_spinner=False)
def scrape_reddit(company_name, max_posts=10):
    headers = {'User-Agent': 'Mozilla/5.0'}
    query = company_name.replace(" ", "%20")
    url = f"https://www.reddit.com/search/?q={query}"
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = []

    for post in soup.find_all("div", {"data-testid": "post-container"}):
        text = post.get_text(separator=" ", strip=True)
        if text:
            results.append({
                "source": "Reddit",
                "content": text,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "url": url
            })
        if len(results) >= max_posts:
            break
    return results

@st.cache_data(show_spinner=False)
def scrape_g2_reviews(g2_url, max_reviews=10):
    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get(g2_url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    reviews = []

    for div in soup.find_all("div", class_="paper-paper__1PY90")[:max_reviews]:
        text = div.get_text(separator=" ", strip=True)
        if text:
            reviews.append({
                "source": "G2",
                "content": text,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "url": g2_url
            })
    return reviews

if st.button("Scrape Mentions"):
    data = []
    if company_name:
        data.extend(scrape_twitter(company_name))
        data.extend(scrape_reddit(company_name))
    if g2_url:
        data.extend(scrape_g2_reviews(g2_url))

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data found or input missing.")
