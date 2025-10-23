# SPY Forecast System

AI-powered SPY stock forecasting system using technical analysis with 15+ indicators.

## Features

- **Forecasting Engine**: Uses yfinance and technical analysis library to generate predictions
- **Prediction Tracking**: Tracks forecast accuracy and evaluates historical performance
- **Web Dashboard**: Beautiful dark-themed dashboard to display forecasts and statistics
- **Automated Daily Updates**: Scheduled task runs daily to generate new forecasts

## Project Structure

```
spy-forecast/
├── scripts/
│   ├── spy_forecaster.py       # Main forecasting engine
│   └── prediction_tracker.py   # Prediction tracking and evaluation
├── data/
│   └── prediction_history.json # Historical predictions (generated)
├── forecast_latest.json         # Latest forecast (generated)
├── predictions_data.json        # Exported data for website (generated)
└── client/                      # Web interface files
    └── public/                  # Static assets for website
```

## Installation

```bash
# Install Python dependencies
pip3 install yfinance ta

# The system is ready to run!
```

## Usage

### Generate Daily Forecast

Run the complete daily forecasting workflow:

```bash
cd /home/ubuntu/spy-forecast

# 1. Generate forecast
python3 scripts/spy_forecaster.py

# 2. Update prediction tracking
python3 scripts/prediction_tracker.py --add --evaluate --export

# 3. Copy data to website
cp forecast_latest.json predictions_data.json client/public/
```

### Individual Commands

**Generate forecast only:**
```bash
python3 scripts/spy_forecaster.py
```

**Add prediction to history:**
```bash
python3 scripts/prediction_tracker.py --add
```

**Evaluate past predictions:**
```bash
python3 scripts/prediction_tracker.py --evaluate
```

**Export data for website:**
```bash
python3 scripts/prediction_tracker.py --export
```

## How It Works

### Forecasting Engine

The forecasting engine analyzes SPY using multiple categories of technical indicators:

**Trend Indicators:**
- Simple Moving Averages (SMA 20, 50)
- Exponential Moving Averages (EMA 12, 26)
- MACD (Moving Average Convergence Divergence)
- ADX (Average Directional Index)

**Momentum Indicators:**
- RSI (Relative Strength Index)
- Stochastic Oscillator
- Rate of Change (ROC)
- Williams %R

**Volatility Indicators:**
- Bollinger Bands
- Average True Range (ATR)

**Volume Indicators:**
- On-Balance Volume (OBV)
- Money Flow Index (MFI)
- Volume Moving Average

### Prediction System

1. Each indicator generates signals (positive for bullish, negative for bearish)
2. Signals are combined across categories (trend, momentum, volatility, volume)
3. Overall direction is determined: UP, DOWN, or NEUTRAL
4. Confidence score is calculated based on signal strength
5. Predictions are tracked and evaluated after 24 hours

## Scheduled Task

The system runs automatically via a scheduled task. The task:
1. Pulls latest code from GitHub
2. Runs the forecasting engine
3. Updates prediction tracking
4. Copies data files to the website
5. Website automatically displays updated forecasts

## Web Dashboard

The web interface displays:
- Current forecast with confidence score
- Signal breakdown by category
- Technical indicator values
- Historical accuracy statistics
- Recent prediction performance

Access the dashboard at: https://spy-forecast-web.manus.space (or your custom domain)

## Notes

- Forecasts are for informational purposes only
- Not financial advice
- Past performance does not guarantee future results
- Use at your own risk

## License

MIT

