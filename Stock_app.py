st로 스트림된 가져오기
판다를 PD로 가져오기
datetime에서 가져오기 datetime
urllib. parse를 가져옵니다
가져오기 요청
bs4에서 BeautifulSoup 가져오기

# 웹 페이지 설정
st.set_page_config(페이지_title="미 증시 모닝 리포트", 레이아웃="와이드")

st.title("📊 통합 증시 모닝 리포트")
st.write(f"최종 업데이트): {datetime.now(.strftime('%Y-%m-%d %H:%M')})"

# --- 함수 정의 (기존 코드와 동일) ---
def translated_to_kor(텍스트):
 시도:
 URL = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q=" + urllib.parse.인용문(텍스트)
 res = requests.get(url, 타임아웃=5).json ()
 반품 해상도[0][0]
 예외: 텍스트 반환

def get_stock_data(이름, 티커):
 헤더 = {'사용자 에이전트': '모질라/5.0'}
 시도:
 # 주가 정보
 c_url = f"https://query1.finance.yahoo.com/v8/finance/chart/ {ticker}?interval=1d⦥=5d"
 c_res = requests.get(c_url, 헤더=headers)json ()
 가격 = c_res['차트']['result'][0]['indic']['adj 마감'][0]
 diff = ((prices[-1] - 가격[-2]) / 가격[-2] * 100
        
 # 뉴스 정보
 s_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={ticker}"
 s_res = requests.get(s_url, 헤더=headers)json ()
 뉴스 = s_res.get ('news', [][][:3]
 반품 가격[-1], diff, 뉴스
 제외: 없음, 없음, 없음, [] 반환

# --- 메인 화면 구성 ---
stocks = {"미국 환율": "USDKRW=X", "애플": "AAPL", "마이크로소프트": "MSFT", "구글": "GOOGL", "아마존": "AMZN", "메타": "META", "테슬라": "TSLA", "엔비디아": "NVDA", "SOXL": "SOXL", "TQQQ": "TQQQ"}

# 주식 섹션 (카드 형식)
st.header("🇺🇸 미국 증시 및 환율")
cols = st.columns(5) # 5열 레이아웃

for i, (name, ticker) in enumerate(stocks.items()):
    with cols[i % 5]:
        price, diff, news_list = get_stock_data(name, ticker)
        if price:
            color = "normal" if abs(diff) < 0.1 else "inverse" if diff < 0 else "off"
            st.metric(label=name, value=f"{price:,.2f}", delta=f"{diff:.2f}%")
            with st.expander("관련 뉴스 보기"):
                for n in news_list:
                    st.write(f"🔗 [{translate_to_kor(n['title'])}]({n['link']})")

st.divider()

# 한국 뉴스 섹션
st.header("🇰🇷 한국 주요 경제 뉴스")
try:
    url = "https://news.naver.com/section/101"
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(res.text, 'html.parser')
    news_items = soup.find_all(['a'], class_='sa_text_title')[:10]
    
    for i, item in enumerate(news_items):
        st.write(f"{i+1}. [{item.get_text().strip()}]({item.get('href')})")
except:
    st.error("한국 뉴스를 가져오는 중 오류가 발생했습니다.")
