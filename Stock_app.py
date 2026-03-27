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

# 공통 헤더 (차단 방지용 PC 브라우저 정보)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
}

def translate_to_kor(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q=" + urllib.parse.quote(text)
        res = requests.get(url, headers=HEADERS, timeout=5).json()
        return res[0][0][0]
    except: return text

def get_stock_data(name, ticker):
    try:
        # 주가 정보
        c_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
        c_res = requests.get(c_url, headers=HEADERS, timeout=10).json()
        prices = [p for p in c_res['chart']['result'][0]['indicators']['adjclose'][0]['adjclose'] if p is not None]
        price, prev = prices[-1], prices[-2]
        diff = ((price - prev) / prev) * 100
        
        # 뉴스 정보
        s_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={ticker}"
        s_res = requests.get(s_url, headers=HEADERS, timeout=10).json()
        news = s_res.get('news', [])[:3]
        return price, diff, news
    except: return None, None, []

# --- 메인 화면: 미국 증시 ---
stocks = {"미국 환율": "USDKRW=X", "애플": "AAPL", "마이크로소프트": "MSFT", "구글": "GOOGL", "아마존": "AMZN", "메타": "META", "테슬라": "TSLA", "엔비디아": "NVDA", "SOXL": "SOXL", "TQQQ": "TQQQ"}

st.header("🇺🇸 미국 증시 및 환율")
cols = st.columns(5)
for i, (name, ticker) in enumerate(stocks.items()):
    with cols[i % 5]:
        price, diff, news_list = get_stock_data(name, ticker)
        if price:
            st.metric(label=name, value=f"{price:,.2f}", delta=f"{diff:.2f}%")
            with st.expander("뉴스 보기"):
                for n in news_list:
                    st.markdown(f"🔗 [{translate_to_kor(n['title'])}]({n['link']})")
        else: st.error(f"{name} 로딩 실패")

st.divider()

# --- 메인 화면: 한국 뉴스 (보강된 크롤러) ---
st.header("🇰🇷 한국 주요 경제 뉴스")

@st.cache_data(ttl=600) # 10분간 결과 저장 (잦은 요청으로 인한 차단 방지)
def get_korean_economy_news():
    news_list = []
    # 네이버 경제 '가장 많이 본 뉴스' 혹은 '속보' 페이지 사용
    urls = [
        "https://news.naver.com/section/101",
        "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"
    ]
    
    for url in urls:
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 네이버 뉴스의 다양한 HTML 태그 패턴들 탐색
            selectors = [
                '.sa_text_title',          # 최신 뉴스 섹션
                '.nlist_item_ttl',         # 리스트형 뉴스
                '.newsflash_body a',       # 속보형 뉴스
                '.sh_text_headline'        # 헤드라인 뉴스
            ]
            
            for selector in selectors:
                tags = soup.select(selector)
                for tag in tags:
                    title = tag.get_text().strip()
                    link = tag.get('href')
                    if title and link and len(title) > 10: # 너무 짧은 메뉴명 제외
                        if not link.startswith('http'): link = "https://news.naver.com" + link
                        if {'title': title, 'link': link} not in news_list:
                            news_list.append({'title': title, 'link': link})
                if len(news_list) >= 10: break
            if len(news_list) >= 10: break
        except: continue
    return news_list[:10]

kor_news = get_korean_economy_news()
if kor_news:
    for i, news in enumerate(kor_news):
        st.write(f"{i+1}. [{news['title']}]({news['link']})")
else:
    st.info("현재 한국 뉴스를 가져올 수 없습니다. 잠시 후 새로고침(R)을 눌러주세요.")
