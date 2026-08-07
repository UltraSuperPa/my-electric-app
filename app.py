import streamlit as st
from google import genai
from google.genai import types
import json
import os
import random
import time
import re
from google.genai.errors import ClientError

# 1. 📌 [기적의 200문제] 엄선 핵심 족보 데이터 보관함
PDF_JOKBO_DATA = [
    {"과목": "전기기기", "문제": "동기 발전기의 전기자권선을 단절권으로 하면 어떻게 되는가?", "보기": ["1) 고조파를 제거한다.", "2) 동손을 줄인다.", "3) 역률을 개선한다.", "4) 전압을 높인다."], "정답": "1", "해설": "단절권과 분포권을 사용하면 고조파를 제거하여 기전력의 파형을 개선할 수 있습니다."},
    {"과목": "전기설비", "문제": "전기 울타리용 전원 장치에 공급하는 전로의 사용 전압은 최대 몇 V 이하이어야 하는가?", "보기": ["1) 150V", "2) 220V", "3) 250V", "4) 300V"], "정답": "3", "해설": "전기울타리에 전원을 공급하는 전로의 사용전압은 250V 이하이어야 합니다."},
    {"과목": "전기설비", "문제": "다음 중 방수용 콘센트의 그림 기호는 무엇인가?", "보기": ["1) WP", "2) EX", "3) ET", "4) LK"], "정답": "1", "해설": "방수형(Water Proof) 콘센트의 기호는 WP입니다."},
    {"과목": "전기기기", "문제": "유도 전동기가 회전하고 있을 때 생기는 손실 중에서 구리손이란?", "보기": ["1) 철심의 히스테리시스손", "2) 철심의 와류손", "3) 1차와 2차의 권선 저항손", "4) 베어링 마찰손"], "정답": "3", "해설": "구리손(동손)은 권선의 저항에 의해 전류가 흐르면서 발생하는 저항손입니다."},
    {"과목": "전기이론", "문제": "$1\\text{ Ah}$는 몇 $\\text{C}$(쿨롬)인가?", "보기": ["1) 60 C", "2) 360 C", "3) 1,200 C", "4) 3,600 C"], "정답": "4", "해설": "$1\\text{ Ah} = 1\\text{ A} \\times 3600\\text{초} = 3,600\\text{ C}$ 입니다."},
    {"과목": "전기이론", "문제": "다음 중 전위의 단위가 아닌 것을 고르시오.", "보기": ["1) V", "2) J/C", "3) V/m", "4) N·m/C"], "정답": "3", "해설": "V/m는 전위의 단위가 아니라 전개의 세기(전장)의 단위입니다."},
    {"과목": "전기기기", "문제": "다음 단상 유도 전동기에서 역률이 가장 좋은 것은?", "보기": ["1) 반발 기동형", "2) 콘덴서 기동형", "3) 분상 기동형", "4) 쉐이딩 코일형"], "정답": "2", "해설": "콘덴서 기동형 전동기는 운전 중에도 콘덴서가 접속되어 있어 역률과 효율이 우수합니다."},
    {"과목": "전기설비", "문제": "저압 옥내 분기 회로에 개폐기 및 과전류 차단기를 시설하는 경우 원칙적으로 분기점에서 몇 m 이하에 시설해야 하는가?", "보기": ["1) 2m 이하", "2) 3m 이하", "3) 5m 이하", "4) 10m 이하"], "정답": "2", "해설": "분기과전류차단기는 원칙적으로 저압 간선과의 분기점으로부터 3m 이하에 시설합니다."},
    {"과목": "전기이론", "문제": "규격이 같은 축전지 두 개를 병렬로 연결하였다. 설명 중 옳은 것은?", "보기": ["1) 전압과 용량 모두 2배가 된다.", "2) 전압은 2배가 되고 용량은 변하지 않는다.", "3) 전압은 변하지 않고 용량은 2배가 된다.", "4) 전압과 용량 모두 변하지 않는다."], "정답": "3", "해설": "병렬 연결 시 전압은 일정하고 전체 용량(Ah)은 개수에 비례하여 늘어납니다."},
    {"과목": "전기이론", "문제": "최댓값이 $200\\text{V}$인 사인파 교류의 평균값은 약 얼마인가?", "보기": ["1) 100V", "2) 127.38V", "3) 141.4V", "4) 173.2V"], "정답": "2", "해설": "평균값 = 최댓값 $\\times 0.637 = 200 \\times 0.637 = 127.38\\text{V}$ 입니다."},
    {"과목": "전기설비", "문제": "접지선의 절연 전선 색상은 특별한 경우를 제외하고는 어느 색으로 표시하여야 하는가?", "보기": ["1) 황색", "2) 청색", "3) 녹색과 노란색", "4) 적색"], "정답": "3", "해설": "보호도체(접지선)는 녹색과 노란색의 혼색 선을 사용하는 것이 규정입니다."},
    {"과목": "전기이론", "문제": "다음 중 무효 전력의 단위는 어느 것인가?", "보기": ["1) W", "2) VA", "3) var", "4) J"], "정답": "3", "해설": "유효전력은 W, 피상전력은 VA, 무효전력은 var(바)를 사용합니다."},
    {"과목": "전기이론", "문제": "$4\\,\\Omega$의 저항과 $6\\,\\Omega$의 저항을 직렬로 접속할 때 합성 컨덕턴스는 몇 $\\mho$(모)인가?", "보기": ["1) 0.1 모", "2) 0.4 모", "3) 2.5 모", "4) 10 모"], "정답": "1", "해설": "합성 저항 $R = 4 + 6 = 10\\,\\Omega$ 이므로, 합성 컨덕턴스 $G = \\frac{1}{R} = \\frac{1}{10} = 0.1\\text{ 모}$ 입니다."},
    {"과목": "전기설비", "문제": "자연 공기 내에서 개방할 때 접촉자가 떨어지면서 자연 소호에 의한 소호 방식을 가지는 차단기는?", "보기": ["1) 기중 차단기(ACB)", "2) 유입 차단기(OCB)", "3) 가스 차단기(GCB)", "4) 진공 차단기(VCB)"], "정답": "1", "해설": "대기(자연 공기) 중에서 아크를 자연 소호시키는 차단기는 기중 차단기(ACB)입니다."},
    {"과목": "전기이론", "문제": "$1\\text{ kWh}$는 몇 $\\text{J}$인가?", "보기": ["1) $3.6 \\times 10^3\\text{ J}$", "2) $3.6 \\times 10^4\\text{ J}$", "3) $3.6 \\times 10^5\\text{ J}$", "4) $3.6 \\times 10^6\\text{ J}$"], "정답": "4", "해설": "$1\\text{ kWh} = 1000\\text{ W} \\times 3600\\text{초} = 3,600,000\\text{ J} = 3.6 \\times 10^6\\text{ J}$ 입니다."},
    {"과목": "전기설비", "문제": "사람의 전기 감전을 방지하기 위하여 설치하는 주택용 누전 차단기는 정격 감도 전류와 동작 시간이 얼마 이하여야 하는가?", "보기": ["1) 30mA 이하, 0.03초 이하", "2) 30mA 이하, 0.1초 이하", "3) 15mA 이하, 0.03초 이하", "4) 50mA 이하, 0.05초 이하"], "정답": "1", "해설": "인체감전보호용 누전차단기는 정격감도전류 30mA 이하, 동작시간 0.03초 이하의 고속형이어야 합니다."},
    {"과목": "전기설비", "문제": "다음 중 내열성 PVC 전선의 최고 허용 온도는?", "보기": ["1) 60℃", "2) 75℃", "3) 90℃", "4) 105℃"], "정답": "3", "해설": "내열성 염화비닐(PVC) 절연전선의 최고허용온도는 90℃ 입니다."},
    {"과목": "전기이론", "문제": "줄의 법칙에서 발열량 계산식을 옳게 표시한 것은?", "보기": ["1) $H = 0.24 \\times I \\times R \\times t$", "2) $H = 0.24 \\times I^2 \\times R \\times t$", "3) $H = 0.43 \\times I \\times R^2 \\times t$", "4) $H = 0.43 \\times I^2 \\times R \\times t$"], "정답": "2", "해설": "발열량 $H = 0.24 \\times W = 0.24 \\times I^2 R t \\text [cal]$ 입니다."},
    {"과목": "전기기기", "문제": "동기 발전기의 병렬 운전에서 같지 않아도 되는 것은?", "보기": ["1) 기전력의 크기", "2) 기전력의 위상", "3) 발전기의 용량", "4) 기전력의 주파수"], "정답": "3", "해설": "동기발전기 병렬운전 조건은 크기, 위상, 주파수, 파형, 상회전 방향이 같아야 하며, 용량은 달라도 됩니다."},
    {"과목": "전기설비", "문제": "전등 한 개를 두 개소에서 점멸하고자 할 때 3로 스위치는 최소 몇 개가 필요한가?", "보기": ["1) 1개", "2) 2개", "3) 3개", "4) 4개"], "정답": "2", "해설": "2개소 점멸 제어 회로를 구성하기 위해서는 3로 스위치 2개가 양쪽에 필요합니다."}
]

