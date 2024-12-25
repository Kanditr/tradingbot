import logging
from openai import OpenAI


class SentimentAnalyzer:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI()

    def analyze(self, news):
        logging.info(f'Performing sentiment analysis for market data')

        prompt = (
            f"{news}\n\n"
            "Based on the above company news and your knowledge about the company, "
            "provide a single sentiment score between -100 and 100. Do not provide any other information, "
            "only return the number."
        )
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert financial analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            sentiment_score = float(completion.choices[0].message.content)
            logging.info(f'Sentiment score: {sentiment_score}')
            return sentiment_score
        except Exception as e:
            logging.error(f'Error during sentiment analysis: {e}', exec_info=True)
            return None
