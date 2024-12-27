import logging
from openai import OpenAI
import pandas as pd
from typing import Dict
import numpy as np
import matplotlib.pyplot as plt


# class TechnicalAnalyzer:
#     def __init__(self, config):
#         self.config = config

#     def analyze(self, processed_ticker_data):
#         logging.info(f'Performing technical analysis for market data')
#         logging.info(f'Market data: {processed_ticker_data}')
#         # Placeholder for actual technical analysis logic
#         # This could involve calculating various technical indicators like moving averages, RSI, MACD, etc.
#         return 80  # Example mock score

class SMATechnicalAnalyzer:
    def __init__(self, df: pd.DataFrame, trend_window: int = 5, sma_windows: list = [10, 50]):
        self.df = df.copy()
        self.trend_window = trend_window
        self.sma_windows = sma_windows
        self.scores = {}

    def calculate_sma(self):
        """
        Calculate SMA for specified window sizes and add them as new columns.
        """
        try:
            for window in self.sma_windows:
                self.df[f'SMA{window}'] = self.df['close'].rolling(window=window, min_periods=1).mean()
            logging.info("SMA columns added to DataFrame.")
        except Exception as e:
            logging.error(f"Error calculating SMA: {e}")

    def calculate_indicators(self):
        try:
            # Calculate SMA Strength Percentage
            self.df['SMA_Strength_Percent'] = ((self.df['SMA10'] - self.df['SMA50']) / self.df['SMA50']) * 100

            # Calculate Moving Average of SMA Strength
            self.df['SMA_Strength_MA5'] = self.df['SMA_Strength_Percent'].rolling(
                window=self.trend_window, min_periods=1).mean()

            # Calculate Slope of SMA Strength over the window
            self.df['SMA_Strength_Slope'] = self.df['SMA_Strength_Percent'].rolling(
                window=self.trend_window, min_periods=1).apply(self.calculate_slope, raw=False)

            logging.info("SMA indicators calculated successfully.")
            logging.info(self.df.tail())
        except Exception as e:
            logging.error(f"Error calculating SMA indicators: {e}")

    def calculate_slope(self, series):
        if series.isnull().any() or len(series) < 2:
            return np.nan
        x = np.arange(len(series))
        y = series.values
        slope, _ = np.polyfit(x, y, 1)
        return slope

    def assign_sma_score(self, row):
        """
        Assign a score based on SMA strength and trend.
        :param row: Pandas Series (row)
        :return: Score (int)
        """
        strength = row['SMA_Strength_Percent']
        slope = row['SMA_Strength_Slope']

        # Define slope thresholds
        slope_threshold_up = 0.5  # % per day
        slope_threshold_down = -0.5  # % per day

        # Determine trend direction
        if pd.isna(slope):
            trend = 'Stable'
        elif slope > slope_threshold_up:
            trend = 'Increasing'
        elif slope < slope_threshold_down:
            trend = 'Decreasing'
        else:
            trend = 'Stable'

        # Assign score based on strength and trend
        if strength > 25:
            if trend == 'Increasing':
                return 10
            elif trend == 'Stable':
                return 8
            elif trend == 'Decreasing':
                return 5
        elif 15 < strength <= 25:
            if trend == 'Increasing':
                return 7
            elif trend == 'Stable':
                return 5
            elif trend == 'Decreasing':
                return 2
        elif 5 < strength <= 15:
            if trend == 'Increasing':
                return 4
            elif trend == 'Stable':
                return 2
            elif trend == 'Decreasing':
                return 0
        elif -5 < strength <= 5:
            if trend in ['Increasing', 'Stable']:
                return -1
            elif trend == 'Decreasing':
                return -2
        elif strength <= -5:
            if trend == 'Increasing':
                return -4
            elif trend == 'Stable':
                return -5
            elif trend == 'Decreasing':
                return -7
        else:
            return 0  # Neutral

    def score_sma_crossover_strength(self):
        """
        Apply the scoring function to each row.
        """
        try:
            self.df['SMA_Score'] = self.df.apply(self.assign_sma_score, axis=1)
            latest_sma_score = self.df['SMA_Score'].iloc[-1]
            self.scores['SMA_Score'] = latest_sma_score
            logging.info(f"SMA Crossover Strength Score: {latest_sma_score}")
        except Exception as e:
            logging.error(f"Error scoring SMA crossover strength: {e}")

    # def calculate_final_score(self, weights: Dict[str, float] = None):
    #     """
    #     Calculate the final technical score based solely on SMA_Score.
    #     :param weights: Dictionary with weights for each indicator.
    #     :return: Final Technical Score
    #     """
    #     try:
    #         if weights is None:
    #             weights = {
    #                 'SMA_Score': 1.0  # 100% weight since it's the only indicator
    #             }

    #         final_score = self.df['SMA_Score'] * weights['SMA_Score']
    #         self.df['Final_Technical_Score'] = final_score
    #         self.scores['Final_Technical_Score'] = final_score.iloc[-1]
    #         logging.info(f"Final Technical Score: {final_score.iloc[-1]}")
    #         return self.scores
    #     except Exception as e:
    #         logging.error(f"Error calculating final score: {e}")
    #         return 0

    def plot_sma(self):
        """
        Plot Close Price along with SMA indicators.
        """
        try:
            plt.figure(figsize=(12, 6))
            plt.plot(self.df['timestamp'], self.df['close'], label='Close Price', color='blue')
            for window in self.sma_windows:
                plt.plot(self.df['timestamp'], self.df[f'SMA{window}'], label=f'SMA{window}')
            plt.title('Close Price and SMA Indicators')
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.legend()
            plt.show()
        except Exception as e:
            logging.error(f"Error plotting SMA: {e}")

    def run_analysis(self):
        """
        Execute the complete SMA technical analysis.
        :return: Dictionary of scores
        """
        self.calculate_sma()
        self.calculate_indicators()
        self.score_sma_crossover_strength()
        # self.plot_sma()
        # final_score = self.calculate_final_score()
        return self.scores


class TechnicalAnalyzer:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI()

    def analyze(self, processed_ticker_data, sma_10_data, sma_50_data, symbol):
        logging.info(f'Performing technical analysis for market data')

        prompt = (
            f"price history - {processed_ticker_data}\n\n"
            f"sma10 - {sma_10_data}\n\n"
            f"sma50 - {sma_50_data}\n\n"
            f"Based on the above price history data and data of SMA indicator and your knowledge about the company {
                symbol}, "
            "provide a single technical analysis score between -100 and 100. Do not provide any other information, "
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
            technical_score = float(completion.choices[0].message.content)
            logging.info(f'Technical score: {technical_score}')
            return technical_score
        except Exception as e:
            logging.error(f'Error during technical analysis: {e}', exec_info=True)
            return None
