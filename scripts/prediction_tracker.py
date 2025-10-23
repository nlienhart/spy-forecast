#!/usr/bin/env python3
"""
Prediction Tracker
Tracks forecast accuracy and maintains historical prediction data
"""

import json
import argparse
from datetime import datetime
import yfinance as yf
import os


class PredictionTracker:
    def __init__(self):
        self.history_file = 'data/prediction_history.json'
        self.export_file = 'predictions_data.json'
        self.forecast_file = 'forecast_latest.json'
        
    def load_history(self):
        """Load prediction history from file"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {'predictions': [], 'statistics': {}}
    
    def save_history(self, history):
        """Save prediction history to file"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def load_forecast(self):
        """Load latest forecast"""
        if not os.path.exists(self.forecast_file):
            raise FileNotFoundError(f"Forecast file not found: {self.forecast_file}")
        
        with open(self.forecast_file, 'r') as f:
            return json.load(f)
    
    def add_prediction(self):
        """Add current forecast to prediction history"""
        print("Adding prediction to history...")
        
        forecast = self.load_forecast()
        history = self.load_history()
        
        # Create prediction record
        prediction = {
            'id': len(history['predictions']) + 1,
            'timestamp': forecast['timestamp'],
            'date': forecast['date'],
            'ticker': forecast['ticker'],
            'price_at_prediction': forecast['current_price'],
            'predicted_direction': forecast['prediction']['direction'],
            'confidence': forecast['prediction']['confidence'],
            'signal_strength': forecast['prediction']['signal_strength'],
            'signals': forecast['signals'],
            'evaluated': False,
            'actual_direction': None,
            'actual_change_pct': None,
            'correct': None
        }
        
        history['predictions'].append(prediction)
        self.save_history(history)
        
        print(f"  Added prediction #{prediction['id']}")
        print(f"  Direction: {prediction['predicted_direction']}")
        print(f"  Confidence: {prediction['confidence']}%")
        
        return history
    
    def evaluate_predictions(self):
        """Evaluate unevaluated predictions"""
        print("\nEvaluating predictions...")
        
        history = self.load_history()
        evaluated_count = 0
        
        for pred in history['predictions']:
            if pred['evaluated']:
                continue
            
            # Check if enough time has passed (at least 1 day)
            pred_date = datetime.fromisoformat(pred['timestamp'])
            hours_passed = (datetime.now() - pred_date).total_seconds() / 3600
            
            if hours_passed < 24:
                continue  # Not enough time to evaluate
            
            # Fetch actual price movement
            try:
                ticker = yf.Ticker(pred['ticker'])
                hist = ticker.history(start=pred['date'], period='2d')
                
                if len(hist) < 2:
                    continue  # Not enough data yet
                
                price_start = pred['price_at_prediction']
                price_end = hist['Close'].iloc[-1]
                actual_change_pct = ((price_end - price_start) / price_start) * 100
                
                # Determine actual direction
                if actual_change_pct > 0.1:
                    actual_direction = "UP"
                elif actual_change_pct < -0.1:
                    actual_direction = "DOWN"
                else:
                    actual_direction = "NEUTRAL"
                
                # Check if prediction was correct
                correct = (pred['predicted_direction'] == actual_direction)
                
                # Update prediction
                pred['evaluated'] = True
                pred['actual_direction'] = actual_direction
                pred['actual_change_pct'] = round(actual_change_pct, 2)
                pred['correct'] = correct
                pred['price_after_24h'] = round(float(price_end), 2)
                
                evaluated_count += 1
                
                print(f"  Evaluated prediction #{pred['id']}: {'✓ CORRECT' if correct else '✗ INCORRECT'}")
                print(f"    Predicted: {pred['predicted_direction']}, Actual: {actual_direction} ({actual_change_pct:.2f}%)")
                
            except Exception as e:
                print(f"  Error evaluating prediction #{pred['id']}: {e}")
                continue
        
        if evaluated_count > 0:
            self.save_history(history)
            print(f"\nEvaluated {evaluated_count} prediction(s)")
        else:
            print("  No predictions ready for evaluation")
        
        return history
    
    def calculate_statistics(self, history):
        """Calculate prediction accuracy statistics"""
        evaluated = [p for p in history['predictions'] if p['evaluated']]
        
        if not evaluated:
            return {
                'total_predictions': len(history['predictions']),
                'evaluated_predictions': 0,
                'accuracy': 0,
                'correct': 0,
                'incorrect': 0
            }
        
        correct = sum(1 for p in evaluated if p['correct'])
        incorrect = len(evaluated) - correct
        accuracy = (correct / len(evaluated)) * 100
        
        # Calculate by direction
        up_preds = [p for p in evaluated if p['predicted_direction'] == 'UP']
        down_preds = [p for p in evaluated if p['predicted_direction'] == 'DOWN']
        neutral_preds = [p for p in evaluated if p['predicted_direction'] == 'NEUTRAL']
        
        stats = {
            'total_predictions': len(history['predictions']),
            'evaluated_predictions': len(evaluated),
            'accuracy': round(accuracy, 2),
            'correct': correct,
            'incorrect': incorrect,
            'by_direction': {
                'UP': {
                    'total': len(up_preds),
                    'correct': sum(1 for p in up_preds if p['correct']),
                    'accuracy': round((sum(1 for p in up_preds if p['correct']) / len(up_preds) * 100) if up_preds else 0, 2)
                },
                'DOWN': {
                    'total': len(down_preds),
                    'correct': sum(1 for p in down_preds if p['correct']),
                    'accuracy': round((sum(1 for p in down_preds if p['correct']) / len(down_preds) * 100) if down_preds else 0, 2)
                },
                'NEUTRAL': {
                    'total': len(neutral_preds),
                    'correct': sum(1 for p in neutral_preds if p['correct']),
                    'accuracy': round((sum(1 for p in neutral_preds if p['correct']) / len(neutral_preds) * 100) if neutral_preds else 0, 2)
                }
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return stats
    
    def export_data(self):
        """Export data for website display"""
        print("\nExporting data for website...")
        
        history = self.load_history()
        
        # Calculate statistics
        stats = self.calculate_statistics(history)
        history['statistics'] = stats
        self.save_history(history)
        
        # Create export data (recent predictions only)
        recent_predictions = history['predictions'][-30:]  # Last 30 predictions
        
        export_data = {
            'statistics': stats,
            'recent_predictions': recent_predictions,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"  Exported data to: {self.export_file}")
        print(f"  Total Predictions: {stats['total_predictions']}")
        print(f"  Evaluated: {stats['evaluated_predictions']}")
        print(f"  Accuracy: {stats['accuracy']}%")
        
        return export_data


def main():
    parser = argparse.ArgumentParser(description='Track and evaluate SPY predictions')
    parser.add_argument('--add', action='store_true', help='Add current forecast to history')
    parser.add_argument('--evaluate', action='store_true', help='Evaluate past predictions')
    parser.add_argument('--export', action='store_true', help='Export data for website')
    
    args = parser.parse_args()
    
    tracker = PredictionTracker()
    
    print("=" * 60)
    print("PREDICTION TRACKER")
    print("=" * 60)
    
    if args.add:
        tracker.add_prediction()
    
    if args.evaluate:
        tracker.evaluate_predictions()
    
    if args.export:
        tracker.export_data()
    
    if not any([args.add, args.evaluate, args.export]):
        print("No action specified. Use --add, --evaluate, or --export")
        parser.print_help()
    
    print("=" * 60)


if __name__ == "__main__":
    main()

