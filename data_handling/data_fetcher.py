from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
import datetime
import logging
import pandas as pd
import psycopg2
from psycopg2 import sql
import traceback
import requests
from typing import Dict, Any, Optional


class DataFetcher:
    def __init__(self, config):
        self.config = config
        self.client = StockHistoricalDataClient(
            api_key=config['alpaca_api_key'],
            secret_key=config['alpaca_api_secret']
        )
        self.crypto_client = CryptoHistoricalDataClient(
            api_key=config['alpaca_api_key'],
            secret_key=config['alpaca_api_secret']
        )
        self.database_url = config['database_url']
        self.create_connection()
        self.base_url = "https://api.polygon.io"
        self.api_key = config['polygon_api_key']

    def create_connection(self):
        """ Create a database connection to the PostgreSQL database """
        try:
            self.connection = psycopg2.connect(self.database_url)
            logging.info('Connected to the PostgreSQL database')
        except psycopg2.Error as e:
            logging.error(f'Error connecting to the PostgreSQL database: {e}')
            self.connection = None

    def get_latest_timestamp(self, symbol, asset_type):
        """ Get the latest timestamp for the given symbol and asset type from the database """
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT MAX(timestamp) FROM ticker_data WHERE symbol = %s AND asset_type = %s
                    """, (symbol, asset_type))
                    result = cursor.fetchone()
                    logging.info(f"Latest timestamp for {symbol}: {result[0]}")
                    return result[0] if result[0] else None
            except psycopg2.Error as e:
                tb = traceback.extract_tb(e.__traceback__)
                filename, line, func, text = tb[-1]
                logging.error(f"Error fetching latest timestamp in {filename} at line {line}: {e}")
                return None
        return None

    def fetch_ticker_data(self, symbol, asset_type, start_date, end_date):
        """
        Fetch data for the given symbol and asset type using Alpaca API or database.

        Parameters:
        symbol (str): The ticker symbol of the asset.
        asset_type (str): The type of the asset (e.g., 'stock').
        start_date (datetime): The start date of the required data range.
        end_date (datetime): The end date of the required data range.
        """
        latest_timestamp = self.get_latest_timestamp(symbol, asset_type)
        db_data = []
        api_data = []

        if latest_timestamp and latest_timestamp >= start_date:
            # Fetch data from the database for the available range
            db_data = self.fetch_data_from_db(symbol, asset_type, start_date, min(latest_timestamp, end_date))
            logging.info(f"Fetched {len(db_data)} records from the database")
            logging.info(db_data)
            # If the latest timestamp in the database is less than the end date, fetch the remaining data from the API
            if latest_timestamp < end_date:
                api_data = self.fetch_data_from_api(
                    symbol, asset_type, latest_timestamp + datetime.timedelta(days=1), end_date)
                logging.info(f"Fetched {len(api_data)} records from the API")
        else:
            # Fetch all data from the API if no data is available in the database
            api_data = self.fetch_data_from_api(symbol, asset_type, start_date, end_date)
            logging.info(f"Fetched {len(api_data)} records from the API")
        if not api_data.empty:
            self.store_data_in_db(api_data, symbol, asset_type)

        # Combine data from the database and API
        combined_data = db_data + api_data.to_dict('records') if not api_data.empty else db_data
        return combined_data

    def fetch_data_from_db(self, symbol, asset_type, start_date, end_date):
        """ Fetch data from the database """
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM ticker_data WHERE symbol = %s AND asset_type = %s AND timestamp BETWEEN %s AND %s
                    """, (symbol, asset_type, start_date, end_date))
                    result = cursor.fetchall()
                    return result
            except psycopg2.Error as e:
                logging.error(f"Error fetching data from database: {e}")
                return []
        return []

    def fetch_data_from_api(self, symbol, asset_type, start_date, end_date):
        """ Fetch data from the Alpaca API """
        if asset_type == 'stock':
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start_date,
                end=end_date
            )
            bars = self.client.get_stock_bars(request_params).df
            # bars.reset_index(inplace=True)
        elif asset_type == 'crypto':
            request_params = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start_date,
                end=end_date
            )
            bars = self.crypto_client.get_crypto_bars(request_params).df
        else:
            raise ValueError("Unsupported asset type")

        bars.reset_index(inplace=True)
        return bars

    def store_data_in_db(self, data, symbol, asset_type):
        """ Store fetched data in the database """
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    insert_query = sql.SQL("""
                        INSERT INTO ticker_data (symbol, asset_type, timestamp, open, high, low, close, volume, trade_count, vwap)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, asset_type, timestamp) DO NOTHING
                    """)
                    cursor.executemany(insert_query, [
                        (symbol, asset_type, row['timestamp'].strftime('%Y-%m-%d'), row['open'], row['high'],
                         row['low'], row['close'], row['volume'], row['trade_count'], row['vwap'])
                        for index, row in data.iterrows()
                    ])
                    self.connection.commit()
                    logging.info("Ticker data stored in the database.")
            except psycopg2.Error as e:
                logging.error(f"Error storing ticker data: {e}")

    def fetch_sentiment_data(self, symbol):
        """
        Fetch historical market sentiment data (e.g., news) for the given symbol.
        """
        # Placeholder for actual data fetching logic
        return [{'news': 'Positive news article', 'timestamp': '2021-01-01'}, {'news': 'Negative news article', 'timestamp': '2021-01-02'}]

    def fetch_technical_analysis_data(self, symbol: str, indicator: str, window: str) -> Dict[str, Any]:

        url = f"{self.base_url}/v1/indicators/{indicator}/{symbol}"
        params = {
            "timespan": "day",
            "adjusted": "true",
            "window": window,
            "series_type": "close",
            "order": "desc",
            "limit": "10",
            "apiKey": self.api_key
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logging.info(f"Technical indicator data for {symbol} ({indicator}): {data}")
            return data
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching technical analysis data: {e}")
            return None

    def fetch_close_prices(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Fetch the close prices for a given symbol between start_date and end_date.

        :param symbol: The ticker symbol (e.g., 'AAPL')
        :param start_date: The start date in 'YYYY-MM-DD' format
        :param end_date: The end date in 'YYYY-MM-DD' format
        :return: A pandas DataFrame with 'timestamp' and 'close' columns or None if an error occurs
        """
        if not self.connection:
            logging.error("Database connection is not established.")
            return None

        try:
            query = """
                SELECT timestamp, close 
                FROM ticker_data 
                WHERE symbol = %s 
                AND timestamp BETWEEN %s AND %s 
                ORDER BY timestamp ASC
            """
            df = pd.read_sql_query(query, self.connection, params=(symbol, start_date, end_date))
            logging.info(f"Fetched {len(df)} close price records for {symbol} from {start_date} to {end_date}.")
            return df
        except Exception as e:
            logging.error(f"Error fetching close prices: {e}")
            logging.debug(traceback.format_exc())
            return None
