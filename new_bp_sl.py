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

# 3. 위치 데이터 이용_경로 계산
## 지하철역 위치 데이터 불러오기
import openpyxl
df_sub_addr = pd.read_excel('전체_도시철도역사정보_20250417.xlsx')
df_sub_addr = df_sub_addr[df_sub_addr['운영기관명'].str.contains('서울')]
df_sub_addr.loc[:, 'CGG_NM'] = df_sub_addr['역사도로명주소'].str.extract(r'([가-힣]+구)')
df_sub_addr.loc[:, 'STDG_NM'] = df_sub_addr['역사도로명주소'].str.extract(r'\(([^,()]+동)')
subway = df_sub_addr[['CGG_NM', 'STDG_NM', '역사명', '역위도', '역경도']]
subway = subway.drop_duplicates(subset='역사명')

filtered_subway = subway[
    (subway['CGG_NM'].isin(filtered_real_estate['CGG_NM'])) &
    (subway['STDG_NM'].isin(filtered_real_estate['STDG_NM']))
]
## 학교 위치 데이터 불러오기
df_school_addr = pd.read_csv('전국초중등학교위치표준데이터.csv', encoding='cp949')
df_school_addr = df_school_addr[df_school_addr['시도교육청명'] == '서울특별시교육청']
df_school_addr.loc[:, 'CGG_NM'] = df_school_addr['소재지지번주소'].str.extract(r'([가-힣]+구)')
df_school_addr.loc[:, 'STDG_NM'] = df_school_addr['소재지지번주소'].str.extract(r'([가-힣]+동)')
school = df_school_addr[['CGG_NM', 'STDG_NM', '학교명', '위도', '경도']]

filtered_school = school[
    (school['CGG_NM'].isin(filtered_real_estate['CGG_NM'])) &
    (school['STDG_NM'].isin(filtered_real_estate['STDG_NM']))
]

import requests
import time
import json
import os

# 여기 카카오
import requests
import json
import os

KAKAO_REST_API_KEY = "58a94e08cd433f0a789ddee57624f990"
CACHE_PATH = "coord_cache.json"

# 캐시 로드
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        coord_cache = json.load(f)
else:
    coord_cache = {}

def get_coords_from_address(address, api_key, cache):
    if address in cache:
        return cache[address]

    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            data = res.json()
            if data['documents']:
                first = data['documents'][0]
                lat = float(first['y'])
                lng = float(first['x'])
                cache[address] = (lat, lng)
                return lat, lng
    except Exception as e:
        print(f"Error for address {address}: {e}")
    return None, None

lat_list = []
lng_list = []

for addr in filtered_real_estate['address']:
    lat, lng = get_coords_from_address(addr, KAKAO_REST_API_KEY, coord_cache)
    lat_list.append(lat)
    lng_list.append(lng)

filtered_real_estate['위도'] = lat_list
filtered_real_estate['경도'] = lng_list

# 캐시 저장
with open(CACHE_PATH, "w", encoding="utf-8") as f:
    json.dump(coord_cache, f, ensure_ascii=False, indent=2)

st.dataframe(filtered_real_estate)




# SHP 파일로 변환
from shapely.geometry import Point
import geopandas as gpd
import matplotlib.pyplot as plt


geometry = [Point(xy) for xy in zip(filtered_real_estate['경도'], filtered_real_estate['위도'])]
gdf_points = gpd.GeoDataFrame(filtered_real_estate, geometry=geometry, crs="EPSG:4326")
gdf_points = gdf_points.to_crs(epsg=5179)
gdf_points.to_file("real_estate_points_5179.shp", encoding="euc-kr")
gdf_estate = gpd.read_file("real_estate_points_5179.shp")

geometry1 = [Point(xy) for xy in zip(subway["역경도"], subway["역위도"])]
gdf_points1 = gpd.GeoDataFrame(subway, geometry=geometry1, crs="EPSG:4326")
gdf_points1 = gdf_points1.to_crs(epsg=5179)
gdf_points1.to_file("seoul_sub_points_5179.shp", encoding="euc-kr")
gdf_subway = gpd.read_file("seoul_sub_points_5179.shp")

geometry2 = [Point(xy) for xy in zip(school["경도"], school["위도"])]
gdf_points2 = gpd.GeoDataFrame(school, geometry=geometry2, crs="EPSG:4326")
gdf_points2 = gdf_points2.to_crs(epsg=5179)
gdf_points2.to_file("seoul_school_points_5179.shp", encoding="euc-kr")
gdf_school = gpd.read_file("seoul_school_points_5179.shp")


gdf_boundary = gpd.read_file("seoul_emd.shp", encoding='euc-kr')
gdf_boundary = gdf_boundary.to_crs(epsg=5179)

fig, ax = plt.subplots(figsize=(16, 16))
gdf_boundary.plot(ax=ax, edgecolor='gray', facecolor='none', linewidth=0.5)
gdf_subway.plot(ax=ax, color='red', markersize=30, label='Subway')
gdf_school.plot(ax=ax, color='green', markersize=30, label='School')
gdf_estate.plot(ax=ax, color='blue', markersize=100, label='Real Estate')

