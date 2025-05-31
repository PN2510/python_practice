import yfinance as yf
import pandas as pd
import time
# We'll comment out nsepython imports for now to ensure the script runs with CSV
# from nsepython import ... # We can revisit this if a stable method is found

# --- Configuration ---
YEARS_FOR_PROFITABILITY = 5
DEBT_TO_EQUITY_THRESHOLD = 1.0
ROE_THRESHOLD = 0.15  # 15%
ROCE_THRESHOLD = 0.15 # 15%
NIFTY_INDEX_NAME = "NIFTY 500" 
CSV_FILENAME = "nifty_500_constituents.csv" # Make sure this file exists!

# --- NSE Symbol Fetching ---
def get_index_symbols_from_csv(index_name="NIFTY 500", csv_filename="nifty_500_constituents.csv"):
    """
    Loads stock symbols for a given NSE index primarily from a local CSV file.
    Returns a list of symbols (e.g., ['RELIANCE', 'INFY']) or an empty list on failure.
    """
    print(f"Loading symbols for {index_name} from local CSV: '{csv_filename}'...")
    symbols = []
    try:
        df = pd.read_csv(csv_filename)
        df.columns = [col.lower().strip() for col in df.columns] # Standardize column names

        # Common column names for symbols in NSE downloaded CSVs
        potential_symbol_columns = ['symbol', 'security name', 'company name'] 
        symbol_col_found = None

        for col_name in potential_symbol_columns:
            if col_name in df.columns:
                symbol_col_found = col_name
                break
        
        if symbol_col_found:
            print(f"Using column '{symbol_col_found}' from CSV for stock symbols.")
            # If using 'company name', it's often the symbol itself in index constituents.
            # If 'series' column exists, we might filter for 'EQ', but for index constituents,
            # 'company name' usually directly maps to the equity symbol.
            if symbol_col_found == 'company name' and 'series' in df.columns:
                # Check if filtering by 'EQ' series is necessary or if all entries are relevant
                # For NIFTY 500, 'company name' is typically the symbol.
                # If distinct symbols are much less than rows, then series 'EQ' might be good.
                if len(df[df['series'] == 'EQ']) > 0 and len(df[df['series'] == 'EQ']) < len(df):
                     print("Filtering by 'EQ' series for 'company name' column.")
                     symbols = df[df['series'] == 'EQ'][symbol_col_found].astype(str).str.strip().tolist()
                else:
                    symbols = df[symbol_col_found].astype(str).str.strip().tolist()
            else:
                symbols = df[symbol_col_found].astype(str).str.strip().tolist()
        else:
            print(f"Error: CSV file '{csv_filename}' found, but a suitable symbol column (like {potential_symbol_columns}) was not found.")
            print(f"Available columns in CSV (lowercased): {df.columns.tolist()}")
            return []
        
        symbols = [s for s in symbols if pd.notna(s) and s and s != "nan"] # Clean symbols

        if symbols:
            print(f"Successfully loaded {len(symbols)} symbols from {csv_filename}.")
            return symbols
        else:
            print(f"No valid symbols extracted from {csv_filename} or the identified column was effectively empty.")
            return []

    except FileNotFoundError:
        print(f"\n--- IMPORTANT ---")
        print(f"FATAL ERROR: CSV file '{csv_filename}' not found in the script's directory: {os.getcwd()}") # Show current dir
        print(f"This script now primarily relies on this CSV file for the stock list.")
        print(f"Please download the {index_name} constituents CSV from the NSE India website:")
        print(f"  1. Go to nseindia.com -> Market Data -> Indices.")
        print(f"  2. Select '{index_name}' from the dropdown list (e.g., NIFTY 500).")
        print(f"  3. Click the 'Download (.csv)' button (often on the right side).")
        print(f"  4. Save the file as '{csv_filename}' in the same directory as this script.")
        print(f"  5. Ensure the CSV file has a column like 'Symbol', 'Security Name', or 'Company Name' containing the stock tickers.")
        print(f"-----------------")
        return []
    except Exception as ex_csv:
        print(f"Error reading or processing CSV '{csv_filename}': {ex_csv}")
        return []
    
    return symbols

# --- Financial Data Fetching & Analysis Functions (Assumed Unchanged) ---
# get_ticker_data, is_consistently_profitable, has_low_debt, has_good_returns
# --- Main Execution Block (Modified to use new function name) ---

import os # For showing current directory in case of FileNotFoundError

