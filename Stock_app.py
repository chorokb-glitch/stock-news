import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import urllib.parse
import requests
from bs4 import BeautifulSoup

# 페이지 설정
st.set_page_config(page_title="미 증시 리포트", layout="wide")

def translate_to_kor(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q=" + urllib.parse.quote(text)
        res = requests.get(url, timeout=5).json()
        return res[0][0][0]
    except: return text

st.title("📊 실시간 증시 모닝 리포트")

# 종목 리스트
stocks = {"미국 환율": "USDKRW=X", "애플": "AAPL", "마이크로소프트": "MSFT", "구글": "GOOGL", "아마존": "AMZN", "메타": "META", "테슬라": "TSLA", "엔비디아": "NVDA", "SOXL": "SOXL", "TQQQ": "TQQQ"}

# 주식 데이터 가져오기
cols = st.columns(5)
for i, (name, ticker) in enumerate(stocks.items()):
    with cols[i % 5]:
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="2d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                diff = ((price - prev) / prev) * 100
                st.metric(label=name, value=f"{price:,.2f}", delta=f"{diff:.2f}%")
                
                with st.expander("뉴스 보기"):
                    for n in data.news[:3]:
                        st.write(f"🔗 [{translate_to_kor(n['title'])}]({n['link']})")
        except:
            st.write(f"{name} 로딩 실패")

st.divider()
st.header("🇰🇷 한국 주요 뉴스")
try:
    res = requests.get("https://news.naver.com/section/101", headers={'User-Agent':'Mozilla/5.0'})
    soup = BeautifulSoup(res.text, 'html.parser')
    news = soup.select('.sa_text_title')[:10]
    for i, n in enumerate(news):
        st.write(f"{i+1}. [{n.get_text().strip()}]({n.get('href')})")
except:
    st.write("한국 뉴스를 불러올 수 없습니다.")
 
