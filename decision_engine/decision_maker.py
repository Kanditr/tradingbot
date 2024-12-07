import logging


class DecisionMaker:
    def __init__(self, config, risk_manager, portfolio_manager):
        self.config = config
        self.risk_manager = risk_manager
        self.portfolio_manager = portfolio_manager
        self.sentiment_weight = config.get('sentiment_weight', 0.5)
        self.technical_weight = config.get('technical_weight', 0.5)
        self.buy_threshold = config.get('buy_threshold', 20)
        self.sell_threshold = config.get('sell_threshold', -20)

    def make_decision(self, sentiment_score, technical_score, current_holdings):
        combined_score = (
            self.sentiment_weight * sentiment_score +
            self.technical_weight * technical_score
        )

        decision = []
        if combined_score >= self.buy_threshold:
            decision.append({'symbol': 'AAPL', 'quantity': 10, 'order_type': 'buy'})
        elif combined_score <= self.sell_threshold:
            decision.append({'symbol': 'AAPL', 'quantity': 10, 'order_type': 'sell'})
        else:
            decision.append({'symbol': 'AAPL', 'quantity': 0, 'order_type': 'hold'})

        logging.info(f'Decision: {decision}')
        return decision
