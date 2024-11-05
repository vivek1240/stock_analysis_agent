# tools.py

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# 2. Tool Functions
# tools.py

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_top_performing_stocks():
    # Replace these with your own values or use environment variables
    API_KEY = os.getenv('GOOGLE_API_KEY')         # Your API key from Google Cloud Console
    SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')  # Your Custom Search Engine ID (cx)
    
    # Check if API keys are set
    if not API_KEY or not SEARCH_ENGINE_ID:
        raise ValueError("Google API key and Search Engine ID must be set as environment variables.")

    # Search query
    query = "top performing stocks today in US"

    # API endpoint and parameters
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": 3  # Number of results to return
    }

    # Make the request to Google Custom Search API
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json()
        links = [item['link'] for item in results.get('items', [])]
    else:
        print(f"Error: {response.status_code}")
        return []

    # User-Agent to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Function to scrape stock data and extract company names
    def generic_scraper(url):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            company_names = []

            # Extract company names based on known website structures
            parsed_url = urlparse(url)
            domain = parsed_url.netloc

            if 'marketwatch.com' in domain:
                # Example for MarketWatch
                for row in soup.find_all("tr", class_="table__row"):
                    name_tag = row.find("a", class_="link")
                    if name_tag:
                        company_name = name_tag.get_text(strip=True)
                        company_names.append(company_name)
            elif 'investing.com' in domain:
                # Example for Investing.com
                for row in soup.find_all("tr", class_="js-row"):
                    name_tag = row.find("td", class_="left bold plusIconTd elp")
                    if name_tag:
                        company_name = name_tag.get_text(strip=True)
                        company_names.append(company_name)
            else:
                # Generic extraction logic
                for row in soup.find_all("tr"):
                    cells = row.find_all("td")
                    for cell in cells:
                        text = cell.get_text(strip=True)
                        # Simple heuristic to identify company names
                        if text and len(text.split()) > 1 and not text.isupper():
                            company_names.append(text)
            return company_names
        else:
            print(f"Failed to retrieve {url} with status code: {response.status_code}")
            return []

    # Collect company names from each link
    company_names = []
    for link in links:
        print(f"Scraping data from: {link}")
        data = generic_scraper(link)
        if data:
            company_names.extend(data)
        else:
            print("No data found or unable to scrape.")

    # Remove duplicates and limit to top 10 companies
    unique_companies = list(dict.fromkeys(company_names))  # Preserves order
    top_companies = unique_companies[:10]
    return top_companies



