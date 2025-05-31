import pandas as pd
import yfinance as yf
import requests
import time
import io
from tqdm import tqdm

# Configure settings
requests.packages.urllib3.disable_warnings()

def get_nse_stocks():
    """Fetch list of all NSE-listed stocks"""
    try:
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.nseindia.com/'
        }
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        df = pd.read_csv(
            io.StringIO(response.text),
            dtype={'SYMBOL': str},
            usecols=['SYMBOL'],
            on_bad_lines='skip'
        )
        
        print(f"Successfully fetched {len(df)} NSE stocks")
        return df['SYMBOL'].unique().tolist()
    
    except Exception as e:
        print(f"Failed to fetch NSE list: {str(e)}")
        return []

def analyze_growth():
    symbols = get_nse_stocks()
    if not symbols:
        return []
    
    doubled_stocks = []
    
    print(f"\nAnalyzing all {len(symbols)} symbols...")
    
    for symbol in tqdm(symbols, desc="Processing Stocks"):
        try:
            yf_symbol = f"{symbol}.NS"
            data = yf.download(yf_symbol, period="6mo", progress=False, threads=True)
            
            if len(data) < 60:
                continue
                
            start_price = data['Adj Close'].iloc[0]
            end_price = data['Adj Close'].iloc[-1]
            
            if start_price <= 10 or end_price <= 10:
                continue
                
            current_volume = data['Volume'].mean()
            if current_volume < 100000:
                continue
                
            growth = ((end_price - start_price)/start_price)*100
            
            if growth >= 100:
                doubled_stocks.append({
                    'Symbol': yf_symbol,
                    'Start Price': round(start_price, 2),
                    'End Price': round(end_price, 2),
                    'Growth %': round(growth, 2),
                    '3M Avg Volume': f"{current_volume:,.0f}"
                })
            
            time.sleep(0.15)
            
        except Exception as e:  # Properly indented except block
            continue
    
    return doubled_stocks  # Now correctly aligned

if __name__ == "__main__":
    print("Starting comprehensive analysis...")
    results = analyze_growth()
    
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('Growth %', ascending=False)
        df.to_csv('all_doubled_stocks.csv', index=False)
        print(f"\nFound {len(results)} stocks that doubled:")
        print(df[['Symbol', 'Growth %', 'Start Price', 'End Price', '3M Avg Volume']].to_string(index=False))
    else:
        print("\nNo doubling stocks found in the analysis")