import streamlit as st
import pandas as pd
from math import log, sqrt, exp
from scipy.stats import norm
import yfinance as yf
from fredapi import Fred

FED_API_KEY = st.secrets['FRED_API_KEY']

def black_scholes_call(spot, strike, risk_free_rate, time, volatility):
    d1 = (log(spot / strike) + time * (risk_free_rate + 0.5 * volatility ** 2)) / (volatility * sqrt(time))
    d2 = d1 - volatility * sqrt(time)
    return spot * norm.cdf(d1) - strike * exp(-risk_free_rate * time) * norm.cdf(d2)

def black_sholes_put(spot, strike, risk_free_rate, time, volatility):
    d1 = (log(spot / strike) + time * (risk_free_rate + 0.5 * volatility ** 2)) / (volatility * sqrt(time))
    d2 = d1 - volatility * sqrt(time)
    return strike * exp(-risk_free_rate * time) * norm.cdf(-d2) - spot * norm.cdf(-d1)

def get_data(ticker, period='1y', interval='1d'):
    # Fetch stock price
    stock = yf.Ticker(ticker)
    stock_price = stock.history(period=interval)['Close'][0]

    # Fetch historical data to calculate volatility
    data = stock.history(period=period)
    data['returns'] = data['Close'].pct_change()
    volatility = data['returns'].std() * (252 ** 0.5)  # Annualized volatility

    return data, stock_price, volatility

def get_fred_data(series_id='DGS10'):
    # Fetch risk-free rate (10-year Treasury yield)
    fred = Fred(api_key=FED_API_KEY)
    risk_free_rate = fred.get_series(series_id).iloc[-1] / 100
    return risk_free_rate

st.write("## Black-Scholes Option Pricing Calculator")
st.text_input("Enter your ticker", key="ticker")
st.slider("Set time in years", min_value=0.1, max_value=5.0, step=0.1, key="time")
clicked = st.button("Calculate")

if clicked:
    ticker = st.session_state.ticker
    time = st.session_state.time
    data, stock_price, volatility = get_data(ticker)
    risk_free_rate = get_fred_data()

    # Calculate option price
    call_price = black_scholes_call(stock_price, stock_price, risk_free_rate, time, volatility)
    put_price = black_sholes_put(stock_price, stock_price, risk_free_rate, time, volatility)

    st.write("### Inputs")
    st.write(f"Ticker: {ticker}")
    st.write(f"Time: {time} years")
    st.write(f"Risk-free rate: {risk_free_rate:.2%}")
    st.write(f"Volatility: {volatility:.2%}")

    st.write("### Outputs")
    st.write(f"Option price: ${call_price:.2f} for call")
    st.write(f"Option price: ${put_price:.2f} for put")
    st.line_chart(data['Close'])
