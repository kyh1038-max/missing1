import streamlit as st
import pandas as pd

# 1. 유사도 및 매칭 알고리즘 함수 정의
def age_similarity(u, d):
    diff = abs(u - d)
    return 1 / (1 + diff)

def blood_similarity(u, d):
    return 1.0 if u == d else 0.2

def feature_similarity(u, d):
    return 1.0 if u == d else 0.3

def compare(user, row):
    # 성별 일치 여부 확인 (기본 필터)
    if user["gender"] != row["gender"]:
        return None

    # 각 항목별 유사도 점수 계산
    age_score = age_similarity(user["age"], row["age"])
    blood_score = blood_similarity(user["blood_type"], row["blood_type"])
    feature_score = feature_similarity(user["feature"], row["feature"])

    # 가중치 반영 (나이 60%, 혈액형 25%, 특징 15%)
    total_score = (
        age_score * 0.6 +
        blood_score * 0.25 +
        feature_score * 0.15
    )

    return {
        "id": row["id"],
        "score": round(total_score * 100, 2),
        "age_similarity": round(age_score, 3),
        "blood_similarity": blood_score,
        "feature_similarity": feature_score
    }

def recommend(user_input, df):
    results = []
    for _, row in df.iterrows():
        r = compare(user_input, row)
        if r is not None:
            results.append(r)
    
    # 매칭 점수 기준 내림차순 정렬
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

# 2. Streamlit UI 레이아웃 구성
st.set_page_config(page_title="장기실종자 매칭 시스템", layout="wide")

st.title("장기실종자 데이터 기반 매칭 시스템")
st.markdown("제보된 정보와 기존 데이터를 비교 분석하여 유사도가 높은 대상을 찾아주는 프로그램입니다.")

# 세션 상태 초기화
if "recommend_results" not in st.session_state:
    st.session_state.recommend_results = None

# 사이드바: 데이터 파일 로드
st.sidebar.header("데이터 관리")
uploaded_file = st.sidebar.file_uploader("데이터베이스 CSV 파일을 업로드하세요.", type=["csv"])

if uploaded_file is not None:
    # 데이터 읽기 및 컬럼 전처리
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    st.sidebar.success("데이터베이스 로드 완료")
    
    # 원본 데이터 확인 공간
    with st.expander("업로드된 원본 데이터 확인 (상위 5개 행)"):
        st.dataframe(df.head())

    # 메인 화면: 제보 정보 입력 폼
    st.header("제보 정보 입력")
    
    with st.form("user_input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("추정 나이 (Age)", min_value=1, max_value=100, value=24)
            gender = st.radio("성별 (Gender)", options=[1, 0], format_func=lambda x: "남성" if x == 1 else "여성")
            
        with col2:
            blood_type = st.selectbox("혈액형 (Blood Type)", options=["A", "B", "O", "AB"], index=3)
            feature = st.number_input("특징 코드 (Feature)", min_value=0, max_value=10, value=0)
            
        submit_button = st.form_submit_button(label="매칭 분석 실행")

    # 분석 실행
    if submit_button:
        user_input = {
            "age": age,
            "gender": gender,
            "blood_type": blood_type,
            "feature": feature
        }
        st.session_state.recommend_results = recommend(user_input, df)

    # 결과 출력
    if st.session_state.recommend_results is not None:
        st.header("분석 결과 리스트")
        results = st.session_state.recommend_results
        
        if results:
            res_df = pd.DataFrame(results)
            res_df.columns = ["대상 ID", "유사도 점수 (Score)", "나이 유사도", "혈액형 유사도", "특징 유사도"]
            
            top_match = results[0]
            st.info(f"분석 결과, 가장 유사도가 높은 대상의 ID는 '{top_match['id']}' 이며, 일치율은 {top_match['score']}%입니다.")
            
            # 전체 순위 테이블 출력
            st.dataframe(res_df, use_container_width=True)
        else:
            st.warning("입력하신 기본 조건(성별 등)과 일치하는 데이터가 데이터베이스에 존재하지 않습니다.")
            
else:
    st.info("왼쪽 사이드바에서 분석의 기준이 될 데이터베이스(CSV 파일)를 먼저 업로드해 주세요.")
