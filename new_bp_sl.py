import streamlit as st
import os

st.title("안녕하세요👋")
st.markdown("## 저희는 <span style='color:blue; font-weight:bold;'>부동산플랜</span>😈입니다.", unsafe_allow_html=True)
st.write("### 이 페이지에서 당신은 2018년부터 2024년까지의 서울시 부동산 실거래가 정보를 통해 데이터 기반의 매물 추천🏠📊을 받으실 수 있습니다.")

name = st.text_input("먼저 이름을 입력하세요", value='김바다')
if name:
    st.success(f"{name}님, 반가워요!🙌")
st.write("저희에겐 2018년부터 2024년까지의 서울시 부동산 실거래가 정보가 주어져있습니다. \
같은 주소의 매물이 시간에 따라 거래된 가격을 기준으로, 모든 거래를 2024년 수준의 가격으로 환산하겠습니다. \
이 작업은 부동산 가격의 시간에 따른 변화율을 활용하여 가격을 보정하는 작업입니다. \
가격 보정의 전체 흐름을 요약해드리자면")
st.write("""#### ✅ 전체 흐름 요약
1. 같은 건물 용도(컬럼명: BLDG_USG, 예: 아파트, 오피스텔 등)별로 연도별 평균 거래금액을 구함
2. 연도별 상승률을 계산 (예: 2020→2021 가격 변화율 등)
3. 각 연도별 거래건에 대해 누적 상승률을 계산해서 2024년 가격으로 보정
4. 모든 거래 데이터에 보정된 가격(컬럼명: THING_AMT_2024) 추가""")

st.write("또한, 방 개수와 신축 여부의 기준을 알려드리겠습니다.")
st.write("""#### 🏠 방 개수 구하기_건축 면적(컬럼명: ARCH_AREA) 기준
- 30㎡ 이하 **→** 방 1개
- 30㎡ 초과 ~ 70㎡ 이하 **→** 방 2개
- 70㎡ 초과 ~ 100㎡ 이하 **→** 방 3개
- 100㎡ 초과 **→** 방 4개 이상
#### 🆕 신축 여부 구하기_건축 연도(컬럼명: ARCH_YR) 기준
- 2019년부터 2024년까지에 지어진 건물 **→** 신축
- 그 외 **→** 구축""")

st.write(f"## 이제 {name}님이 원하시는 매물 가격, 방 개수, 건물 종류, 신축 여부를 선택해주세요.")
y = st.number_input("💰 예산을 숫자로 선택해주세요 (예: 400000000)", value=400000000, step = 100000000)
rooms = st.number_input("🔢 방 개수를 숫자로 선택해주세요 (예: 2, 3)", value=3)
usg = st.selectbox("🏘️ 건물 종류를 선택해주세요",
    ['아파트', '연립다세대', '단독다가구', '오피스텔'],
    index=0)
new_old = st.selectbox("🆕 신축 여부를 선택해주세요",
    ['신축', '구축'],
    index=0)

import pandas as pd 
real_estate = pd.read_csv("real_estate.csv", encoding='utf-8-sig')

def filter_by_price(df):
  return df[df['THING_AMT'] < y/10000]
def filter_by_rooms(df):
  return df[df['방개수'] == f"{rooms}개"]
def filter_by_usg(df):
  return df[df['BLDG_USG'] == usg]
def filter_by_new_old(df):
  return df[df['신축여부'] == new_old]

df_price = filter_by_price(real_estate)
df_rooms = filter_by_rooms(df_price)
df_usg = filter_by_usg(df_rooms)
df_final = filter_by_new_old(df_usg)

st.write("📊 가격, 방 개수, 건물 종류, 신축 여부로 필터링된 매물 데이터:")

if "show_result1" not in st.session_state:
    st.session_state["show_result1"] = False

if st.button("📋 결과 보기", key="show_result1_button"):
    st.session_state["show_result1"] = True

if st.session_state["show_result1"]:
    st.dataframe(df_final)

st.write(f"## 다음으로 {name}님이 원하시는 N개의 상위 법정동 찾아보겠습니다.")
st.write("저희는 서울시의 법정동 단위로 다양한 생활 인프라 지표(학원, 유흥주점, 대규모 점포, 병원)를 집계하고, \
         이를 병합하여 지표가 하나라도 존재하는 유효한 법정동 리스트 만들었습니다.\
         전체 흐름을 요약해드리자면")