# --- PASTE YOUR FINANCIAL FUNCTIONS HERE (get_ticker_data, is_consistently_profitable, etc.) ---
def get_ticker_data(symbol_with_suffix):
    """Fetches data for a given stock symbol (e.g., RELIANCE.NS)."""
    try:
        stock = yf.Ticker(symbol_with_suffix)
        info = stock.info
        financials = stock.financials # Annual
        balance_sheet = stock.balance_sheet # Annual
        
        if not info and financials.empty and balance_sheet.empty:
             # print(f"  - Data: No data returned by yfinance for {symbol_with_suffix}.") # Too verbose
             return None, None, None, None
        return stock, info, financials, balance_sheet
    except Exception as e:
        # print(f"  - Data: Could not fetch yfinance data for {symbol_with_suffix}: {e}") # Can be too verbose
        return None, None, None, None

def is_consistently_profitable(financials, symbol, years=YEARS_FOR_PROFITABILITY):
    """Checks if 'Net Income' has been positive for the last 'years'."""
    if financials is None or financials.empty:
        print(f"  - {symbol} | Profitability: Financials data not available.")
        return False
    try:
        if 'Net Income' not in financials.index:
            print(f"  - {symbol} | Profitability: 'Net Income' not found in financials.")
            return False

        net_income_series = financials.loc['Net Income']
        if len(net_income_series.columns) < years: 
            print(f"  - {symbol} | Profitability: Not enough data (available: {len(net_income_series.columns)}, needed: {years}).")
            return False

        recent_net_incomes = net_income_series.iloc[:, :years] 
        
        if recent_net_incomes.isnull().values.any(): 
            print(f"  - {symbol} | Profitability: Contains NaN values in net income for the last {years} years.")
            return False
            
        profitable_years = (recent_net_incomes > 0).all(axis=None) 
        
        if profitable_years:
            return True
        else:
            num_profitable = (recent_net_incomes > 0).sum().sum() 
            print(f"  - {symbol} | Profitability: Not consistently profitable (profitable in {num_profitable}/{recent_net_incomes.size} periods of last {years} years). (Fail)")
            return False
    except KeyError:
        print(f"  - {symbol} | Profitability: 'Net Income' key missing from financials.")
        return False
    except Exception as e:
        print(f"  - {symbol} | Profitability: Error checking profitability: {e}")
        return False

def has_low_debt(balance_sheet, info, symbol, threshold=DEBT_TO_EQUITY_THRESHOLD):
    """Checks if Debt-to-Equity ratio is below the threshold."""
    d_e_ratio = None
    if info and 'debtToEquity' in info and info['debtToEquity'] is not None and not pd.isna(info['debtToEquity']): # Added NaN check for info
        val = info['debtToEquity']
        d_e_ratio = val / 100.0 if val > 5 else val # Handle if it's percentage or ratio
    
    if d_e_ratio is None: # Only calculate if not found in info or info value was NaN
        if balance_sheet is None or balance_sheet.empty:
            print(f"  - {symbol} | Debt: Balance sheet data not available for D/E calculation.")
            return False
        try:
            latest_balance_sheet = balance_sheet.iloc[:, 0] 

            total_debt = latest_balance_sheet.get('Total Debt')
            if total_debt is None or pd.isna(total_debt): 
                ltd = latest_balance_sheet.get('Long Term Debt')
                sstd = latest_balance_sheet.get('Short Long Term Debt')
                
                ltd_val = ltd if pd.notna(ltd) else 0
                sstd_val = sstd if pd.notna(sstd) else 0
                
                calculated_debt = ltd_val + sstd_val
                
                if calculated_debt == 0 and pd.notna(ltd) and ltd != 0:
                    total_debt = ltd
                elif calculated_debt != 0 : 
                    total_debt = calculated_debt
                # If still None (i.e. calculated_debt is 0 and ltd was 0 or None) total_debt remains None or original NaN

            shareholder_equity = latest_balance_sheet.get('Total Stockholder Equity')

            if total_debt is None or pd.isna(total_debt): 
                print(f"  - {symbol} | Debt: Could not determine valid Total Debt from balance sheet.")
                return False
            if shareholder_equity is None or pd.isna(shareholder_equity):
                print(f"  - {symbol} | Debt: Could not determine valid Shareholder Equity from balance sheet.")
                return False
            if shareholder_equity == 0:
                print(f"  - {symbol} | Debt: Shareholder Equity is zero. D/E is effectively infinite or undefined.")
                return False 

            d_e_ratio = total_debt / shareholder_equity
        except (KeyError, IndexError) as e:
            print(f"  - {symbol} | Debt: Missing key/data in balance sheet for D/E calculation: {e}")
            return False
        except Exception as e:
            print(f"  - {symbol} | Debt: Error calculating D/E: {e}")
            return False
            
    if d_e_ratio is not None and not pd.isna(d_e_ratio) and d_e_ratio < threshold:
        return True
    else:
        if d_e_ratio is not None and not pd.isna(d_e_ratio):
            print(f"  - {symbol} | Debt: High debt (D/E: {d_e_ratio:.2f} >= {threshold}). (Fail)")
        elif pd.isna(d_e_ratio):
             print(f"  - {symbol} | Debt: D/E ratio calculated as NaN or from NaN source. (Fail)")
        # else d_e_ratio is None, meaning it couldn't be determined from info or calculation
        return False

