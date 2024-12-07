import argparse
import logging
import sys
import schedule
import time
import signal
import datetime

from config.settings import load_configurations
from utils.logger import initialize_logging
from data_handling.data_fetcher import DataFetcher
from data_handling.data_processor import DataProcessor
from sentiment_analysis.sentiment_analyzer import SentimentAnalyzer
from technical_analysis.technical_analyzer import TechnicalAnalyzer
from decision_engine.decision_maker import DecisionMaker
from data_handling.account_manager import AccountManager
from decision_engine.portfolio_manager import PortfolioManager
from decision_engine.risk_manager import RiskManager

from sentiment_analysis.services.macro_economic_service import get_economic_indicators


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
    economic_indicators = get_economic_indicators(current_date)

    sentiment_analyzer = SentimentAnalyzer(config, economic_indicators)

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

    # Perform technical analysis
    technical_signal = technical_analyzer.analyze(processed_ticker_data)
    logging.info(f'Technical signal: {technical_signal}')

    # Perform sentiment analysis
    sentiment_score = sentiment_analyzer.analyze()

    # Get current position
    account_info = portfolio_manager.get_holdings()
    current_holdings = account_info['holdings']
    balance = account_info['balance']

    logging.info(f'Current holdings: {current_holdings}')
    logging.info(f'Current balance: {balance}')

    # Make trading decision
    decision = decision_maker.make_decision(sentiment_score, technical_signal, current_holdings)

    logging.info(f'Trading decision: {decision}')

    # Execute trading decision
    portfolio_manager.rebalance_portfolio(decision)


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
