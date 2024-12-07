import logging
from openai import OpenAI
from sentiment_analysis.data_models.macro_economic import EconomicIndicators


class SentimentAnalyzer:
    def __init__(self, config, economic_indicators: EconomicIndicators):
        self.config = config
        self.client = OpenAI()
        self.economic_indicators = economic_indicators

    def analyze(self):
        logging.info(f'Performing sentiment analysis for market data')
        economic_context = (
            f"GDP Growth Rate: {self.economic_indicators.gdp_growth_rate}%, "
            f"Unemployment Rate: {self.economic_indicators.unemployment_rate}%, "
            f"Inflation Rate: {self.economic_indicators.inflation_rate}%, "
            f"Consumer Confidence Index: {self.economic_indicators.consumer_confidence_index}, "
            f"Manufacturing Index: {self.economic_indicators.manufacturing_index}\n"
            f"Interest Rates:\n"
        )

        for rate in self.economic_indicators.interest_rates.interest_rates:
            economic_context += f"  - {rate.country}: {rate.central_bank_interest_rate}%\n"

        economic_context += "Exchange Rates:\n"
        for rate in self.economic_indicators.exchange_rates.exchange_rates:
            economic_context += f"  - {rate.currency_pair}: {rate.exchange_rate}\n"

        economic_context += "Commodity Prices:\n"
        for commodity in self.economic_indicators.commodity_prices.commodities:
            economic_context += f"  - {commodity.commodity_name}: ${commodity.commodity_price}\n"

        prompt = (
            f"{economic_context}\n\n"
            "Based on the above macroeconomic indicators and your knowledge about Apple company, "
            "provide a single sentiment score between -100 and 100. Do not provide any other information, "
            "only return the number."
        )
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            sentiment_score = float(completion.choices[0].message.content)
            logging.info(f'Sentiment score: {sentiment_score}')
            return sentiment_score
        except Exception as e:
            logging.error(f'Error during sentiment analysis: {e}', exec_info=True)
            return None
