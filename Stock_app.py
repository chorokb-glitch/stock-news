import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import requests
from bs4 import BeautifulSoup

# 웹 페이지 설정
st.set_page_config(page_title="미 증시 모닝 리포트", layout="wide")

st.title("📊 통합 증시 모닝 리포트")
st.write(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# 공통 헤더 (봇 차단 방지)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def translate_to_kor(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q=" + urllib.parse.quote(text)
        res = requests.get(url, headers=HEADERS, timeout=5).json()
        return res[0][0][0]
    except: return text

def get_stock_data(name, ticker):
    try:
        # 주가 정보 호출
        c_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
        c_res = requests.get(c_url, headers=HEADERS, timeout=10).json()
        prices = c_res['chart']['result'][0]['indicators']['adjclose'][0]['adjclose']
        # None 값 제거 후 마지막 가격 추출
        clean_prices = [p for p in prices if p is not None]
        price = clean_prices[-1]
        prev = clean_prices[-2]
        diff = ((price - prev) / prev) * 100
        
        # 뉴스 정보 호출 (더 안정적인 검색 엔드포인트 활용)
        s_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={ticker}"
        s_res = requests.get(s_url, headers=HEADERS, timeout=10).json()
        news = s_res.get('news', [])[:3]
        return price, diff, news
    except Exception as e:
        return None, None, []

# --- 메인 화면 구성 ---
stocks = {"미국 환율": "USDKRW=X", "애플": "AAPL", "마이크로소프트": "MSFT", "구글": "GOOGL", "아마존": "AMZN", "메타": "META", "테슬라": "TSLA", "엔비디아": "NVDA", "SOXL": "SOXL", "TQQQ": "TQQQ"}

st.header("🇺🇸 미국 증시 및 환율")
cols = st.columns(5)

for i, (name, ticker) in enumerate(stocks.items()):
    with cols[i % 5]:
        price, diff, news_list = get_stock_data(name, ticker)
        if price is not None:
            st.metric(label=name, value=f"{price:,.2f}", delta=f"{diff:.2f}%")
            with st.expander("뉴스 보기"):
                if news_list:
                    for n in news_list:
                        title = translate_to_kor(n.get('title', '제목 없음'))
                        link = n.get('link', '#')
                        st.markdown(f"🔗 [{title}]({link})")
                else:
                    st.write("관련 뉴스가 없습니다.")
        else:
            st.error(f"{name} 로딩 실패")

st.divider()

# 한국 뉴스 섹션
st.header("🇰🇷 한국 주요 경제 뉴스")
try:
    # 네이버 경제 속보 페이지가 크롤링에 더 유리함
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"
    res = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 새로운 네이버 뉴스 구조에 맞게 수정
    news_tags = soup.select('.nlist_item_contents .nlist_item_ttl') or soup.select('.newsflash_body .type06_headline a')
    
    if news_tags:
        for i, tag in enumerate(news_tags[:10]):
            title = tag.get_text().strip()
            link = tag.get('href')
            if not link.startswith('http'): link = "https://news.naver.com" + link
            st.write(f"{i+1}. [{title}]({link})")
    else:
        st.info("현재 새로운 뉴스를 불러올 수 없습니다. 잠시 후 시도해 주세요.")
except Exception as e:
    st.error(f"한국 뉴스 로딩 중 오류가 발생했습니다.")
