import streamlit as st
from google import genai
from google.genai import types
import json
import os
import random
import time
from google.genai.errors import ClientError

# 60문제 세트를 한 번에 요청하는 시스템
def generate_60_exams(api_key):
    clean_key = str(api_key).strip()
    client = genai.Client(api_key=clean_key)
    
    system_prompt = (
        "너는 전기기능사(전기이론, 전기기기, 전기설비) 국가자격증 시험의 전문 출제위원 교육용 AI야.\n"
        "자격증 취득을 위한 60문항의 완성된 '실전 기출 동형 모의고사' 세트를 구성해라.\n"
        "실제 출제 기준 및 난이도와 유형(수식 계산, 복잡한 회로 이론, 설비 규정 등)을 완벽히 매칭하여 수험생이 진짜 시험으로 느낄 수 있게 정밀 제작해라.\n"
        "답변은 반드시 지정된 JSON 구조의 리스트([]) 형식으로만 출력하고 앞뒤에 Markdown 기호나 설명글을 절대 붙이지 마.\n\n"
        "🔥 [수식 표기 필수 규칙]:\n"
        "1. 문제, 보기, 해설에 나오는 모든 수학/물리 수식, 분수, 루트, 단위는 반드시 LaTeX 문법인 $ 기호로 감싸서 작성해라.\n"
        "2. 분수는 반드시 $\\frac{분자}{분모}$ 형태로 작성해라. (예: $\\frac{1}{2}$)\n"
        "3. 루트는 반드시 $\\sqrt{값}$ 형태로 작성해라. (예: $\\sqrt{3}$)\n"
        "4. 옴($\\Omega$), 마이크로패럿($\\mu F$) 등 전기 단위도 기호로 깔끔하게 처리해라.\n\n"
        "{\n"
        '  "exams": [\n'
        "    {\n"
        '      "번호": 1,\n'
        '      "과목": "전기이론",\n'
        '      "문제": "수식과 텍스트가 조합된 1번 문제 내용",\n'
        '      "보기": ["1) 보기1", "2) 보기2", "3) 보기3", "4) 보기4"],\n'
        '      "정답": "정답 숫자 (1~4)",\n'
        '      "해설": "상세한 수식 풀이 과정 및 핵심 요약"\n'
        "    },\n"
        "    ... 60번까지 반복 ...\n"
        "  ]\n"
        "}"
    )

    safety_settings = [
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    ]

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents="전기이론 20문제, 전기기기 20문제, 전기설비 20문제를 순서대로 배치하여 총 60문항으로 구성된 완벽한 JSON 시험 세트(전체 객체 형태)를 빌드해줘.",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt, 
                    temperature=0.6, 
                    safety_settings=safety_settings, 
                    response_mime_type="application/json" 
                )
            )
            raw_data = json.loads(response.text.strip())
            return raw_data.get("exams", [])
        except (ClientError, json.JSONDecodeError):
            time.sleep(2)
            if attempt == 2:
                return [{"번호": i, "과목": "전기이론", "문제": f"구글 API 연결 지연으로 인해 로드된 백업 모의 문항 {i}번입니다. 아래 정답 제출을 누르시면 다음 문항으로 무리 없이 이어집니다.", "보기": ["1) 연습용 보기 A", "2) 연습용 보기 B", "3) 연습용 보기 C", "4) 연습용 보기 D"], "정답": "1", "해설": "서버 상태 안정화 후 다음 세트에서 새로운 수식이 온전히 반영됩니다."} for i in range(1, 61)]

# ⭐ [오답 횟수 누적 기능이 고도화된 저장 함수]
def save_wrong_answer(quiz_data):
    filename = "wrong_answers.json"
    wrong_list = []
    
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                wrong_list = json.load(f)
                if not isinstance(wrong_list, list): wrong_list = []
            except:
                wrong_list = []
                
    # 이미 틀렸던 문제인지 체크하여 횟수 업그레이드
    found = False
    for item in wrong_list:
        if item.get("문제") == quiz_data.get("문제"):
            # 기존에 존재하던 문항이면 '틀린횟수' 데이터 1 증가
            item["틀린횟수"] = item.get("틀린횟수", 1) + 1
            found = True
            break
            
    if not found:
        # 최초로 틀린 문제인 경우 기본 1회로 세팅하여 추가
        quiz_data["틀린횟수"] = 1
        wrong_list.append(quiz_data)
        
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(wrong_list, f, ensure_ascii=False, indent=4)

def load_wrong_answers():
    filename = "wrong_answers.json"
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, "r", encoding="utf-8") as f:
            try: 
                res = json.load(f)
                return res if isinstance(res, list) else []
            except: 
                return []
    return []

# 📱 기본 앱 세팅 및 디자인 최적화
st.set_page_config(page_title="전기기능사 기출앱", page_icon="⚡", layout="centered")
REAL_GOOGLE_KEY = st.secrets.get("API_KEY", "")

st.markdown("""
    <style>
    .stRadio p { font-size: 21px !important; font-weight: bold !important; line-height: 1.6 !important; }
    .stButton button p { font-size: 19px !important; font-weight: bold !important; }
    .highlight-box { padding: 15px; border-radius: 10px; background-color: #f0f2f6; margin-bottom: 15px; border-left: 5px solid #ff4b4b; }
    .count-badge { padding: 4px 10px; border-radius: 5px; background-color: #ff4b4b; color: white; font-weight: bold; font-size: 14px; margin-left: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'exam_set' not in st.session_state: st.session_state.exam_set = None
if 'current_index' not in st.session_state: st.session_state.current_index = 0
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'exam_submitted' not in st.session_state: st.session_state.exam_submitted = False

st.title("⚡ 전기기능사 스마트 기출앱")
menu = st.radio("모드 선택", ["📢 메인 화면", "🎯 60문항 실전 모의고사", "📝 내 오답노트 복습"], horizontal=True)
st.markdown("---")

if menu == "📢 메인 화면":
    st.subheader("김경욱 님, 환영합니다! 👋")
    wrong_list = load_wrong_answers()
    wrong_count = len(wrong_list)
    
    # 여러 번 반복해서 자주 틀리는 상위 취약 문제 수 계산
    hard_count = sum(1 for item in wrong_list if item.get("틀린횟수", 1) >= 2)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="저장된 총 오답 문항 수", value=f"{wrong_count}개")
    with col2:
        st.metric(label="⚡ 2회 이상 중복 오답 수", value=f"{hard_count}개")
        
    st.info("💡 실전 모의고사 중 여러 번 연속해서 틀리는 고난도 문항은 오답노트에서 별도의 카운트 배지가 부여됩니다.")

elif menu == "🎯 60문항 실전 모의고사":
    if st.session_state.exam_set is None:
        st.subheader("📝 한국산업인력공단 기준 실전 모의고사")
        st.markdown("실제 시험과 동일하게 **전기이론, 전기기기, 전기설비 총 60문항**이 한 세트로 출제됩니다. (60점 이상 합격)")
        if st.button("🚀 새로운 60문항 시험지 출제하기", use_container_width=True, type="primary"):
            with st.spinner("구글 AI가 실전 유형을 엄선하여 새로운 60문제를 배치 중입니다. 잠시만 기다려주세요 (약 5초)..."):
                st.session_state.exam_set = generate_60_exams(REAL_GOOGLE_KEY)
                st.session_state.current_index = 0
                st.session_state.user_answers = {}
                st.session_state.exam_submitted = False
                st.rerun()

    else:
        exams = st.session_state.exam_set
        idx = st.session_state.current_index
        total_questions = len(exams)
        
        if not st.session_state.exam_submitted:
            q = exams[idx]
            st.progress((idx + 1) / total_questions)
            st.markdown(f"#### **문항 상태: {idx + 1} / {total_questions}번 문제**")
            st.markdown(f"<div class='highlight-box'><b>과목 구분:</b> {q.get('과목', '전기기능사')}</div>", unsafe_allow_html=True)
            st.markdown(f"### **Q{idx + 1}. {q['문제']}**")
            
            saved_choice = st.session_state.user_answers.get(idx, None)
            choice = st.radio("정답 선택:", q['보기'], index=q['보기'].index(saved_choice) if saved_choice in q['보기'] else None, key=f"exam_radio_{idx}")
            
            if choice:
                st.session_state.user_answers[idx] = choice

            col1, col2, col3 = st.columns()
            with col1:
                if st.button("⬅️ 이전 문제", disabled=(idx == 0), use_container_width=True):
                    st.session_state.current_index -= 1
                    st.rerun()
            with col2:
                if idx < total_questions - 1:
                    if st.button("다음 문제 ➡️", disabled=(choice is None), use_container_width=True):
                        st.session_state.current_index += 1
                        st.rerun()
                else:
                    if st.button("📊 시험지 최종 제출하고 채점하기", type="primary", use_container_width=True, disabled=(len(st.session_state.user_answers) < total_questions)):
                        st.session_state.exam_submitted = True
                        st.rerun()
            with col3:
                if st.button("❌ 시험 강제종료", type="secondary", use_container_width=True):
                    st.session_state.exam_set = None
                    st.rerun()

        else:
            st.subheader("🏁 모의고사 최종 결과 분석 보고서")
            
            correct_count = 0
            for i, exam_item in enumerate(exams):
                u_ans = st.session_state.user_answers.get(i, "")
                u_num = str(u_ans) if u_ans else ""
                r_ans = str(exam_item['정답']).strip()
                if u_num == r_ans:
                    correct_count += 1
                else:
                    if exam_item.get("연도") != "서버 통신 지연":
                        save_wrong_answer(exam_item)
            
            final_score = int((correct_count / total_questions) * 100)
            
            if final_score >= 60:
                st.success(f"🎉 **합격을 진심으로 축하합니다!** 총 점수: **{final_score}점** ({correct_count}/{total_questions} 맞춤)")
            else:
                st.error(f"⚠️ **아쉽지만 불합격입니다.** 틀린 문항을 복습해보세요! 총 점수: **{final_score}점** ({correct_count}/{total_questions} 맞춤)")
            
            st.info("💡 방금 틀린 새로운 문제들이 오답노트에 업데이트되었습니다.")
            
            st.markdown("---")
            if st.button("🔄 다음 세트(새로운 60문제) 무한 풀기 시작!", use_container_width=True, type="primary"):
                st.session_state.exam_set = None
                st.session_state.current_index = 0
                st.session_state.user_answers = {}
                st.session_state.exam_submitted = False
                st.rerun()

elif menu == "📝 내 오답노트 복습":
    wrong_list = load_wrong_answers()
