"""
Real news scraper - no API limits, just scrape everything
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

class NewsAggregator:
    """Scrapes news from multiple sources without API limits"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_globenewswire(self, keywords):
        """Scrape GlobeNewswire directly"""
        results = []
        try:
            url = "https://www.globenewswire.com/en/search/keyword/" + "%20".join(keywords[:3])
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for article in soup.find_all('div', class_='search-result-item')[:10]:
                try:
                    title = article.find('h3')
                    if not title:
                        continue
                    
                    title_text = title.get_text(strip=True)
                    link = article.find('a')['href'] if article.find('a') else ''
                    date_elem = article.find('time')
                    date = date_elem['datetime'] if date_elem and date_elem.get('datetime') else ''
                    
                    # Extract tickers
                    tickers = re.findall(r'\b([A-Z]{2,5})\b', title_text)
                    
                    results.append({
                        'source': 'GlobeNewswire',
                        'title': title_text,
                        'url': link if link.startswith('http') else f"https://www.globenewswire.com{link}",
                        'date': date,
                        'tickers': tickers[:3],
                        'scraped_at': datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Parse error: {e}")
                    continue
            
            logger.info(f"GlobeNewswire: {len(results)} articles")
        except Exception as e:
            logger.error(f"GlobeNewswire scrape error: {e}")
        
        return results
    
    def scrape_prnewswire(self, keywords):
        """Scrape PRNewswire directly"""
        results = []
        try:
            search_term = "+".join(keywords[:3])
            url = f"https://www.prnewswire.com/search/news/?keyword={search_term}"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for article in soup.find_all('div', class_='card')[:10]:
                try:
                    title_elem = article.find('h3') or article.find('a', class_='newsreleaseconsolidatelink')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link_elem = article.find('a', href=True)
                    link = link_elem['href'] if link_elem else ''
                    
                    date_elem = article.find('small') or article.find('span', class_='mb-0')
                    date = date_elem.get_text(strip=True) if date_elem else ''
                    
                    tickers = re.findall(r'\b([A-Z]{2,5})\b', title)
                    
                    results.append({
                        'source': 'PRNewswire',
                        'title': title,
                        'url': link if link.startswith('http') else f"https://www.prnewswire.com{link}",
                        'date': date,
                        'tickers': tickers[:3],
                        'scraped_at': datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Parse error: {e}")
                    continue
            
            logger.info(f"PRNewswire: {len(results)} articles")
        except Exception as e:
            logger.error(f"PRNewswire scrape error: {e}")
        
        return results
    
    def scrape_benzinga(self, ticker):
        """Scrape Benzinga for specific ticker"""
        results = []
        try:
            url = f"https://www.benzinga.com/quote/{ticker}/news"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for article in soup.find_all('div', class_='story-block')[:5]:
                try:
                    title_elem = article.find('h2') or article.find('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = article.find('a')['href'] if article.find('a') else ''
                    
                    results.append({
                        'source': 'Benzinga',
                        'title': title,
                        'url': link if link.startswith('http') else f"https://www.benzinga.com{link}",
                        'ticker': ticker,
                        'scraped_at': datetime.now().isoformat()
                    })
                except:
                    continue
            
            logger.info(f"Benzinga {ticker}: {len(results)} articles")
        except Exception as e:
            logger.error(f"Benzinga scrape error for {ticker}: {e}")
        
        return results
    
    def scrape_all(self, keywords, tickers):
        """Scrape all sources"""
        all_news = []
        
        # Scrape by keywords
        all_news.extend(self.scrape_globenewswire(keywords))
        time.sleep(1)  # Be respectful
        all_news.extend(self.scrape_prnewswire(keywords))
        
        # Scrape specific tickers (limit to prevent rate limiting)
        for ticker in tickers[:5]:  # Top 5 tickers only
            time.sleep(0.5)
            all_news.extend(self.scrape_benzinga(ticker))
        
        return all_news
    
    def filter_hot_news(self, articles, hot_keywords):
        """Filter for urgent catalyst keywords"""
        hot = []
        for article in articles:
            title_lower = article['title'].lower()
            if any(kw in title_lower for kw in hot_keywords):
                article['hot'] = True
                hot.append(article)
        
        logger.info(f"🔥 {len(hot)} HOT articles found")
        return hot


# Aggressive keyword list based on your research
HOT_KEYWORDS = [
    'nvidia', 'gpu', 'b300', 'b200', 'blackwell',
    'phase 3', 'trial results', 'fda approval', 'endpoints met',
    'government contract', 'defense contract', '$100m', '$50m',
    'merger', 'acquisition', 'per share', 'announces',
    'operational', 'begins operations', 'launches'
]

SEARCH_KEYWORDS = [
    ['nvidia', 'gpu', 'contract'],
    ['phase', 'trial', 'fda'],
    ['government', 'defense', 'contract'],
    ['merger', 'acquisition'],
    ['biotech', 'clinical', 'approval']
]
