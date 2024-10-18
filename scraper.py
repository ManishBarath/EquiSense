import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin
import feedparser

def get_headers():
    """Rotate user agents to avoid blocking"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    return {"User-Agent": random.choice(user_agents)}

def safe_request(url, timeout=10):
    """Make a safe request with error handling"""
    try:
        response = requests.get(url, headers=get_headers(), timeout=timeout)
        response.raise_for_status()
        return response
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

def scrape_rss_feed(url, source_name):
    """Scrape headlines from RSS feeds"""
    try:
        feed = feedparser.parse(url)
        headlines = []
        
        for entry in feed.entries[:20]:  # Limit to 20 entries
            title = entry.title.strip()
            if title and len(title.split()) > 4 and len(title) < 200:
                headlines.append(title)
        
        print(f"✅ {source_name} RSS: {len(headlines)} headlines")
        return headlines
    except Exception as e:
        print(f"❌ Error scraping {source_name} RSS: {str(e)}")
        return []

def scrape_yahoo_rss():
    """Scrape Yahoo Finance RSS feed"""
    return scrape_rss_feed("https://finance.yahoo.com/rss/", "Yahoo Finance")

def scrape_marketwatch_rss():
    """Scrape MarketWatch RSS feed"""
    return scrape_rss_feed("https://feeds.marketwatch.com/marketwatch/realtimeheadlines/", "MarketWatch")

def scrape_reuters_rss():
    """Scrape Reuters RSS feed"""
    return scrape_rss_feed("https://feeds.reuters.com/reuters/businessNews", "Reuters Business")

def scrape_cnbc_rss():
    """Scrape CNBC RSS feed"""
    return scrape_rss_feed("https://feeds.cnbc.com/cnbc/world", "CNBC")

def scrape_benzinga():
    """Scrape Benzinga - more accessible"""
    url = "https://www.benzinga.com/news"
    response = safe_request(url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    selectors = [
        'h2 a',
        'h3 a',
        '.story-title a',
        '.headline a'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            title = element.get_text(strip=True)
            if title and len(title.split()) > 4 and len(title) < 200:
                headlines.append(title)
    
    return list(set(headlines))

def scrape_finviz():
    """Scrape FinViz news"""
    url = "https://finviz.com/news.ashx"
    response = safe_request(url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    # FinViz has a specific table structure
    news_table = soup.find('table', {'id': 'news'})
    if news_table:
        for row in news_table.find_all('tr'):
            link = row.find('a')
            if link:
                title = link.get_text(strip=True)
                if title and len(title.split()) > 4 and len(title) < 200:
                    headlines.append(title)
    
    return list(set(headlines))

def scrape_alpha_architect():
    """Scrape Alpha Architect - accessible financial blog"""
    url = "https://alphaarchitect.com/blog/"
    response = safe_request(url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    selectors = [
        'h2.entry-title a',
        'h3.entry-title a',
        '.post-title a'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            title = element.get_text(strip=True)
            if title and len(title.split()) > 4 and len(title) < 200:
                headlines.append(title)
    
    return list(set(headlines))

def scrape_zerohedge():
    """Scrape ZeroHedge - alternative financial news"""
    url = "https://www.zerohedge.com/"
    response = safe_request(url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    selectors = [
        'h2 a',
        '.teaser-title a',
        'h3 a'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            title = element.get_text(strip=True)
            if title and len(title.split()) > 4 and len(title) < 200:
                headlines.append(title)
    
    return list(set(headlines))

def scrape_reuters():
    """Scrape Reuters financial news with improved selectors"""
    url = "https://www.reuters.com/markets/"
    response = safe_request(url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    # Multiple selector strategies for Reuters
    selectors = [
        'h3[data-testid="Heading"]',
        'h3 a',
        'a[data-testid="Link"]',
        '.story-title',
        '[data-module="ArticleHeader"] h1',
        '[data-module="ArticleHeader"] h3'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            title = element.get_text(strip=True)
            if title and len(title.split()) > 4 and len(title) < 200:
                headlines.append(title)
    
    return list(set(headlines))  # Remove duplicates

def scrape_yahoo():
    """Scrape Yahoo Finance with improved selectors"""
    url = "https://finance.yahoo.com/"
    response = safe_request(url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    # Multiple selector strategies
    selectors = [
        'h3 a',
        'h2 a',
        '[data-module="Stream"] h3',
        '.js-content-viewer h3',
        '.Fw\\(b\\) a',
        '.rapidnofollow'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            title = element.get_text(strip=True)
            if title and len(title.split()) > 4 and len(title) < 200:
                headlines.append(title)
    
    return list(set(headlines))

def scrape_marketwatch():
    """Scrape MarketWatch with improved selectors"""
    url = "https://www.marketwatch.com/latest-news"
    response = safe_request(url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    selectors = [
        '.article__headline a',
        'h3.article__headline',
        '.headline a',
        'h2 a',
        'h3 a'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            title = element.get_text(strip=True)
            if title and len(title.split()) > 4 and len(title) < 200:
                headlines.append(title)
    
    return list(set(headlines))

def scrape_cnbc():
    """Scrape CNBC finance news"""
    url = "https://www.cnbc.com/finance/"
    response = safe_request(url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    selectors = [
        '.ArticleWrap-cVzZiI h2 a',
        '.InlineArticle-cVzZiI h3 a',
        '.Card-cVzZiI h3 a',
        'h2 a',
        'h3 a',
        '.RiverHeadline-cVzZiI a'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            title = element.get_text(strip=True)
            if title and len(title.split()) > 4 and len(title) < 200:
                headlines.append(title)
    
    return list(set(headlines))

def scrape_bloomberg():
    """Scrape Bloomberg news (basic selectors)"""
    url = "https://www.bloomberg.com/markets"
    response = safe_request(url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    selectors = [
        'h3 a',
        'h2 a',
        '.story-package-module__story__headline a',
        '[data-module="headline"] a'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            title = element.get_text(strip=True)
            if title and len(title.split()) > 4 and len(title) < 200:
                headlines.append(title)
    
    return list(set(headlines))

def scrape_investing_com():
    """Scrape Investing.com news"""
    url = "https://www.investing.com/news/latest-news"
    response = safe_request(url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    selectors = [
        '.largeTitle a',
        '.title a',
        'h3 a',
        '.textDiv a',
        '.articleItem .title a'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            title = element.get_text(strip=True)
            if title and len(title.split()) > 4 and len(title) < 200:
                headlines.append(title)
    
    return list(set(headlines))

def scrape_financial_times():
    """Scrape Financial Times (limited due to paywall)"""
    url = "https://www.ft.com/markets"
    response = safe_request(url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    selectors = [
        '.o-teaser__heading a',
        'h3 a',
        '.js-teaser-heading-link'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            title = element.get_text(strip=True)
            if title and len(title.split()) > 4 and len(title) < 200:
                headlines.append(title)
    
    return list(set(headlines))

def scrape_seeking_alpha():
    """Scrape Seeking Alpha news"""
    url = "https://seekingalpha.com/news"
    response = safe_request(url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = []

    selectors = [
        '[data-test-id="post-list-item-title"] a',
        '.mc a',
        'h3 a',
        '.article-title a'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            title = element.get_text(strip=True)
            if title and len(title.split()) > 4 and len(title) < 200:
                headlines.append(title)
    
    return list(set(headlines))


def scrape_all():
    """Scrape headlines from multiple financial news sources including RSS feeds"""
    headlines = []
    
    # Primary scrapers (web scraping)
    web_scrapers = [
        ("Seeking Alpha", scrape_seeking_alpha),
        ("Benzinga", scrape_benzinga),
        ("FinViz", scrape_finviz),
        ("Alpha Architect", scrape_alpha_architect),
        ("ZeroHedge", scrape_zerohedge)
    ]
    
    # RSS feed scrapers (more reliable)
    rss_scrapers = [
        ("Yahoo Finance RSS", scrape_yahoo_rss),
        ("MarketWatch RSS", scrape_marketwatch_rss),
        ("Reuters RSS", scrape_reuters_rss),
        ("CNBC RSS", scrape_cnbc_rss)
    ]
    
    # Scrape RSS feeds first (more reliable)
    print("=== Scraping RSS Feeds ===")
    for source_name, scraper_func in rss_scrapers:
        try:
            source_headlines = scraper_func()
            headlines.extend(source_headlines)
            time.sleep(random.uniform(0.5, 2))
        except Exception as e:
            print(f"❌ Error scraping {source_name}: {str(e)}")
            continue
    
    print("\n=== Scraping Websites ===")
    for source_name, scraper_func in web_scrapers:
        try:
            source_headlines = scraper_func()
            headlines.extend(source_headlines)
            print(f"✅ {source_name}: {len(source_headlines)} headlines")
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"❌ Error scraping {source_name}: {str(e)}")
            continue

    # Remove duplicates and filter quality
    unique_headlines = []
    seen = set()
    
    for headline in headlines:
        # Clean and normalize
        headline = headline.strip()
        headline_lower = headline.lower()
        
        # Skip if too short, too long, or duplicate
        if (len(headline.split()) < 4 or 
            len(headline) > 200 or 
            headline_lower in seen or
            not any(char.isalpha() for char in headline)):
            continue
            
        # Filter out non-financial content and improve quality
        financial_keywords = [
            'stock', 'market', 'trading', 'investment', 'finance', 'economy',
            'earnings', 'revenue', 'profit', 'loss', 'shares', 'price',
            'nasdaq', 'dow', 's&p', 'bond', 'federal', 'fed', 'rate',
            'bank', 'wall street', 'financial', 'economic', 'analyst',
            'forecast', 'outlook', 'quarter', 'quarterly', 'annual',
            'company', 'corp', 'corporation', 'inc', 'billion', 'million',
            'dividend', 'merger', 'acquisition', 'ipo', 'sec', 'ceo',
            'cfo', 'buyback', 'guidance', 'beat', 'miss', 'estimate'
        ]
        
        # Skip common non-financial terms
        skip_terms = [
            'sports', 'weather', 'celebrity', 'entertainment', 'movie',
            'music', 'fashion', 'recipe', 'health tips', 'lifestyle'
        ]
        
        has_financial_content = any(keyword in headline_lower for keyword in financial_keywords)
        has_skip_content = any(term in headline_lower for term in skip_terms)
        
        if has_financial_content and not has_skip_content:
            unique_headlines.append(headline)
            seen.add(headline_lower)

    print(f"\n✅ Collected {len(unique_headlines)} unique financial headlines.")
    return unique_headlines

def scrape_quick():
    """Quick scrape from RSS feeds (most reliable)"""
    headlines = []
    
    rss_scrapers = [
        ("Yahoo Finance RSS", scrape_yahoo_rss),
        ("MarketWatch RSS", scrape_marketwatch_rss),
        ("Reuters RSS", scrape_reuters_rss),
        ("CNBC RSS", scrape_cnbc_rss)
    ]
    
    for source_name, scraper_func in rss_scrapers:
        try:
            source_headlines = scraper_func()
            headlines.extend(source_headlines)
        except Exception as e:
            print(f"❌ Error scraping {source_name}: {str(e)}")
    
    # Add some web sources that are typically reliable
    try:
        headlines.extend(scrape_seeking_alpha())
        headlines.extend(scrape_finviz())
    except:
        pass
    
    # Clean and deduplicate
    unique_headlines = list(set([h.strip() for h in headlines if len(h.split()) > 4]))
    print(f"✅ Quick scrape collected {len(unique_headlines)} headlines.")
    return unique_headlines


if __name__ == "__main__":
    data = scrape_all()
    for i, h in enumerate(data[:10], 1):
        print(f"{i}. {h}")