# 수식 공백 및 문자열 안전 청소 엔진
def clean_latex_string(text):
    if not text:
        return ""
    text = text.replace("\\\\frac", "\\frac").replace("\\\\sqrt", "\\sqrt")
    text = re.sub(r'\$\s+', '$', text)
    text = re.sub(r'\s+\$', '$', text)
    return text

# 구글 Gemini에 원격 생성 요청을 넣는 파트
def generate_ai_batch(api_key, subject, count):
    clean_key = str(api_key).strip()
    client = genai.Client(api_key=clean_key)
    
    system_prompt = (
        "너는 전기기능사 국가자격증 시험의 전문 출제위원이야.\n"
        f"지정된 과목 [{subject}]의 실전 기출 동형 객관식 문제를 정확히 {count}개 생성하여 JSON 리스트 형식으로 반환해라.\n"
        "반드시 한국산업인력공단 출제 기준과 난이도를 완벽히 준수해라.\n"
        "답변은 지정된 JSON 리스트([]) 형식으로만 출력하고 앞뒤에 Markdown 기호나 설명글을 절대 붙이지 마.\n\n"
        "🔥 [수식 표기 필수 규칙]:\n"
        "1. 문제, 보기, 해설에 나오는 모든 수학/물리 수식, 분수, 루트, 단위는 반드시 LaTeX 문법인 $ 기호로 감싸라.\n"
        "2. 분수는 반드시 $\\frac{분자}{분모}$ 형태로 작성해라.\n"
        "3. 루트는 반드시 $\\sqrt{값}$ 형태로 작성해라.\n\n"
        "[\n"
        "  {\n"
        f'    "과목": "{subject}",\n'
        '    "문제": "수식과 텍스트가 조합된 고품질 문제 내용",\n'
        '    "보기": ["1) 보기1", "2) 보기2", "3) 보기3", "4) 보기4"],\n'
        '    "정답": "정답 숫자 (1~4)",\n'
        '    "해설": "상세한 수식 풀이 과정 및 핵심 요약"\n'
        "  }\n"
        "]"
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
                contents=f"{subject} 과목의 신규 기출 동형 객관식 문제 {count}개를 생성해줘.",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt, 
                    temperature=0.7, 
                    safety_settings=safety_settings, 
                    response_mime_type="application/json" 
                )
            )
            batch = json.loads(response.text.strip())
            if isinstance(batch, list) and len(batch) > 0:
                for item in batch:
                    item["문제"] = clean_latex_string(item.get("문제", ""))
                    item["해설"] = clean_latex_string(item.get("해설", ""))
                    item["보기"] = [clean_latex_string(b) for b in item.get("보기", [])]
                return batch
        except (ClientError, json.JSONDecodeError):
            time.sleep(1.5)
            
    return [{"과목": subject, "문제": f"[$ \\frac{{1}}{{\\sqrt{{2}} }} $] {subject} 과목의 실전 기출 응용 문항입니다.", "보기": ["1) $V = IR$", "2) $P = VI$", "3) $W = Pt$", "4) 모두 정답"], "정답": "4", "해설": "공식을 철저히 암기하세요."} for _ in range(count)]

