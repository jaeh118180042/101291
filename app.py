import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="서울 기온 분석", page_icon="🌡️")

st.title("🌡️ 서울 연도별 평균기온 분석")
st.caption("서울 기상관측 데이터 (1907년 ~ 현재)")

# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv("seoul_temperature.csv")
    
    # 날짜 컬럼의 탭 문자 제거
    df['날짜'] = df['날짜'].astype(str).str.strip()
    
    # 날짜 파싱
    df['날짜'] = pd.to_datetime(df['날짜'], format='%Y-%m-%d', errors='coerce')
    
    # 연도 추출
    df['연도'] = df['날짜'].dt.year
    
    # 1950-1953 결측치 제외
    df = df[~df['연도'].isin([1950, 1951, 1952, 1953])]
    
    # 결측치 제거 (기온 데이터)
    df = df.dropna(subset=['평균기온(℃)', '최저기온(℃)', '최고기온(℃)'])
    
    return df

df = load_data()

# 연도별 집계
yearly_df = df.groupby('연도').agg({
    '평균기온(℃)': 'mean',
    '최저기온(℃)': 'mean',
    '최고기온(℃)': 'mean'
}).reset_index()

yearly_df.columns = ['연도', '연평균기온', '연최저기온(평균)', '연최고기온(평균)']

# 5년 이동평균 계산
yearly_df['5년이동평균'] = yearly_df['연평균기온'].rolling(window=5, min_periods=1).mean()

# 사이드바 - 연도 범위 슬라이더
min_year = int(yearly_df['연도'].min())
max_year = int(yearly_df['연도'].max())

st.sidebar.header("📊 분석 설정")
selected_years = st.sidebar.slider(
    "연도 범위 선택",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

# 선택된 연도 필터링
filtered_df = yearly_df[
    (yearly_df['연도'] >= selected_years[0]) & 
    (yearly_df['연도'] <= selected_years[1])
]

# 그래프 그리기
fig = go.Figure()

# 연도별 평균기온 선
fig.add_trace(go.Scatter(
    x=filtered_df['연도'],
    y=filtered_df['연평균기온'],
    mode='lines+markers',
    name='연도별 평균기온',
    line=dict(color='#2563EB', width=2),
    marker=dict(size=5)
))

# 5년 이동평균선
fig.add_trace(go.Scatter(
    x=filtered_df['연도'],
    y=filtered_df['5년이동평균'],
    mode='lines',
    name='5년 이동평균',
    line=dict(color='#DC2626', width=3, dash='dash')
))

fig.update_layout(
    title=f"서울 연도별 평균기온 ({selected_years[0]}년 ~ {selected_years[1]}년)",
    xaxis_title="연도",
    yaxis_title="기온 (℃)",
    hovermode='x unified',
    template='plotly_white',
    height=500,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)

st.plotly_chart(fig, use_container_width=True)

# 선택 구간 통계 표시
st.subheader("📈 선택 구간 통계")

col1, col2, col3 = st.columns(3)

with col1:
    avg_temp = filtered_df['연평균기온'].mean()
    st.metric(
        label="평균 기온",
        value=f"{avg_temp:.2f} ℃",
        delta=None
    )

with col2:
    max_temp = filtered_df['연최고기온(평균)'].mean()
    st.metric(
        label="최고 기온 (연평균)",
        value=f"{max_temp:.2f} ℃",
        delta=None
    )

with col3:
    min_temp = filtered_df['연최저기온(평균)'].mean()
    st.metric(
        label="최저 기온 (연평균)",
        value=f"{min_temp:.2f} ℃",
        delta=None
    )

# 데이터 범위 정보
st.caption(f"데이터 범위: {min_year}년 ~ {max_year}년 (총 {len(yearly_df)}개년)")
st.caption("※ 1950년~1953년 데이터는 분석에서 제외되었습니다.")

# 원시 데이터 표시 (선택 사항)
with st.expander("📋 연도별 상세 데이터 보기"):
    st.dataframe(
        filtered_df[['연도', '연평균기온', '5년이동평균']].style.format({
            '연평균기온': '{:.2f} ℃',
            '5년이동평균': '{:.2f} ℃'
        }),
        use_container_width=True
    )
