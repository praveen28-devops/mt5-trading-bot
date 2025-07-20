"""
LSTM Model for Forex Trend Prediction
This module trains and predicts currency price trends using LSTM
"""

import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple
from loguru import logger


class LSTMPredictor:
    """LSTM model for forex trend prediction"""
    def __init__(self, lookback_period: int = 60, prediction_horizon: int = 1):
        """
        Initialize the LSTM model
        
        Args:
            lookback_period: Number of time steps to look back for prediction
            prediction_horizon: Number of time steps to predict ahead
        """
        self.lookback_period = lookback_period
        self.prediction_horizon = prediction_horizon
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    def create_model(self, input_shape: Tuple[int, int]):
        """Create LSTM model architecture"""
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(units=1))
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        logger.info("LSTM model created")
        return model
    
    def prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Prepare data for LSTM model training and testing"""
        # Scale data
        scaled_data = self.scaler.fit_transform(data)
        
        # Create sequences
        X, y = [], []
        for i in range(self.lookback_period, len(scaled_data) - self.prediction_horizon):
            X.append(scaled_data[i-self.lookback_period:i, 0])
            y.append(scaled_data[i+self.prediction_horizon-1, 0])
        
        X, y = np.array(X), np.array(y)
        
        # Reshape X to be 3-dimensional input for LSTM [samples, time steps, features]
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        # Split into training and testing
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        logger.info("Data prepared for LSTM model")
        return X_train, y_train, X_test, y_test
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              epochs: int = 100, batch_size: int = 32) -> float:
        """Train the LSTM model"""
        input_shape = (X_train.shape[1], X_train.shape[2])
        self.model = self.create_model(input_shape)
        
        # Early stopping to prevent overfitting
        early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        
        # Train model
        history = self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, 
                                 validation_split=0.2, callbacks=[early_stopping], verbose=0)
        
        # Return validation loss
        val_loss = history.history['val_loss'][-1]
        logger.info(f"LSTM model training complete with validation loss {val_loss}")
        return val_loss
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using the trained LSTM model"""
        if self.model is None:
            raise ValueError("Model is not trained")
        
        predictions = self.model.predict(X)
        # Inverse scale predictions
        predictions = self.scaler.inverse_transform(predictions)
        logger.info("Predictions generated using LSTM model")
        return predictions
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """Evaluate the LSTM model performance"""
        predictions = self.predict(X_test)
        # Calculate RMSE
        rmse = np.sqrt(np.mean(np.square(y_test - predictions[:, 0])))
        logger.info(f"Model evaluation complete with RMSE: {rmse}")
        return rmse