def has_good_returns(financials, balance_sheet, info, symbol, roe_thresh=ROE_THRESHOLD, roce_thresh=ROCE_THRESHOLD):
    """Checks if ROE and ROCE are above their respective thresholds."""
    if financials is None or financials.empty or balance_sheet is None or balance_sheet.empty:
        print(f"  - {symbol} | Returns: Financials or Balance Sheet data not available.")
        return False

    roe = None
    if info and 'returnOnEquity' in info and info['returnOnEquity'] is not None and not pd.isna(info['returnOnEquity']):
        roe = info['returnOnEquity']
    else:
        try:
            net_income = financials.loc['Net Income'].iloc[0] 
            shareholder_equity = balance_sheet.loc['Total Stockholder Equity'].iloc[0] 
            if pd.notna(shareholder_equity) and shareholder_equity != 0 and pd.notna(net_income):
                roe = net_income / shareholder_equity
            elif shareholder_equity == 0:
                print(f"  - {symbol} | ROE: Shareholder Equity is zero, cannot calculate ROE.")
            elif pd.isna(shareholder_equity) or pd.isna(net_income):
                print(f"  - {symbol} | ROE: Net Income or Shareholder Equity is NaN.")

        except (KeyError, IndexError) as e:
            print(f"  - {symbol} | ROE: Could not calculate ROE (missing data): {e}")
        except Exception as e:
            print(f"  - {symbol} | ROE: Error calculating ROE: {e}")

    if roe is None or pd.isna(roe) or roe <= roe_thresh:
        if roe is not None and not pd.isna(roe):
            print(f"  - {symbol} | Returns: ROE ({roe:.2%}) is not > {roe_thresh:.0%}. (ROE Fail)")
        elif pd.isna(roe):
            print(f"  - {symbol} | Returns: ROE is NaN. (ROE Fail)")
        else: # roe is None
            print(f"  - {symbol} | Returns: ROE could not be determined. (ROE Fail)")
        return False

    roce = None
    try:
        ebit = financials.loc['Ebit'].iloc[0] 
        latest_balance_sheet = balance_sheet.iloc[:, 0]
        capital_employed = None
        
        total_assets = latest_balance_sheet.get('Total Assets')
        current_liabilities = latest_balance_sheet.get('Total Current Liabilities')

        if pd.notna(total_assets) and pd.notna(current_liabilities):
            ce_val = total_assets - current_liabilities
            if ce_val != 0: capital_employed = ce_val
        
        if capital_employed is None or capital_employed == 0: 
            shareholder_equity_roce = latest_balance_sheet.get('Total Stockholder Equity')
            total_debt_bs_roce = latest_balance_sheet.get('Total Debt')
            
            if total_debt_bs_roce is None or pd.isna(total_debt_bs_roce):
                 ltd_roce = latest_balance_sheet.get('Long Term Debt')
                 sstd_roce = latest_balance_sheet.get('Short Long Term Debt')
                 ltd_roce_val = ltd_roce if pd.notna(ltd_roce) else 0
                 sstd_roce_val = sstd_roce if pd.notna(sstd_roce) else 0
                 total_debt_bs_roce = ltd_roce_val + sstd_roce_val
            
            if pd.notna(shareholder_equity_roce) and pd.notna(total_debt_bs_roce):
                ce_val = shareholder_equity_roce + total_debt_bs_roce
                if ce_val != 0: capital_employed = ce_val

        if pd.notna(ebit) and capital_employed is not None and capital_employed != 0 and pd.notna(capital_employed):
            roce = ebit / capital_employed
        elif capital_employed == 0 :
             print(f"  - {symbol} | ROCE: Calculated Capital Employed is zero. Cannot calculate ROCE.")
        elif pd.isna(ebit):
            print(f"  - {symbol} | ROCE: EBIT is NaN. Cannot calculate ROCE.")
        elif capital_employed is not None and pd.isna(capital_employed):
             print(f"  - {symbol} | ROCE: Capital Employed calculated as NaN. Cannot calculate ROCE.")
        else: 
            print(f"  - {symbol} | ROCE: Could not determine valid Capital Employed or EBIT for ROCE.")

    except (KeyError, IndexError) as e:
        print(f"  - {symbol} | ROCE: Missing data for ROCE (e.g., EBIT, BS items): {e}")
    except Exception as e:
        print(f"  - {symbol} | ROCE: Error calculating ROCE: {e}")

    if roce is None or pd.isna(roce) or roce <= roce_thresh:
        if roce is not None and not pd.isna(roce):
            print(f"  - {symbol} | Returns: ROCE ({roce:.2%}) is not > {roce_thresh:.0%}. (ROCE Fail)")
        elif pd.isna(roce):
            print(f"  - {symbol} | Returns: ROCE is NaN. (ROCE Fail)")
        else: # roce is None
            print(f"  - {symbol} | Returns: ROCE could not be determined. (ROCE Fail)")
        return False
    
    return True

