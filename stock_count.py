import pandas as pd
import requests
import io  # Missing import added here

def get_nse_stock_count():
    try:
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.nseindia.com/'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Use io module to convert text response to file-like object
        df = pd.read_csv(io.StringIO(response.text))
        return len(df)
    
    except Exception as e:
        print(f"\nError details: {str(e)}")
        return None

count = get_nse_stock_count()
if count:
    print(f"Currently listed stocks on NSE: {count}")
else:
    print("Could not fetch data. Check internet connection or try again later.")