import logging
import psycopg2
from psycopg2 import sql, Error


class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.database_url = config['database_url']
        self.create_connection()

    def create_connection(self):
        """
        Create a database connection to the PostgreSQL database
        """
        try:
            self.connection = psycopg2.connect(self.database_url)
            logging.info('Connected to the PostgreSQL database')
        except Error as e:
            logging.error(f'Error connecting to the PostgreSQL database: {e}')
            self.connection = None

    def create_table(self):
        """
        Create a table in the PostgreSQL database
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    sql.SQL("""
                    CREATE TABLE IF NOT EXISTS ticker_data (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(10) NOT NULL,
                        asset_type VARCHAR(10) NOT NULL,
                        timestamp DATE NOT NULL,
                        open DECIMAL NOT NULL,
                        high DECIMAL NOT NULL,
                        low DECIMAL NOT NULL,
                        close DECIMAL NOT NULL,
                        volume DECIMAL NOT NULL,
                        trade_count INTEGER NOT NULL,
                        vwap DECIMAL NOT NULL,
                        UNIQUE (symbol, asset_type, timestamp)
                    )
                    """)
                )
                self.connection.commit()
                logging.info('Table is exist or created successfully')
        except Error as e:
            logging.error(f'Error creating table: {e}')

    def process_ticker_data(self, bars, symbol, asset_type):
        """
        Process ticker data to prepare it for analysis and store it in the database.
        """
        data = [{
            "symbol": symbol,
            "asset_type": asset_type,
            "timestamp": row['timestamp'].strftime('%Y-%m-%d'),
            "open": row['open'],
            "high": row['high'],
            "low": row['low'],
            "close": row['close'],
            "volume": row['volume'],
            "trade_count": row['trade_count'],
            "vwap": row['vwap']
        } for index, row in bars.iterrows()]

        logging.info(f'Processed ticker data: {data}')
        # self.store_ticker_data(data)
        return data

    def store_ticker_data(self, data):
        """ Store processed ticker data into the database """
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    insert_query = sql.SQL("""
                        INSERT INTO ticker_data (symbol, asset_type, timestamp, open, high, low, close, volume, trade_count, vwap)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """)
                    cursor.executemany(insert_query, [
                        (d['symbol'], d['asset_type'], d['timestamp'], d['open'], d['high'],
                         d['low'], d['close'], d['volume'], d['trade_count'], d['vwap'])
                        for d in data
                    ])
                    self.connection.commit()
                    logging.info("Ticker data stored in the database.")
            except Error as e:
                logging.error(f"Error storing ticker data: {e}")

    def process_sentiment_data(self, sentiment_data):
        """
        Process sentiment data to prepare it for analysis.
        """
        # Placeholder for actual data processing logic
        return sentiment_data