def screen_stocks(stock_symbols_with_suffix):
    passed_stocks = []
    total_symbols = len(stock_symbols_with_suffix)
    print(f"\nStarting screening for {total_symbols} symbols...\n")

    for i, symbol_ns in enumerate(stock_symbols_with_suffix):
        print(f"--- ({i+1}/{total_symbols}) Processing: {symbol_ns} ---")
        
        stock, info, financials, balance_sheet = get_ticker_data(symbol_ns)

        if not stock and not info and (financials is None or financials.empty) and \
           (balance_sheet is None or balance_sheet.empty):
            print(f"  - {symbol_ns} | Skipping due to no data from yfinance.")
            time.sleep(0.2) 
            continue

        if not is_consistently_profitable(financials, symbol_ns):
            time.sleep(1) 
            continue 

        if not has_low_debt(balance_sheet, info, symbol_ns):
            time.sleep(1)
            continue

        if has_good_returns(financials, balance_sheet, info, symbol_ns):
            print(f"--- {symbol_ns} QUALIFIED ---")
            passed_stocks.append(symbol_ns)
        
        time.sleep(1) 
    return passed_stocks

if __name__ == "__main__":
    print("="*50)
    print("NSE Stock Screener")
    print("="*50)
    print(f"Criteria: \n1. Consistently Profitable (net income > 0 for last {YEARS_FOR_PROFITABILITY} years)")
    print(f"2. Low Debt (Debt-to-Equity < {DEBT_TO_EQUITY_THRESHOLD})")
    print(f"3. Good Returns (ROE > {ROE_THRESHOLD*100:.0f}% AND ROCE > {ROCE_THRESHOLD*100:.0f}%)")
    print("-" * 30)

    # Now primarily uses CSV
    base_symbols = get_index_symbols_from_csv(index_name=NIFTY_INDEX_NAME, csv_filename=CSV_FILENAME)
    
    if base_symbols:
        nse_symbols_with_suffix = [
            f"{str(symbol).strip().upper()}.NS" for symbol in base_symbols 
            if isinstance(symbol, str) and str(symbol).strip() and str(symbol).strip().lower() != "nan"
        ]
        nse_symbols_with_suffix = sorted(list(set(nse_symbols_with_suffix)))

        print(f"\nPrepared {len(nse_symbols_with_suffix)} unique symbols for yfinance screening (e.g., {nse_symbols_with_suffix[0] if nse_symbols_with_suffix else 'N/A'}).")
        
        if not nse_symbols_with_suffix:
             print("\nNo valid symbols to screen after processing the list.")
        else:
            # --- Optional: For faster testing ---
            # test_subset = nse_symbols_with_suffix[:5] 
            # print(f"*** TESTING WITH A SUBSET OF {len(test_subset)} STOCKS: {test_subset} ***")
            # nse_symbols_to_screen = test_subset
            # --- --- --- --- --- --- --- --- --- ---
            nse_symbols_to_screen = nse_symbols_with_suffix

            qualified_stocks = screen_stocks(nse_symbols_to_screen)

            print("\n" + "=" * 30)
            print("SCREENING COMPLETE")
            print("=" * 30)
            if qualified_stocks:
                print(f"\n{len(qualified_stocks)} Stocks that passed all criteria:")
                for stock_symbol in qualified_stocks:
                    print(f"- {stock_symbol}")
            else:
                print(f"\nNo stocks passed all criteria from the {NIFTY_INDEX_NAME} list (or the subset processed).")
    else:
        print(f"\nNo stock symbols were available for {NIFTY_INDEX_NAME} to screen from CSV.")
        print("Please ensure the CSV file is correctly downloaded, named, and placed, and contains a recognizable symbol column.")

    print("\nDisclaimer: Financial data from yfinance can be incomplete or delayed for Indian stocks.")
    print("Always cross-verify with official sources before making investment decisions.")
    print("This script is for educational purposes and not financial advice.")