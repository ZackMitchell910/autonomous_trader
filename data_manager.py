import time
import pandas as pd
import numpy as np
import datetime
import cbpro

from coinbase.rest import RESTClient
from config import COINBASE_API_KEY, COINBASE_API_SECRET

class DataManager:
    def __init__(self, product_ids=None, granularity=3600):
        """
        product_ids: list of trading pairs, e.g., ['BTC-USD', 'ETH-USD', 'SOL-USD']
        granularity: candle duration in seconds (e.g. 60 = 1 min, 3600 = 1 hour, etc.)
                     But for Advanced Trade, we'll map these to the required string enums.
        """
        self.product_ids = product_ids or ["BTC-USD"]
        self.granularity = granularity

        # Create a Coinbase REST client using your Advanced Trade API Key + Secret
        self.client = RESTClient(
            api_key=COINBASE_API_KEY,
            api_secret=COINBASE_API_SECRET
        )

    def fetch_historical_data(self, product_id, start, end):
    # Convert start/end to datetime objects
        if isinstance(start, str):
            start_dt = pd.to_datetime(start, utc=True)
        else:
            start_dt = start

        if isinstance(end, str):
            end_dt = pd.to_datetime(end, utc=True)
        else:
            end_dt = end

    # Calculate maximum allowed time window per API call
        max_candles = 350
        timeframe_seconds = self.granularity
        max_window = pd.Timedelta(seconds=timeframe_seconds * max_candles)

    # Split the request into chunks
        all_data = []
        current_start = start_dt

        while current_start < end_dt:
            current_end = min(current_start + max_window, end_dt)
        
        # Convert to Unix timestamps
            start_unix = int(current_start.timestamp())
            end_unix = int(current_end.timestamp())

        # API call
            path = f"/api/v3/brokerage/products/{product_id}/candles"
            params = {
                "start": start_unix,
                "end": end_unix,
                "granularity": self._get_granularity_str()  # Add helper method
            }

            resp = self.client.get(path, params=params)
            chunk_data = resp.get("candles", [])

            if isinstance(chunk_data, list):
                all_data.extend(chunk_data)

            current_start = current_end  # Move to next chunk

        # Process combined data
        if not all_data:
            return pd.DataFrame()

        df = pd.DataFrame(all_data, columns=["time", "low", "high", "open", "close", "volume"])
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df.sort_values("time", inplace=True)
        df.drop_duplicates(subset=["time"], inplace=True)
        return df

    def _get_granularity_str(self):
    # Map numeric granularity to Coinbase's string enums
        granularity_map = {
            60: "ONE_MINUTE",
            300: "FIVE_MINUTE",
            900: "FIFTEEN_MINUTE",
            1800: "THIRTY_MINUTE",
            3600: "ONE_HOUR",
            7200: "TWO_HOUR",
            21600: "SIX_HOUR",
            86400: "ONE_DAY"
        }
        return granularity_map.get(self.granularity, "ONE_HOUR")

        path = f"/api/v3/brokerage/products/{product_id}/candles"
        params = {
            "start": start_unix,
            "end": end_unix,
            "granularity": granularity_str
        }

        resp = self.client.get(path, params=params)
        data = resp.to_dict()

        if not isinstance(data, list):
            print(f"Warning: unexpected data format for {product_id} candles: {data}")
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=["time", "low", "high", "open", "close", "volume"])
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df.sort_values("time", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

        # Convert your numeric self.granularity to the required string
        granularity_str = granularity_map.get(self.granularity, "ONE_HOUR")

        path = f"/api/v3/brokerage/products/{product_id}/candles"
        params = {
            "start": start,
            "end": end,
            "granularity": granularity_str
        }

        resp = self.client.get(path, params=params)
        data = resp.to_dict()

        if not isinstance(data, list):
            print(f"Warning: unexpected data format for {product_id} candles: {data}")
            return pd.DataFrame()

        # Each candle array is [time, low, high, open, close, volume]
        df = pd.DataFrame(data, columns=["time", "low", "high", "open", "close", "volume"])
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df.sort_values("time", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def build_multiasset_dataset(self, start, end):
        """
        Fetch data for each product_id in self.product_ids,
        add technical indicators, then merge into a single dataset.
        Each row could contain columns like:
            time, BTC-USD_close, BTC-USD_rsi, ETH-USD_close, ETH-USD_rsi, ...
        """
        final_df = None
        for pid in self.product_ids:
            df = self.fetch_historical_data(pid, start, end)
            df = self.add_technical_indicators(df, pid)
            if df.empty:
                continue
            # rename columns to avoid overlap
            rename_dict = {}
            for col in df.columns:
                if col not in ("time"):
                    rename_dict[col] = f"{pid}_{col}"
            df.rename(columns=rename_dict, inplace=True)

            if final_df is None:
                final_df = df
            else:
                # merge on 'time' using asof merge
                final_df = pd.merge_asof(final_df, df, on="time", direction="forward")

        if final_df is not None:
            final_df.dropna(inplace=True)
        return final_df

    def add_technical_indicators(self, df, prefix=""):
        if df.empty:
            return df
        df.sort_values("time", inplace=True)
        df.reset_index(drop=True, inplace=True)

        df["ma_50"] = df["close"].rolling(window=50).mean()
        df["ma_200"] = df["close"].rolling(window=200).mean()

        # Simple RSI
        delta = df["close"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=14).mean()
        avg_loss = pd.Series(loss).rolling(window=14).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        df["rsi"] = 100 - (100 / (1 + rs))

        df.fillna(method="ffill", inplace=True)
        df.fillna(0, inplace=True)

        return df

    def get_latest_ticker(self, product_id):
        """
        Fetch the latest price for a product from Advanced Trade.
        """
        path = f"/api/v3/brokerage/products/{product_id}/ticker"
        resp = self.client.get(path)
        data = resp.to_dict()
        if "price" in data:
            return float(data["price"])
        return None
