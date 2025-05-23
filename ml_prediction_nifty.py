# -*- coding: utf-8 -*-
"""ML Prediction NIfty.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1WH7MM9UFLiz-STLL-vX5GCjT22RIRoWp
"""

!pip install yfinance pandas --quiet

import yfinance as yf
import pandas as pd

from google.colab import files
uploaded = files.upload()

import pandas as pd

nifty = pd.read_csv('Nifty 50 Historical Data-3 (1).csv')
print(nifty.head())
print(nifty.columns.tolist())

# Remove spaces from column names
nifty.columns = nifty.columns.str.strip()

# Convert 'Date' to datetime and sort (dates are in DD-MM-YYYY)
nifty['Date'] = pd.to_datetime(nifty['Date'], dayfirst=True)
nifty = nifty.sort_values('Date')

# Remove commas and convert to float
for col in ['Close', 'Open', 'High', 'Low']:
    nifty[col] = nifty[col].str.replace(',', '').astype(float)

# Convert 'Vol.' to numeric (e.g., '270.47M' to 270470000)
def parse_volume(val):
    val = str(val).replace(',', '').strip()
    if val.endswith('M'):
        return float(val[:-1]) * 1e6
    elif val.endswith('K'):
        return float(val[:-1]) * 1e3
    else:
        try:
            return float(val)
        except:
            return None

nifty['Volume'] = nifty['Vol.'].apply(parse_volume)

# Drop unnecessary columns
nifty = nifty[['Date', 'Close', 'Open', 'High', 'Low', 'Volume']]
nifty = nifty.dropna()
nifty = nifty.set_index('Date')
print(nifty.head())

from statsmodels.tsa.arima.model import ARIMA

close_prices = nifty['Close']

# Fit ARIMA model (order can be tuned)
model = ARIMA(close_prices, order=(1,1,1))
model_fit = model.fit()

# Forecast the next day's close
forecast = model_fit.forecast(steps=1)
print("Forecasted next close price:", forecast.iloc[0])

import matplotlib.pyplot as plt

plt.figure(figsize=(12,6))
plt.plot(nifty.index, nifty['Close'], label='Actual Close')
plt.plot(nifty.index, model_fit.fittedvalues, label='Fitted', linestyle='--')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.title('NIFTY 50 Actual vs. ARIMA Fitted Close')
plt.legend()
plt.tight_layout()
plt.show()

from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Fit the model
model = ExponentialSmoothing(nifty['Close'], trend='add', seasonal=None)
model_fit = model.fit()

# Forecast the next day
forecast = model_fit.forecast(steps=1)
print("Holt-Winters forecasted next close price:", forecast.iloc[0])

!pip install prophet --quiet

from prophet import Prophet

df = nifty.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds', 'Close':'y'})
model = Prophet()
model.fit(df)
future = model.make_future_dataframe(periods=1)
forecast = model.predict(future)
print("Prophet forecasted next close price:", forecast.iloc[-1]['yhat'])

from sklearn.ensemble import RandomForestRegressor
import numpy as np

# Create lagged features
nifty_ml = nifty.copy()
nifty_ml['lag1'] = nifty_ml['Close'].shift(1)
nifty_ml['lag2'] = nifty_ml['Close'].shift(2)
nifty_ml = nifty_ml.dropna()

X = nifty_ml[['lag1', 'lag2']]
y = nifty_ml['Close']

# Train/test split
X_train, y_train = X[:-1], y[:-1]
X_test = X[-1:]

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Forecast next close
forecast = model.predict(X_test)
print("Random Forest forecasted next close price:", forecast[0])

# 1. Install necessary packages
!pip install tensorflow scikit-learn pandas matplotlib --quiet

# 2. Load and clean your data
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# Replace with your actual filename if different
nifty = pd.read_csv('Nifty 50 Historical Data-3 (1).csv')

# Clean column names and data
nifty.columns = nifty.columns.str.strip()
nifty['Date'] = pd.to_datetime(nifty['Date'], dayfirst=True)
nifty = nifty.sort_values('Date')

# Remove commas and convert to float
for col in ['Close', 'Open', 'High', 'Low']:
    nifty[col] = nifty[col].astype(str).str.replace(',', '').astype(float)

# Convert 'Vol.' to numeric
def parse_volume(val):
    val = str(val).replace(',', '').strip()
    if val.endswith('M'):
        return float(val[:-1]) * 1e6
    elif val.endswith('K'):
        return float(val[:-1]) * 1e3
    else:
        try:
            return float(val)
        except:
            return np.nan

nifty['Volume'] = nifty['Vol.'].apply(parse_volume)
nifty = nifty[['Date', 'Close', 'Open', 'High', 'Low', 'Volume']]
nifty = nifty.dropna()
nifty.set_index('Date', inplace=True)

# 3. Prepare data for LSTM
close_prices = nifty['Close'].values.reshape(-1, 1)
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_close = scaler.fit_transform(close_prices)

sequence_length = 60
X, y = [], []
for i in range(sequence_length, len(scaled_close)):
    X.append(scaled_close[i-sequence_length:i, 0])
    y.append(scaled_close[i, 0])
X, y = np.array(X), np.array(y)
X = np.reshape(X, (X.shape[0], X.shape[1], 1))

split = int(0.8 * len(X))
X_train, y_train = X[:split], y[:split]
X_test, y_test = X[split:], y[split:]

# 4. Build and train the LSTM model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(LSTM(units=50))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=1)

# 5. Make predictions and plot results
predicted = model.predict(X_test)
predicted_prices = scaler.inverse_transform(predicted.reshape(-1, 1))
real_prices = scaler.inverse_transform(y_test.reshape(-1, 1))

plt.figure(figsize=(12,6))
plt.plot(real_prices, label='Actual Close')
plt.plot(predicted_prices, label='LSTM Predicted Close')
plt.title('NIFTY 50 Close Price Prediction with LSTM')
plt.xlabel('Time Step')
plt.ylabel('Price')
plt.legend()
plt.tight_layout()
plt.show()

# 6. Forecast the next day's close
last_sequence = scaled_close[-sequence_length:]
last_sequence = last_sequence.reshape((1, sequence_length, 1))
next_pred_scaled = model.predict(last_sequence)
next_pred = scaler.inverse_transform(next_pred_scaled)[0,0]
print("LSTM forecasted next close price:", next_pred)

forecast_days = 20  # Number of days to forecast

# Start with the last 'sequence_length' days from your scaled data
last_sequence = scaled_close[-sequence_length:].reshape(1, sequence_length, 1)

forecast_scaled = []

for _ in range(forecast_days):
    # Predict next value
    next_pred = model.predict(last_sequence)[0,0]
    forecast_scaled.append(next_pred)

    # Update the sequence by appending the prediction and removing the oldest value
    last_sequence = np.append(last_sequence[:,1:,:], [[[next_pred]]], axis=1)

# Inverse transform the scaled predictions to original price scale
forecast_prices = scaler.inverse_transform(np.array(forecast_scaled).reshape(-1,1))

# Print or plot the forecasted prices
print("Forecasted next month closing prices:")
print(forecast_prices.flatten())

