#!/usr/bin/env python3
"""
SPY Forecasting Engine
Uses technical analysis with 15+ indicators to generate directional predictions
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import ta
import warnings
warnings.filterwarnings('ignore')


class SPYForecaster:
    def __init__(self):
        self.ticker = "SPY"
        self.lookback_days = 100
        
    def fetch_data(self):
        """Fetch SPY historical data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.lookback_days)
        
        print(f"Fetching {self.ticker} data from {start_date.date()} to {end_date.date()}...")
        df = yf.download(self.ticker, start=start_date, end=end_date, progress=False)
        
        if df.empty:
            raise ValueError("No data fetched from yfinance")
        
        # Flatten multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        return df
    
    def calculate_indicators(self, df):
        """Calculate technical indicators across multiple categories"""
        
        # Trend Indicators
        df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
        df['EMA_26'] = ta.trend.ema_indicator(df['Close'], window=26)
        df['MACD'] = ta.trend.macd(df['Close'])
        df['MACD_signal'] = ta.trend.macd_signal(df['Close'])
        df['ADX'] = ta.trend.adx(df['High'], df['Low'], df['Close'])
        
        # Momentum Indicators
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        df['Stoch'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])
        df['Stoch_signal'] = ta.momentum.stoch_signal(df['High'], df['Low'], df['Close'])
        df['ROC'] = ta.momentum.roc(df['Close'], window=12)
        df['Williams_R'] = ta.momentum.williams_r(df['High'], df['Low'], df['Close'])
        
        # Volatility Indicators
        bb = ta.volatility.BollingerBands(df['Close'])
        df['BB_upper'] = bb.bollinger_hband()
        df['BB_middle'] = bb.bollinger_mavg()
        df['BB_lower'] = bb.bollinger_lband()
        df['BB_width'] = bb.bollinger_wband()
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])
        
        # Volume Indicators
        df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
        df['MFI'] = ta.volume.money_flow_index(df['High'], df['Low'], df['Close'], df['Volume'])
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        
        return df
    
    def generate_signals(self, df):
        """Generate trading signals from indicators"""
        signals = {
            'trend': 0,
            'momentum': 0,
            'volatility': 0,
            'volume': 0
        }
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Trend signals
        if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
            signals['trend'] += 2
        elif latest['Close'] > latest['SMA_20']:
            signals['trend'] += 1
        elif latest['Close'] < latest['SMA_20'] < latest['SMA_50']:
            signals['trend'] -= 2
        elif latest['Close'] < latest['SMA_20']:
            signals['trend'] -= 1
            
        if latest['MACD'] > latest['MACD_signal']:
            signals['trend'] += 1
        else:
            signals['trend'] -= 1
            
        if latest['ADX'] > 25:
            # Strong trend
            if latest['Close'] > prev['Close']:
                signals['trend'] += 1
            else:
                signals['trend'] -= 1
        
        # Momentum signals
        if latest['RSI'] > 70:
            signals['momentum'] -= 2  # Overbought
        elif latest['RSI'] > 60:
            signals['momentum'] += 1
        elif latest['RSI'] < 30:
            signals['momentum'] += 2  # Oversold
        elif latest['RSI'] < 40:
            signals['momentum'] -= 1
        
        if latest['Stoch'] > latest['Stoch_signal'] and latest['Stoch'] < 80:
            signals['momentum'] += 1
        elif latest['Stoch'] < latest['Stoch_signal'] and latest['Stoch'] > 20:
            signals['momentum'] -= 1
            
        if latest['ROC'] > 0:
            signals['momentum'] += 1
        else:
            signals['momentum'] -= 1
        
        # Volatility signals
        if latest['Close'] > latest['BB_upper']:
            signals['volatility'] -= 1  # Overbought
        elif latest['Close'] < latest['BB_lower']:
            signals['volatility'] += 1  # Oversold
        elif latest['Close'] > latest['BB_middle']:
            signals['volatility'] += 1
        else:
            signals['volatility'] -= 1
            
        if latest['ATR'] > df['ATR'].rolling(20).mean().iloc[-1]:
            # High volatility - be cautious
            signals['volatility'] -= 1
        
        # Volume signals
        if latest['Volume'] > latest['Volume_SMA']:
            if latest['Close'] > prev['Close']:
                signals['volume'] += 2  # Strong buying
            else:
                signals['volume'] -= 2  # Strong selling
        
        if latest['MFI'] > 80:
            signals['volume'] -= 1  # Overbought
        elif latest['MFI'] < 20:
            signals['volume'] += 1  # Oversold
            
        obv_trend = df['OBV'].iloc[-5:].diff().mean()
        if obv_trend > 0:
            signals['volume'] += 1
        else:
            signals['volume'] -= 1
        
        return signals
    
    def calculate_confidence(self, signals):
        """Calculate confidence score from signals"""
        total_signal = sum(signals.values())
        max_possible = 20  # Approximate max signal strength
        
        confidence = abs(total_signal) / max_possible * 100
        confidence = min(confidence, 100)
        
        return round(confidence, 2)
    
    def generate_forecast(self):
        """Main forecasting function"""
        print("=" * 60)
        print("SPY FORECASTING ENGINE")
        print("=" * 60)
        
        # Fetch and prepare data
        df = self.fetch_data()
        df = self.calculate_indicators(df)
        
        # Generate signals
        signals = self.generate_signals(df)
        
        # Calculate overall direction
        total_signal = sum(signals.values())
        if total_signal > 0:
            direction = "UP"
        elif total_signal < 0:
            direction = "DOWN"
        else:
            direction = "NEUTRAL"
        
        # Calculate confidence
        confidence = self.calculate_confidence(signals)
        
        # Get current price info
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        price_change = latest['Close'] - prev['Close']
        price_change_pct = (price_change / prev['Close']) * 100
        
        # Create forecast output
        forecast = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'ticker': self.ticker,
            'current_price': round(float(latest['Close']), 2),
            'price_change': round(float(price_change), 2),
            'price_change_pct': round(float(price_change_pct), 2),
            'prediction': {
                'direction': direction,
                'confidence': confidence,
                'signal_strength': total_signal
            },
            'signals': signals,
            'indicators': {
                'RSI': round(float(latest['RSI']), 2),
                'MACD': round(float(latest['MACD']), 4),
                'ADX': round(float(latest['ADX']), 2),
                'Stochastic': round(float(latest['Stoch']), 2),
                'MFI': round(float(latest['MFI']), 2),
                'ATR': round(float(latest['ATR']), 2)
            }
        }
        
        # Save to file
        output_file = 'forecast_latest.json'
        with open(output_file, 'w') as f:
            json.dump(forecast, f, indent=2)
        
        print(f"\nForecast Generated:")
        print(f"  Current Price: ${forecast['current_price']}")
        print(f"  Change: ${forecast['price_change']} ({forecast['price_change_pct']}%)")
        print(f"  Prediction: {direction}")
        print(f"  Confidence: {confidence}%")
        print(f"  Signal Breakdown: {signals}")
        print(f"\nSaved to: {output_file}")
        print("=" * 60)
        
        return forecast


if __name__ == "__main__":
    forecaster = SPYForecaster()
    forecaster.generate_forecast()