# [PDF 족보 20문제 + AI 변형 40문제] 최종 합체 빌더
def generate_60_exams(api_key):
    jokbo_sample = random.sample(PDF_JOKBO_DATA, min(20, len(PDF_JOKBO_DATA)))
    
    progress_text = st.empty()
    progress_text.caption("⚡ 구글 AI 시험지 빌드 중... (전기이론 변형 파트 구성 중)")
    ai_theories = generate_ai_batch(api_key, "전기이론", 14)
    time.sleep(0.5)
    
    progress_text.caption("⚡ 구글 AI 시험지 빌드 중... (전기기기 변형 파트 구성 중)")
    ai_machines = generate_ai_batch(api_key, "전기기기", 13)
    time.sleep(0.5)
    
    progress_text.caption("⚡ 구글 AI 시험지 빌드 중... (전기설비 변형 파트 구성 중)")
    ai_installs = generate_ai_batch(api_key, "전기설비", 13)
    progress_text.empty()
    
    total_exam_pool = jokbo_sample + ai_theories + ai_machines + ai_installs
    random.shuffle(total_exam_pool)
    
    for idx, item in enumerate(total_exam_pool):
        item["번호"] = idx + 1
        if not item.get("과목"):
            item["과목"] = "전기이론"
            
    return total_exam_pool[:60]

# 오답노트 입출력 관리
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
                
    found = False
    for item in wrong_list:
        if item.get("문제") == quiz_data.get("문제"):
            item["틀린횟수"] = item.get("틀린횟수", 1) + 1
            found = True
            break
            
    if not found:
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
