import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="서울 100년 기온 변화 추이",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 지난 100년간 서울의 연평균 기온 변화")
st.markdown("기상청 데이터를 바탕으로 서울의 연도별 평균 기온 변화 추이를 시각화합니다.")

# 데이터 불러오기 (캐싱 적용)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"
    # encoding='cp949' 또는 'utf-8' 대응
    try:
        df = pd.read_csv(url, encoding='cp949')
    except Exception:
        df = pd.read_csv(url, encoding='utf-8')
    
    # 컬럼명 공백 제거
    df.columns = df.columns.str.strip()
    
    # 컬럼명 표준화 (기온 컬럼명에 단위(℃)가 들어간 경우 대응)
    rename_dict = {}
    for col in df.columns:
        if '날짜' in col:
            rename_dict[col] = '날짜'
        elif '평균' in col:
            rename_dict[col] = '평균기온'
        elif '최저' in col:
            rename_dict[col] = '최저기온'
        elif '최고' in col:
            rename_dict[col] = '최고기온'
    df.rename(columns=rename_dict, inplace=True)
    
    # 날짜 데이터 변환 및 연도 추출
    df['날짜'] = pd.to_datetime(df['날짜'])
    df['연도'] = df['날짜'].dt.year
    
    # 결측치 제거
    df = df.dropna(subset=['평균기온'])
    return df

try:
    with st.spinner("데이터를 불러오는 중입니다..."):
        df = load_data()

    # 연도별 평균 기온 계산
    yearly_df = df.groupby('연도')['평균기온'].mean().reset_index()
    yearly_df['평균기온'] = yearly_df['평균기온'].round(2)

    # 5년/10년 이동평균선 추가 (추세 파악용)
    yearly_df['10년 이동평균'] = yearly_df['평균기온'].rolling(window=10, min_periods=1).mean().round(2)

    # 지표 요약
    col1, col2, col3, col4 = st.columns(4)
    min_year = int(yearly_df['연도'].min())
    max_year = int(yearly_df['연도'].max())
    first_temp = yearly_df.iloc[0]['평균기온']
    last_temp = yearly_df.iloc[-1]['평균기온']
    max_temp_year = yearly_df.loc[yearly_df['평균기온'].idxmax()]

    col1.metric("관측 기간", f"{min_year}년 ~ {max_year}년")
    col2.metric("전체 평균 기온", f"{yearly_df['평균기온'].mean():.1f} °C")
    col3.metric("최고 연평균 기온", f"{max_temp_year['평균기온']} °C", f"{int(max_temp_year['연도'])}년")
    col4.metric("기온 변화 (최초 대비 최신)", f"{last_temp} °C", f"{last_temp - first_temp:+.1f} °C")

    st.markdown("---")

    # 인터랙티브 라인 차트 생성 (Plotly)
    fig = px.line(
        yearly_df,
        x='연도',
        y=['평균기온', '10년 이동평균'],
        title="서울 연도별 평균 기온 및 10년 이동평균 추이",
        labels={'연도': '연도', 'value': '기온 (°C)', 'variable': '구분'},
        color_discrete_map={'평균기온': '#FF5722', '10년 이동평균': '#1E88E5'}
    )
    
    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True, title="기온 (°C)"),
        legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 상세 데이터 확인용 확장 탭
    with st.expander("📊 상세 연도별 데이터 보기"):
        st.dataframe(yearly_df.sort_values(by='연도', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")
