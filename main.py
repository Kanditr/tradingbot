import argparse
import logging
import sys
import pandas as pd
import schedule
import time
import signal
import datetime

from config.settings import load_configurations
from sentiment_analysis.services.company_news_service import CompanyNewsService
from utils.logger import initialize_logging
from data_handling.data_fetcher import DataFetcher
from data_handling.data_processor import DataProcessor
from sentiment_analysis.sentiment_analyzer import SentimentAnalyzer
from technical_analysis.technical_analyzer import TechnicalAnalyzer
from technical_analysis.technical_analyzer import SMATechnicalAnalyzer
from decision_engine.decision_maker import DecisionMaker
from data_handling.account_manager import AccountManager
from decision_engine.portfolio_manager import PortfolioManager
from decision_engine.risk_manager import RiskManager


def parse_input_arguments():
    parser = argparse.ArgumentParser(description='Algorithmic Trading Application')
    parser.add_argument('symbol', type=str, help='Trading symbol (e.g., AAPL for stocks, BTC for crypto)')
    parser.add_argument('asset_type', type=str, choices=['stock', 'crypto'], help='Type of asset (stock or crypto)')
    parser.add_argument('start_date', type=str, help='Start date for data retrieval (YYYY-MM-DD)')
    parser.add_argument('end_date', type=str, help='End date for data retrieval (YYYY-MM-DD)')
    args = parser.parse_args()
    return args.symbol, args.asset_type, args.start_date, args.end_date


def handle_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def job():
    try:
        main()
    except Exception as e:
        logging.error(f"Error during job execution: {e}", exc_info=True)
    finally:
        shutdown_procedure()


def shutdown_procedure():
    logging.info('Shutting down application...')
    # Add any cleanup code here


def signal_handler(sig, frame):
    logging.info('Received signal to stop. Shutting down...')
    shutdown_procedure()
    sys.exit(0)


