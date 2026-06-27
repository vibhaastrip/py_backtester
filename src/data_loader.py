import os
import sqlite3
import pandas as pd
import yfinance as yf

class DataLoader:
    def __init__(self, db_name="market_data.db"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_dir = os.path.join(base_dir, "data")

        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, db_name)

    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def download_to_db(self,tickers,start_date,end_date, interval='1d'):
        conn = self._get_connection()

        if isinstance(tickers,str):
            tickers = [tickers]
        print(f"Starting data extraction into: {self.db_path}")

        for ticker in tickers:
            print(f"Fetching data for {ticker} ...")
            try:
                df = yf.download(ticker, start=start_date, end=end_date, interval = interval)

                if df.empty:
                    print(f"## No data for {ticker} ##")
                    continue
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                df = df.reset_index()

                df.columns = [col.lower().replace(" ","_") for col in df.columns]

                table_name = ticker.replace("^", "INDEX_").replace("=", "").replace("-","_")
                df.to_sql(table_name, conn, if_exists="replace", index=False)

                print(f"Successfully saved {len(df)} roes to table '{table_name}'")
            except:
                print(f"Failed to download {ticker}. Error: {e}")

        conn.close()
        print("Data extraction complete")

    def load_data(self,ticker, start_date= None, end_date = None):
        table_name = ticker.replace("^", "INDEX_").replace("=", "").replace("-","_")
        conn = self._get_connection()
        query = f"SELECT * FROM {table_name}"

        try:
            df = pd.read_sql_query(query, conn)
            if 'data' in df.columns:
                df['data'] = pd.to_datatime(df['date'])
                if start_date:
                    df = df[df['date'] >= start_date]
                if end_date:
                    df = df[df['date'] <= end_date]
                
                df.set_index('date', inplace=True)

            conn.close()
            return df
        except Exception as e:
            print(f"Could not load data for {ticker} Error: {e}")
            conn.close()
            return None
        


# Execution test
if __name__ == "__main__":
    loader = DataLoader()

    # A mix of stocks and commodities with YFinance tickers
    # AAPL = Apple, GC=F = Gold Futures, MSFT = Microsoft
    test_tickers = ["AAPL", "MSFT", "GC=F"]
    loader.download_to_db(
        tickers=test_tickers, 
        start_date="2020-01-01", 
        end_date="2025-12-31"
    )
    print("\n--- Testing Data Extraction ---")
    
    # Test for Apple's data to see if it works
    aapl_data = loader.load_data("AAPL")
    
    if aapl_data is not None:
        print(f"Successfully loaded {len(aapl_data)} days of AAPL data.")
        print("Here are the first 3 days:")
        print(aapl_data.head(3)) # .head() prints the top rows of a DataFrame