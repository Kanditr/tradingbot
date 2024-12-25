from datetime import date
import json
import logging
from typing import List, Dict
from openai import OpenAI
import os


class CompanyNewsService:
    def __init__(self, config: Dict):
        self.config = config
        self.api_key = self.config['pplx_api_key']
        self.client = OpenAI(api_key=self.api_key,
                             base_url="https://api.perplexity.ai")

    def get_company_news(self, current_date: date, company_ticker: str) -> dict:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an artificial intelligence financial assistant. "
                    "You need to provide list of news that might impact the stock price movement of a company. "
                    "Return the response in JSON format with the following structure: "
                    "{ 'date': 'YYYY-MM-DD', 'company': 'Company Name', 'news': [ { 'headline': 'News Headline', 'impact': 'Positive/Negative/Neutral', 'details': 'Detailed description of the news' } ] }."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Provide news that might impact the stock price movement of {
                        company_ticker} published on {current_date.strftime('%d %B %Y')}."
                ),
            },
        ]

        completion = self.client.chat.completions.create(
            model="llama-3.1-sonar-small-128k-online",
            messages=messages,
        )
        response = completion.choices[0].message.content

        logging.info(f"Company news response: {response}")

        # Parse the response to ensure it's in JSON format
        try:
            response_json = json.loads(response)
            return response_json
        except json.JSONDecodeError:
            print("Failed to parse response as JSON")
            return {"error": "Failed to parse response as JSON", "response": response}