def main():
    # Initialization
    sys.excepthook = handle_exceptions
    config = load_configurations()
    symbol, asset_type, start_date, end_date = parse_input_arguments()
    logging.info('Starting Algorithmic Trading Application')

    # Initialize components
    data_fetcher = DataFetcher(config)
    data_processor = DataProcessor(config)
    data_processor.create_table()
    technical_analyzer = TechnicalAnalyzer(config)

    # Initialize EconomicIndicators
    current_date = datetime.date.today()
    news_service = CompanyNewsService(config)
    # sentiment_analyzer = SentimentAnalyzer(config)

    risk_manager = RiskManager(config)
    account_manager = AccountManager(config)
    portfolio_manager = PortfolioManager(config, account_manager)
    decision_maker = DecisionMaker(config, risk_manager, portfolio_manager)

    # Convert start_date and end_date to datetime.date objects
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    # Retrieve market data
    combined_data = data_fetcher.fetch_ticker_data(symbol, asset_type, start_date, end_date)

    # Separate data retrieved from the database and new data fetched from the API
    db_data = [data for data in combined_data if 'source' in data and data['source'] == 'db']
    api_data = [data for data in combined_data if 'source' in data and data['source'] == 'api']

    # Process new data fetched from the API
    if api_data:
        processed_api_data = data_processor.process_ticker_data(api_data, symbol, asset_type)
        logging.info(f'Processed new ticker data: {processed_api_data}')

    # Combine processed API data with DB data for analysis
    processed_ticker_data = db_data + processed_api_data if api_data else db_data

    close_prices_df = data_fetcher.fetch_close_prices(symbol, start_date, end_date)

    # Ensure 'timestamp' is datetime and sort ascending
    close_prices_df['timestamp'] = pd.to_datetime(close_prices_df['timestamp'])
    df_merged = close_prices_df.sort_values('timestamp', ascending=True).reset_index(drop=True)

    # Initialize Technical Analyzer
    technical_analyzer = SMATechnicalAnalyzer(df=df_merged, trend_window=5, sma_windows=[10, 50])

    # Run Analysis
    technical_scores = technical_analyzer.run_analysis()

    # Perform technical analysis
    # sma10_data = data_fetcher.fetch_technical_analysis_data(symbol, 'sma', '10')
    # sma50_data = data_fetcher.fetch_technical_analysis_data(symbol, 'sma', '50')

    # sma10_data = {
    #     'results': {
    #         'underlying': {
    #             'url': 'https://api.polygon.io/v2/aggs/ticker/NVO/range/1/day/1063281600000/1734835774539?limit=57&sort=desc'
    #         },
    #         'values': [
    #             {'timestamp': 1734670800000, 'value': 105.79800000000003},
    #             {'timestamp': 1734584400000, 'value': 108.37500000000003},
    #             {'timestamp': 1734498000000, 'value': 108.91300000000001},
    #             {'timestamp': 1734411600000, 'value': 109.21400000000001},
    #             {'timestamp': 1734325200000, 'value': 109.33300000000001},
    #             {'timestamp': 1734066000000, 'value': 109.39500000000002},
    #             {'timestamp': 1733979600000, 'value': 109.38000000000002},
    #             {'timestamp': 1733893200000, 'value': 109.13200000000002},
    #             {'timestamp': 1733806800000, 'value': 108.57600000000002},
    #             {'timestamp': 1733720400000, 'value': 108.11300000000001}
    #         ]
    #     },
    #     'status': 'OK',
    #     'request_id': '843116985f555981f3a40045cd12f97f',
    #     'next_url': 'https://api.polygon.io/v1/indicators/sma/NVO?cursor=...'
    # }

    # sma50_data = {
    #     'results': {
    #         'underlying': {
    #             'url': 'https://api.polygon.io/v2/aggs/ticker/NVO/range/1/day/1063281600000/1734835774539?limit=57&sort=desc'
    #         },
    #         'values': [
    #             {'timestamp': 1734670800000, 'value': 100.12300000000002},
    #             {'timestamp': 1734584400000, 'value': 102.45600000000002},
    #             {'timestamp': 1734498000000, 'value': 104.78000000000002},
    #             {'timestamp': 1734411600000, 'value': 107.10000000000002},
    #             {'timestamp': 1734325200000, 'value': 109.43000000000002},
    #             {'timestamp': 1734066000000, 'value': 111.76000000000002},
    #             {'timestamp': 1733979600000, 'value': 114.09000000000002},
    #             {'timestamp': 1733893200000, 'value': 116.42000000000001},
    #             {'timestamp': 1733806800000, 'value': 118.75000000000001},
    #             {'timestamp': 1733720400000, 'value': 121.08000000000001}
    #         ]
    #     },
    #     'status': 'OK',
    #     'request_id': '843116985f555981f3a40045cd12f97f',
    #     'next_url': 'https://api.polygon.io/v1/indicators/sma/NVO?cursor=...'
    # }

    # sma10_df = data_processor.process_sma_data(sma10_data, 10)
    # sma50_df = data_processor.process_sma_data(sma50_data, 50)

    # merged_sma = data_processor.merge_sma_data(sma10_df, sma50_df)
    # sma_analyzer = SMATechnicalAnalyzer(df=merged_sma, trend_window=5)
    # sma_scores = sma_analyzer.run_analysis()

    # technical_signal = technical_analyzer.analyze(processed_ticker_data, sma_10_data, sma_50_data, symbol)

    # Perform sentiment analysis
    # news = news_service.get_company_news(current_date, symbol)
    # sentiment_score = sentiment_analyzer.analyze(news)

    # Get current position
    # account_info = portfolio_manager.get_holdings()
    # current_holdings = account_info['holdings']
    # balance = account_info['balance']

    # logging.info(f'Current holdings: {current_holdings}')
    # logging.info(f'Current balance: {balance}')

    # Make trading decision
    # decision = decision_maker.make_decision(sentiment_score, technical_signal, current_holdings)

    # logging.info(f'Trading decision: {decision}')

    # Execute trading decision
    # portfolio_manager.rebalance_portfolio(decision)


if __name__ == '__main__':
    initialize_logging()

    # Handle signals for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the job immediately before starting the schedule loop
    job()

    # Schedule the job
    # schedule.every().minute.do(job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Application interrupted by user. Exiting gracefully...")
        sys.exit(0)
    main()