def get_basic_stock_info(ticker: str) -> dict:
    """Retrieves basic information about a single stock."""
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
        basic_info = {
            'Name': info.get('longName', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Market Cap': info.get('marketCap', 'N/A'),
            'Current Price': info.get('currentPrice', 'N/A'),
            '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
            'Average Volume': info.get('averageVolume', 'N/A')
        }
        return basic_info
    except Exception as e:
        print(f"Error fetching basic info for {ticker}: {e}")
        return {}

def get_fundamental_analysis(ticker: str) -> dict:
    """Performs fundamental analysis on a given stock."""
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
        fundamental_analysis = {
            'PE Ratio': info.get('trailingPE', 'N/A'),
            'Forward PE': info.get('forwardPE', 'N/A'),
            'PEG Ratio': info.get('pegRatio', 'N/A'),
            'Price to Book': info.get('priceToBook', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A'),
            'EPS (TTM)': info.get('trailingEps', 'N/A'),
            'Revenue Growth': info.get('revenueGrowth', 'N/A'),
            'Profit Margin': info.get('profitMargins', 'N/A'),
            'Free Cash Flow': info.get('freeCashflow', 'N/A'),
            'Debt to Equity': info.get('debtToEquity', 'N/A'),
            'Return on Equity': info.get('returnOnEquity', 'N/A'),
            'Operating Margin': info.get('operatingMargins', 'N/A'),
            'Quick Ratio': info.get('quickRatio', 'N/A'),
            'Current Ratio': info.get('currentRatio', 'N/A'),
            'Earnings Growth': info.get('earningsGrowth', 'N/A'),
        }
        return fundamental_analysis
    except Exception as e:
        print(f"Error fetching fundamental analysis for {ticker}: {e}")
        return {}

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(series, short_window=12, long_window=26, signal_window=9):
    short_ema = series.ewm(span=short_window, adjust=False).mean()
    long_ema = series.ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal

def analyze_trend(latest):
    if latest['Close'] > latest['SMA_50'] > latest['SMA_200']:
        return "Bullish"
    elif latest['Close'] < latest['SMA_50'] < latest['SMA_200']:
        return "Bearish"
    else:
        return "Neutral"

def analyze_macd(latest):
    if latest['MACD'] > latest['Signal']:
        return "Bullish"
    else:
        return "Bearish"

def analyze_rsi(latest):
    if latest['RSI'] > 70:
        return "Overbought"
    elif latest['RSI'] < 30:
        return "Oversold"
    else:
        return "Neutral"

def get_technical_analysis(ticker: str, period: str = '2y') -> dict:
    """Perform technical analysis on a given stock."""
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)

    if history.empty:
        print(f"No historical data for {ticker}.")
        return {}

    # Calculate indicators
    history['SMA_50'] = history['Close'].rolling(window=50).mean()
    history['SMA_200'] = history['Close'].rolling(window=200).mean()
    history['RSI'] = calculate_rsi(history['Close'])
    history['MACD'], history['Signal'] = calculate_macd(history['Close'])

    # Drop rows with NaN values
    history = history.dropna()

    if history.empty:
        print(f"Not enough data to perform technical analysis for {ticker}.")
        return {}

    latest = history.iloc[-1]

    analysis = {
        'Current Price': latest['Close'],
        '50-day SMA': latest['SMA_50'],
        '200-day SMA': latest['SMA_200'],
        'RSI (14-day)': latest['RSI'],
        'MACD': latest['MACD'],
        'MACD Signal': latest['Signal'],
        'Trend': analyze_trend(latest),
        'MACD Analysis': analyze_macd(latest),
        'RSI Analysis': analyze_rsi(latest)
    }

    return analysis

def calculate_beta(stock_returns, market_returns):
    # Align the dates of stock and market returns
    aligned_returns = pd.concat([stock_returns, market_returns], axis=1).dropna()
    if aligned_returns.empty:
        return 'N/A'

    covariance = aligned_returns.cov().iloc[0, 1]
    market_variance = aligned_returns.iloc[:, 1].var()

    return covariance / market_variance

def calculate_max_drawdown(prices):
    peak = prices.cummax()
    drawdown = (prices - peak) / peak
    return drawdown.min()

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    excess_returns = returns - risk_free_rate/252
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

def calculate_sortino_ratio(returns, risk_free_rate=0.02, target_return=0):
    excess_returns = returns - risk_free_rate/252
    downside_returns = excess_returns[excess_returns < target_return]
    if downside_returns.empty:
        return 'N/A'
    downside_deviation = np.sqrt(np.mean(downside_returns**2))
    return np.sqrt(252) * excess_returns.mean() / downside_deviation

def get_stock_risk_assessment(ticker: str, period: str = '1y') -> dict:
    """Performs a risk assessment on a given stock."""
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)

    if history.empty:
        print(f"No historical data for {ticker}.")
        return {}

    # Calculate daily returns
    returns = history['Close'].pct_change().dropna()
    if returns.empty:
        print(f"No return data for {ticker}.")
        return {}

    # Get market returns (using S&P 500 Index for US stocks)
    market_ticker = '^GSPC'  # S&P 500
    market = yf.Ticker(market_ticker)
    market_history = market.history(period=period)
    market_returns = market_history['Close'].pct_change().dropna()

    # Calculate risk metrics
    volatility = returns.std() * np.sqrt(252)  # Annualized volatility
    beta = calculate_beta(returns, market_returns)  # Beta relative to S&P 500
    var_95 = np.percentile(returns, 5)  # 95% Value at Risk
    max_drawdown = calculate_max_drawdown(history['Close'])

    risk_assessment = {
        'Annualized Volatility': volatility,
        'Beta': beta,
        'Value at Risk (95%)': var_95,
        'Maximum Drawdown': max_drawdown,
        'Sharpe Ratio': calculate_sharpe_ratio(returns),
        'Sortino Ratio': calculate_sortino_ratio(returns)
    }

    return risk_assessment

def get_stock_news(ticker: str, limit: int = 5) -> list:
    """Fetches recent news articles related to a specific stock."""
    stock = yf.Ticker(ticker)
    try:
        news = stock.news[:limit]

        news_data = []
        for article in news:
            news_entry = {
                "Title": article.get('title', 'N/A'),
                "Publisher": article.get('publisher', 'N/A'),
                "Published": datetime.fromtimestamp(article.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                "Link": article.get('link', 'N/A')
            }
            news_data.append(news_entry)

        return news_data
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []
