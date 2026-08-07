import streamlit as st
from google import genai
from google.genai import types
import json
import os
import random

# 구글 AI에게 기출 원본 요청
def generate_real_exam(api_key):
    # 🛠️ [공백 버그 원천 차단] 키 앞뒤에 숨은 공백이나 스페이스바를 컴퓨터가 강제로 지우고 깨끗하게 읽도록 만듭니다.
    clean_key = str(api_key).strip()
    client = genai.Client(api_key=clean_key)
    
    system_prompt = (
        "너는 전기기능사 국가자격증 시험의 전문 기출문제 보관소야.\n"
        "절대로 문제를 변형하거나 창작하지 말고, 2023~2026년 한국산업인력공단 필기 시험에 출제되었던 '진짜 원본 기출문제' 중 1문제를 복원해줘.\n"
        "반드시 지정된 JSON 형식으로만 답변하고 앞뒤로 설명 글은 절대 붙이지 마.\n\n"
        "{\n"
        '  "연도": "202X년 진짜 기출 원본",\n'
        '  "과목": "과목명",\n'
        '  "문제": "실제 출제된 문제 원본",\n'
        '  "보기": ["1) 보기1", "2) 보기2", "3) 보기3", "4) 보기4"],\n'
        '  "정답": "정답 숫자 (1~4 중 하나)",\n'
        '  "해설": "상세한 수식 풀이 및 핵심 요약"\n'
        "}"
    )
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents='전기기능사 실제 기출문제 중 1개를 원본 그대로 복원해줘.',
        config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.3)
    )
    return json.loads(response.text.strip())

# 오답 저장 및 로드 기능
def save_wrong_answer(quiz_data):
    filename = "wrong_answers.json"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            wrong_list = json.load(f)
    else:
        wrong_list = []
    if quiz_data not in wrong_list:
        wrong_list.append(quiz_data)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(wrong_list, f, ensure_ascii=False, indent=4)

def load_wrong_answers():
    filename = "wrong_answers.json"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 📱 모바일 화면 최적화 세팅
st.set_page_config(page_title="전기기능사 기출앱", page_icon="⚡", layout="centered")

# 🛠️ [가장 중요] 여기에 김경욱 님의 진짜 구글 무료 API 키(AIzaSy...)를 정확하게 붙여넣으세요!
MY_API_KEY = "AQ.Ab8RN6Jsybtta-vQhZk-o2H62umJ80RtHOd1_yF4Mu6cahG-6w"

# 🎨 [글자 크기 시원시원하게 2배로 키우는 디자인]
st.markdown("""
    <style>
    .stRadio p {
        font-size: 22px !important;
        font-weight: bold !important;
        line-height: 1.6 !important;
    }
    .stButton button p {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'quiz' not in st.session_state:
    st.session_state.quiz = None
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

st.title("⚡ 전기기능사 스마트 기출앱")
menu = st.radio("모드 선택", ["📢 메인 화면", "🎯 최신 기출 풀기", "📝 내 오답노트 복습"], horizontal=True)
st.markdown("---")

if menu == "📢 메인 화면":
    st.subheader("김경욱 님, 환영합니다! 👋")
    wrong_count = len(load_wrong_answers())
    st.metric(label="현재 누적된 오답 개수", value=f"{wrong_count}개")
    st.info("💡 위의 메뉴 탭에서 '최신 기출 풀기'를 누르면 즉시 시험이 가동됩니다.")

elif menu == "🎯 최신 기출 풀기":
    if st.session_state.quiz is None:
        with st.spinner("새로운 기출문제 소환 중..."):
            st.session_state.quiz = generate_real_exam(MY_API_KEY)
            st.session_state.submitted = False

    if st.session_state.quiz:
        q = st.session_state.quiz
        st.info(f"📌 {q['연도']} / {q['과목']}")
        st.markdown(f"### **Q. {q['문제']}**")
        
        choice = st.radio("정답 선택:", q['보기'], index=None, key="real_radio")
        
        if choice and not st.session_state.submitted:
            if st.button("📝 정답 제출 및 채점하기", use_container_width=True, type="primary"):
                st.session_state.submitted = True
                st.rerun()

        if st.session_state.submitted:
            if str(choice) == str(q['정답']):
                st.success("⭕ 정답입니다! 아주 훌륭하십니다! 🎉")
            else:
                st.error(f"❌ 틀렸습니다! (실제 정답: {q['정답']}번)")
                save_wrong_answer(q)
                
            st.warning(f"💡 [기출 해설]\n{q['해설']}")
            st.markdown("---")
            if st.button("➡️ 다음 진짜 기출문제 풀기", use_container_width=True):
                st.session_state.quiz = None
                st.session_state.submitted = False
                st.rerun()

elif menu == "📝 내 오답노트 복습":
    wrong_list = load_wrong_answers()
    st.subheader(f"📝 틀린 문제 복습방 (총 {len(wrong_list)}개)")
    
    if not wrong_list:
        st.success("🎉 현재 저장된 오답이 없습니다!")
    else:
        if st.button("🎲 오답 중 1문제 랜덤 추출하여 재시험", use_container_width=True):
            st.session_state.review_quiz = random.choice(wrong_list)
            st.session_state.review_submitted = False
            
        if 'review_quiz' in st.session_state:
            rq = st.session_state.review_quiz
            st.markdown(f"### **Q. {rq['문제']}**")
            r_choice = st.radio("다시 푸는 정답 선택:", rq['보기'], index=None, key="review_radio")
            
            if r_choice and not st.session_state.get('review_submitted', False):
                if st.button("📝 복습 정답 제출", use_container_width=True, type="primary"):
                    st.session_state.review_submitted = True
                    st.rerun()
                    
            if st.session_state.get('review_submitted', False):
                if str(r_choice) == str(rq['정답']):
                    st.success("⭕ 맞췄습니다! 오답을 정복하셨네요! 👏")
                else:
                    st.error(f"❌ 또 틀렸습니다! (정답: {rq['정답']}번)")
                st.warning(f"💡 [해설 다시보기]\n{rq['해설']}")