ax.set_title("서울시 지하철·학교·부동산 위치", fontsize=18)
ax.legend()
st.pyplot(fig)








import folium
from streamlit_folium import st_folium

# Mapbox API 키
MAPBOX_TOKEN = 'pk.eyJ1IjoidmxmdG1kNjAwOCIsImEiOiJjbWMxaTRkOGswNmQ5Mmtvano2MmdqdHdrIn0.ckEJMKAK1p8t7Ss3XfFsFg'

@st.cache_data
def load_data():
    gdf_subway = gpd.read_file("seoul_sub_points_5179.shp").to_crs(epsg=4326)
    subway_info = list(zip(gdf_subway.geometry.x, gdf_subway.geometry.y, gdf_subway['역사명']))

    gdf_school = gpd.read_file("seoul_school_points_5179.shp").to_crs(epsg=4326)
    school_info = list(zip(gdf_school.geometry.x, gdf_school.geometry.y, gdf_school['학교명']))
    return subway_info, school_info

def get_routes_and_map(filtered_real_estate, subway_info, school_info):
    valid_subway_pairs = []
    valid_school_pairs = []

    m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

    for idx, row in filtered_real_estate.iterrows():
        dest_lat = row['위도']
        dest_lon = row['경도']
        address = row['address']
        if dest_lat == 0.0 or dest_lon == 0.0:
            continue

        # 지하철 처리
        closest_subway = min(subway_info, key=lambda x: (dest_lat - x[1])**2 + (dest_lon - x[0])**2)
        subway_lon, subway_lat, subway_name = closest_subway
        origin_subway = f"{subway_lon},{subway_lat}"
        destination = f"{dest_lon},{dest_lat}"
        url = f"https://api.mapbox.com/directions/v5/mapbox/walking/{origin_subway};{destination}"
        params = {
            "access_token": MAPBOX_TOKEN,
            "geometries": "geojson",
            "overview": "full"
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if 'routes' in data and data['routes']:
                distance = data['routes'][0]['distance']
                if distance <= 800:
                    valid_subway_pairs.append({
                        '매물주소': address,
                        '지하철역': subway_name,
                        '도보거리(m)': round(distance)
                    })
                    coords = data['routes'][0]['geometry']['coordinates']
                    folium.PolyLine(
                        locations=[[lat, lon] for lon, lat in coords],
                        color="blue", weight=3, opacity=0.7
                    ).add_to(m)
                    folium.Marker([dest_lat, dest_lon], popup=f"매물\n{address}",
                                  icon=folium.Icon(color="red", icon="home")).add_to(m)
                    folium.Marker([subway_lat, subway_lon], popup=f"지하철: {subway_name}",
                                  icon=folium.Icon(color="green", icon="train")).add_to(m)
        except Exception as e:
            st.warning(f"지하철 경로 오류: {origin_subway} → {destination} / {e}")

        # 학교 처리
        closest_school = min(school_info, key=lambda x: (dest_lat - x[1])**2 + (dest_lon - x[0])**2)
        school_lon, school_lat, school_name = closest_school
        origin_school = f"{school_lon},{school_lat}"
        try:
            response = requests.get(f"https://api.mapbox.com/directions/v5/mapbox/walking/{origin_school};{destination}", params=params)
            data = response.json()
            if 'routes' in data and data['routes']:
                distance = data['routes'][0]['distance']
                if distance <= 800:
                    valid_school_pairs.append({
                        '매물주소': address,
                        '학교': school_name,
                        '도보거리(m)': round(distance)
                    })
                    coords = data['routes'][0]['geometry']['coordinates']
                    folium.PolyLine(
                        locations=[[lat, lon] for lon, lat in coords],
                        color="purple", weight=3, opacity=0.7
                    ).add_to(m)
                    folium.Marker([dest_lat, dest_lon], popup=f"매물\n{address}",
                                  icon=folium.Icon(color="red", icon="home")).add_to(m)
                    folium.Marker([school_lat, school_lon], popup=f"학교: {school_name}",
                                  icon=folium.Icon(color="darkgreen", icon="school")).add_to(m)
        except Exception as e:
            st.warning(f"학교 경로 오류: {origin_school} → {destination} / {e}")

    return pd.DataFrame(valid_subway_pairs), pd.DataFrame(valid_school_pairs), m

def main():
    st.title("서울 매물-지하철/학교 도보 거리 분석")

    df_subway, df_school, folium_map = get_routes_and_map(filtered_real_estate, subway_info, school_info)

    st.subheader("지하철 도보 800m 이내 매물 리스트")
    st.dataframe(df_subway)

    st.subheader("학교 도보 800m 이내 매물 리스트")
    st.dataframe(df_school)

    st.subheader("지도")
    st_data = st_folium(folium_map, width=700, height=500)

if __name__ == "__main__":
    main()



