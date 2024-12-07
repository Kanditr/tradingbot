import logging


class PortfolioManager:
    def __init__(self, config, account_manager):
        self.config = config
        self.account_manager = account_manager

    def rebalance_portfolio(self, decision):
        """
        Rebalance the portfolio based on the trading decision.
        """
        for action in decision:
            symbol = action['symbol']
            quantity = action['quantity']
            order_type = action['order_type']
            self.account_manager.place_order(symbol, quantity, order_type)
        logging.info(f"Rebalanced portfolio based on decision: {decision}")

    def get_holdings(self):
        """
        Retrieve current holdings and balance from account manager.
        """
        return self.account_manager.get_holdings()
