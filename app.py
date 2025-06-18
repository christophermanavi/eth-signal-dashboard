
import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Ethereum (ETH) Signal Dashboard")

@st.cache_data
def load_data():
    df = yf.download('ETH-USD', start='2023-01-01', interval='1d')
    df.dropna(inplace=True)
    return df

eth = load_data()
eth['rsi'] = ta.momentum.RSIIndicator(eth['Close']).rsi()
eth['macd'] = ta.trend.MACD(eth['Close']).macd_diff()
eth['sma_10'] = ta.trend.SMAIndicator(eth['Close'], 10).sma_indicator()
eth['sma_30'] = ta.trend.SMAIndicator(eth['Close'], 30).sma_indicator()
eth['boll_hi'] = ta.volatility.BollingerBands(eth['Close']).bollinger_hband()
eth['boll_lo'] = ta.volatility.BollingerBands(eth['Close']).bollinger_lband()

def signal(row):
    if row['rsi'] < 30 and row['macd'] > 0 and row['Close'] < row['boll_lo'] and row['sma_10'] > row['sma_30']:
        return 'LONG'
    elif row['rsi'] > 70 and row['macd'] < 0 and row['Close'] > row['boll_hi'] and row['sma_10'] < row['sma_30']:
        return 'SHORT'
    return 'HOLD'

eth['signal'] = eth.apply(signal, axis=1)

st.subheader("ETH Price and Signals")
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(eth.index, eth['Close'], label='ETH Price', color='blue')
ax.plot(eth.index, eth['sma_10'], label='SMA 10', linestyle='--', color='green')
ax.plot(eth.index, eth['sma_30'], label='SMA 30', linestyle='--', color='red')
ax.scatter(eth[eth['signal'] == 'LONG'].index, eth[eth['signal'] == 'LONG']['Close'], label='LONG', color='green', marker='^', s=100)
ax.scatter(eth[eth['signal'] == 'SHORT'].index, eth[eth['signal'] == 'SHORT']['Close'], label='SHORT', color='red', marker='v', s=100)
ax.set_title('ETH Price with Buy/Sell Signals')
ax.set_ylabel('Price (USD)')
ax.legend()
st.pyplot(fig)

st.subheader("Recent Signals")
st.dataframe(eth[['Close', 'rsi', 'macd', 'sma_10', 'sma_30', 'signal']].tail(20))