st.write("""#### ✅ 전체 흐름 요약
1. 서울시의 법정동을 기준으로, 여러 외부 데이터를 병합합니다.
병합되는 주요 데이터들은 다음과 같습니다:""")
table_data = {
    "항목": [
        "`academy`",
        "`bar`",
        "`store`",
        "`hospital`, `second_hospital`, `third_hospital`"
    ],
    "설명": [
        "입시·보습 학원 수 (많을수록 좋음)",
        "유흥주점 수 (적을수록 좋음)",
        "대규모 점포 수 (많을수록 좋음)",
        "병의원 수, 2차 병원 수, 3차 병원 수 (많을수록 좋음)"
    ]
}

df_info = pd.DataFrame(table_data)

st.write("📊 활용 지표 설명")
st.dataframe(df_info)
st.write("⇒ 모든 지표값이 모두 없는(결측치인) 법정동은 제거합니다.")
st.write("""2. 병원의 중요도를 다르게 보고 가중치를 부여합니다:
- 일반 병원 수는 그대로 사용
- 2차 병원 수는 5배
- 3차 병원 수는 20배
이렇게 가중치를 적용해 총 병원 지표(컬럼명: t_hospital)를 계산합니다.""")
st.write("3. 각 지표가 얼마나 유의미한지를 데이터 자체에서 자동으로 판단해 가중치를 계산합니다.")
st.markdown("""
🔸 **Step 1. 정규화 (min-max scaling)**  
- 모든 지표를 0~1 범위로 정규화하여 비교 가능하도록 만듭니다.  

🔸 **Step 2. 엔트로피 값 계산**  
- 각 지표의 불확실성을 계산합니다.  
- 엔트로피 값이 높으면 → 다양성 ↓ → 구별력이 낮음  

🔸 **Step 3. 다양성(D) 계산**  
- D = 1 - 엔트로피  
- 다양성이 높을수록 정보량이 많은 지표라고 판단  

🔸 **Step 4. 최종 가중치 계산**  
- 전체 다양성 합계에서 비율을 나눠 각 지표의 **가중치 벡터 w**를 구합니다.  
""")
st.write("""4. 계산된 가중치를 활용해, 각 법정동의 종합 점수(score)를 구합니다:
- 유흥주점 수는 감점 요소이기 때문에 마이너스(-)로 계산합니다.
점수가 높은 순으로 정렬합니다.""")

topN = pd.read_csv("topN.csv", encoding='utf-8-sig')
N = st.number_input(f"## {name}님이 원하시는 상위 법정동의 개수를 선택해주세요. (예: 5, 10)", value=10)
top = topN.head(N)
top = pd.DataFrame(top)

if "show_result2" not in st.session_state:
    st.session_state["show_result2"] = False

if st.button("📋 결과 보기", key="show_result2_button"):
    st.session_state["show_result2"] = True

if st.session_state["show_result2"]:
    st.dataframe(top)

filtered_real_estate = pd.merge(df_final, top, how='inner', on=['CGG_NM', 'STDG_NM'])
st.write(f"### {name}님이 원하시는 상위 {N}개 법정동 내에서 가격, 방 개수, 건물 종류, 신축 여부로 필터링된 매물 리스트:")

if "show_result3" not in st.session_state:
    st.session_state["show_result3"] = False

if st.button("📋 결과 보기", key="show_result3_button"):
    st.session_state["show_result3"] = True

if st.session_state["show_result3"]:
    st.dataframe(filtered_real_estate.head(30))

st.write("## 다음으로 위의 필터링된 매물 리스트에서 가장 가까운 지하철역과 학교에 \
         도보 10분(800m) 이내로 갈 수 있는 매물들만 뽑아보겠습니다.")



import papermill as pm
filtered_real_estate.to_csv("filtered_real_estate.csv", index=False)
pm.execute_notebook(
    input_path="bp_sl.ipynb",
    output_path="bp_sl.ipynb",
    parameters=dict(input_file="filtered_real_estate.csv")
)

filtered_subway = pd.read_csv("filtered_subway.csv")
st.dataframe(filtered_subway)