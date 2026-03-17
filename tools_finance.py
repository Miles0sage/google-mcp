import urllib.request
import urllib.parse
import json
import re
from typing import Dict, Optional


def stock_quote(symbol: str) -> str:
    """
    Get real-time stock quote using Google Finance page scraping.

    Args:
        symbol: Stock symbol to look up

    Returns:
        Formatted string with stock information
    """
    # Try Google Finance first
    for exchange in ['NASDAQ', 'NYSE']:
        try:
            url = f"https://www.google.com/finance/quote/{symbol}:{exchange}"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

            response = urllib.request.urlopen(req)
            html = response.read().decode('utf-8')

            # Extract price
            price_match = re.search(r'"Price"(?:[^"]*"){1}[^>]*>([\d,]+\.?\d*)', html)
            if not price_match:
                price_match = re.search(r'"(\d+\.?\d+)"[^"]*aria-label="United States Dollar"', html)

            if price_match:
                price = price_match.group(1)

                # Extract change and change percent
                change_match = re.search(r'([+-]?[\d,]+\.?\d*)\s*\(([-+]?[\d,]*\.?\d*)%', html)
                change = change_match.group(1) if change_match else "N/A"
                change_percent = change_match.group(2) if change_match else "N/A"

                # Extract 52-week range
                week_52_match = re.search(r'52 Week Range[^"]*">\s*([\d,]+\.?\d+)\s*-?\s*([\d,]+\.?\d+)', html)
                week_52_low = week_52_match.group(1) if week_52_match else "N/A"
                week_52_high = week_52_match.group(2) if week_52_match else "N/A"

                # Extract market cap
                market_cap_match = re.search(r'Market Cap[^"]*">\s*([\$A-Z\d.]+)', html)
                market_cap = market_cap_match.group(1) if market_cap_match else "N/A"

                # Extract P/E ratio
                pe_match = re.search(r'PE Ratio[^"]*">\s*([\d.]+)', html)
                pe_ratio = pe_match.group(1) if pe_match else "N/A"

                result = f"""Stock Quote: {symbol}
Price: ${price}
Change: {change} ({change_percent}%)
Market Cap: {market_cap}
P/E Ratio: {pe_ratio}
52-Week Range: ${week_52_low} - ${week_52_high}
Exchange: {exchange}
"""
                return result

        except Exception:
            continue

    # If Google Finance fails, try Yahoo Finance API
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))

        quote_data = data.get('chart', {}).get('result', [{}])[0].get('meta', {})

        price = quote_data.get('regularMarketPrice', 'N/A')
        previous_close = quote_data.get('previousClose', 'N/A')

        if previous_close != 'N/A' and price != 'N/A':
            change = round(price - previous_close, 2)
            change_percent = round(((price - previous_close) / previous_close) * 100, 2)
        else:
            change = 'N/A'
            change_percent = 'N/A'

        result = f"""Stock Quote: {symbol}
Price: ${price}
Change: {change} ({change_percent}%)
Market Cap: {quote_data.get('marketCap', 'N/A')}
P/E Ratio: {quote_data.get('trailingPE', 'N/A')}
52-Week Range: ${quote_data.get('fiftyTwoWeekLow', 'N/A')} - ${quote_data.get('fiftyTwoWeekHigh', 'N/A')}
Exchange: {quote_data.get('exchangeName', 'N/A')}
"""
        return result
    except Exception as e:
        return f"Error fetching stock data for {symbol}: {str(e)}"


def market_overview() -> str:
    """
    Get major market indices overview (S&P 500, NASDAQ, DOW).

    Returns:
        Formatted string with market indices information
    """
    indices = {
        "^GSPC": "S&P 500",
        "^IXIC": "NASDAQ",
        "^DJI": "DOW Jones"
    }

    result = "Market Overview:\n"

    for symbol, name in indices.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

            response = urllib.request.urlopen(req)
            data = json.loads(response.read().decode('utf-8'))

            quote_data = data.get('chart', {}).get('result', [{}])[0].get('meta', {})

            price = quote_data.get('regularMarketPrice', 'N/A')
            previous_close = quote_data.get('previousClose', 'N/A')

            if previous_close != 'N/A' and price != 'N/A':
                change = round(price - previous_close, 2)
                change_percent = round(((price - previous_close) / previous_close) * 100, 2)
            else:
                change = 'N/A'
                change_percent = 'N/A'

            result += f"{name}: {price} ({change:+.2f}, {change_percent:+.2f}%)\n"

        except Exception as e:
            result += f"{name}: Error fetching data - {str(e)}\n"

    return result