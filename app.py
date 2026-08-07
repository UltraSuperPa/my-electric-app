import streamlit as st
import json
import os
import random


# =========================
# 기본 설정
# =========================

st.set_page_config(
    page_title="전기기능사 CBT",
    page_icon="⚡",
    layout="centered"
)


# =========================
# 화면 크게 설정
# =========================

st.markdown(
    """
    <style>
    .stMarkdown p {
        font-size: 22px;
        line-height: 1.8;
    }

    .stRadio label {
        font-size: 20px !important;
        padding: 10px;
    }

    button {
        font-size: 18px !important;
    }

    h1 {
        font-size: 38px !important;
    }

    h2 {
        font-size: 30px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# 문제 데이터 불러오기
# =========================

QUESTION_FILE = "questions.json"
WRONG_FILE = "wrong_answers.json"


def load_questions():

    if os.path.exists(QUESTION_FILE):

        with open(
            QUESTION_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    return []



# =========================
# 오답 저장
# =========================

def load_wrong():

    if os.path.exists(WRONG_FILE):

        with open(
            WRONG_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            try:
                return json.load(f)

            except:
                return []

    return []



def save_wrong(question):

    wrong = load_wrong()

    exists = False

    for item in wrong:

        if item["문제"] == question["문제"]:

            item["틀린횟수"] = item.get(
                "틀린횟수",
                1
            ) + 1

            exists = True


    if not exists:

        question["틀린횟수"] = 1
        wrong.append(question)


    with open(
        WRONG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            wrong,
            f,
            ensure_ascii=False,
            indent=4
        )



questions = load_questions()


# =========================
# 세션 저장
# =========================

if "exam" not in st.session_state:
    st.session_state.exam = []

if "index" not in st.session_state:
    st.session_state.index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "checked" not in st.session_state:
    st.session_state.checked = False

if "answers" not in st.session_state:
    st.session_state.answers = {}
# =========================
# 메인 화면
# =========================

st.title("⚡ 전기기능사 스마트 CBT")


menu = st.radio(
    "메뉴 선택",
    [
        "🎯 실전 모의고사",
        "📝 오답노트 복습"
    ],
    horizontal=True
)


st.divider()


# =========================
# 실전 모의고사
# =========================

if menu == "🎯 실전 모의고사":


    if not st.session_state.exam:


        st.subheader("60문항 실전 모의고사")

        st.info(
            "문제를 풀고 답을 선택하면 바로 채점 및 해설이 표시됩니다."
        )


        if st.button(
            "🚀 시험 시작",
            use_container_width=True
        ):


            if len(questions) == 0:

                st.error(
                    "questions.json 파일에 문제가 없습니다."
                )

            else:

                count = min(
                    60,
                    len(questions)
                )

                st.session_state.exam = random.sample(
                    questions,
                    count
                )

                st.session_state.index = 0
                st.session_state.score = 0
                st.session_state.checked = False
                st.session_state.answers = {}

                st.rerun()



    else:


        quiz = st.session_state.exam[
            st.session_state.index
        ]


        number = st.session_state.index + 1


        st.progress(
            number / len(st.session_state.exam)
        )


        st.subheader(
            f"문제 {number} / {len(st.session_state.exam)}"
        )


        st.write(
            f"### [{quiz['과목']}]"
        )


        st.markdown(
            f"## {quiz['문제']}"
        )



        answer = st.radio(
            "정답 선택",
            quiz["보기"],
            key=f"answer_{number}"
        )



        # =========================
        # 즉시 채점
        # =========================


        if st.button(
            "✅ 정답 확인",
            use_container_width=True
        ):


            selected = answer[0]


            st.session_state.checked = True


            if selected == quiz["정답"]:


                st.session_state.score += 1


                st.success(
                    "🎉 정답입니다!"
                )


            else:


                st.error(
                    f"❌ 오답입니다. 정답은 {quiz['정답']}번 입니다."
                )


                save_wrong(
                    quiz
                )


            st.info(
                f"📖 해설\n\n{quiz['해설']}"
            )



        # 다음 문제 버튼


        if st.session_state.checked:


            if st.session_state.index < len(st.session_state.exam)-1:


                if st.button(
                    "다음 문제 ➡",
                    use_container_width=True
                ):


                    st.session_state.index += 1
                    st.session_state.checked = False

                    st.rerun()


            else:


                if st.button(
                    "🏁 결과 보기",
                    use_container_width=True
                ):

                    st.success(
                        f"시험 종료! 점수 : {st.session_state.score} / {len(st.session_state.exam)}"
                    )

                    rate = round(
                        st.session_state.score /
                        len(st.session_state.exam)
                        * 100,
                        1
                    )


                    st.info(
                        f"정답률 : {rate}%"
                    )

                    if rate >= 60:

                        st.balloons()

                        st.success(
                            "🎉 합격권입니다!"
                        )

                    else:

                        st.warning(
                            "조금 더 복습이 필요합니다."
                        ) 
# =========================
# 오답노트 복습
# =========================

elif menu == "📝 오답노트 복습":


    wrong = load_wrong()


    st.subheader("📝 내 오답노트")


    if not wrong:


        st.info(
            "아직 틀린 문제가 없습니다."
        )


    else:


        st.write(
            f"저장된 오답 : {len(wrong)}개"
        )


        for i, item in enumerate(wrong):


            with st.expander(
                f"{i+1}. {item['문제']}"
            ):


                st.write(
                    f"📌 과목 : {item['과목']}"
                )


                st.write(
                    "보기"
                )


                for choice in item["보기"]:

                    st.write(choice)


                st.success(
                    f"정답 : {item['정답']}번"
                )


                st.info(
                    f"해설 : {item['해설']}"
                )



# =========================
# 초기 안내
# =========================

st.sidebar.divider()

st.sidebar.write(
    "⚡ 전기기능사 CBT 학습 앱"
)

st.sidebar.write(
    "문제 선택 → 즉시 채점 → 오답 저장"
)
