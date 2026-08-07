import streamlit as st
import json
import os
import random


# ==============================
# 페이지 설정
# ==============================

st.set_page_config(
    page_title="전기기능사 CBT",
    page_icon="⚡",
    layout="centered"
)


# ==============================
# 화면 디자인
# ==============================

st.markdown(
    """
    <style>

    .stMarkdown p {
        font-size: 22px;
        line-height: 1.8;
    }

    .stRadio label {
        font-size: 20px !important;
        padding: 8px;
    }

    div[data-testid="stButton"] button {
        font-size: 18px;
        height: 3em;
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



# ==============================
# 파일 위치
# ==============================

QUESTION_FILE = "questions.json"

WRONG_FILE = "wrong_answers.json"



# ==============================
# 문제 불러오기
# ==============================

def load_questions():

    if not os.path.exists(QUESTION_FILE):
        return []

    with open(
        QUESTION_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)



# ==============================
# 오답 불러오기
# ==============================

def load_wrong_answers():

    if not os.path.exists(WRONG_FILE):

        return []


    with open(
        WRONG_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        try:

            data = json.load(f)

            if isinstance(data, list):
                return data

        except:

            pass


    return []



# ==============================
# 오답 저장
# ==============================

def save_wrong_answer(question):

    wrong = load_wrong_answers()


    for item in wrong:

        if item.get("문제") == question.get("문제"):

            item["틀린횟수"] = item.get(
                "틀린횟수",
                1
            ) + 1

            break

    else:

        new_item = question.copy()

        new_item["틀린횟수"] = 1

        wrong.append(new_item)



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



# ==============================
# 데이터 로드
# ==============================

questions = load_questions()



# ==============================
# 세션 상태
# ==============================

if "exam" not in st.session_state:
    st.session_state.exam = []


if "index" not in st.session_state:
    st.session_state.index = 0


if "score" not in st.session_state:
    st.session_state.score = 0


if "checked" not in st.session_state:
    st.session_state.checked = False


if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = ""
# ==============================
# 메인 화면
# ==============================

st.title("⚡ 전기기능사 스마트 CBT")


# ==============================
# 메뉴
# ==============================

menu = st.radio(
    "학습 모드 선택",
    [
        "🎯 실전 모의고사",
        "📝 오답노트 복습"
    ],
    horizontal=True
)


st.divider()



# ==============================
# 실전 모의고사
# ==============================

if menu == "🎯 실전 모의고사":


    if len(questions) == 0:

        st.error(
            "questions.json 파일에 문제가 없습니다."
        )


    else:


        # 시험 시작 전

        if len(st.session_state.exam) == 0:


            st.subheader(
                "📚 전기기능사 실전 CBT"
            )


            st.info(
                f"현재 등록 문제 : {len(questions)}문제"
            )


            # 과목 목록

            subjects = list(
                set(
                    q.get(
                        "과목",
                        "기타"
                    )
                    for q in questions
                )
            )


            subjects.insert(
                0,
                "전체"
            )


            selected_subject = st.selectbox(
                "출제 범위 선택",
                subjects
            )



            # 출제 문제 수

            count = st.selectbox(
                "문제 수",
                [
                    20,
                    40,
                    60
                ],
                index=2
            )



            if st.button(
                "🚀 시험 시작",
                use_container_width=True,
                type="primary"
            ):


                if selected_subject == "전체":

                    pool = questions


                else:

                    pool = [

                        q for q in questions

                        if q.get(
                            "과목"
                        ) == selected_subject

                    ]



                if len(pool) < count:

                    count = len(pool)



                st.session_state.exam = random.sample(
                    pool,
                    count
                )


                st.session_state.index = 0

                st.session_state.score = 0

                st.session_state.checked = False

                st.session_state.selected_answer = ""


                st.rerun()



        # 시험 진행 중

        else:


            quiz = st.session_state.exam[
                st.session_state.index
            ]


            current = (
                st.session_state.index + 1
            )


            total = len(
                st.session_state.exam
            )


            st.progress(
                current / total
            )


            st.subheader(
                f"문제 {current} / {total}"
            )


            st.caption(
                quiz.get(
                    "과목",
                    ""
                )
            )


            st.markdown(
                f"## {quiz['문제']}"
            )



            answer = st.radio(
                "정답 선택",
                quiz["보기"],
                key=f"answer_{current}"
            )



            st.session_state.selected_answer = answer



            if st.button(
                "✅ 정답 확인",
                use_container_width=True
            ):

                st.session_state.checked = True
            # ==============================
            # 채점 및 해설
            # ==============================

            if st.session_state.checked:


                selected = (
                    st.session_state.selected_answer[0]
                )


                correct = quiz["정답"]



                if selected == correct:


                    st.success(
                        "🎉 정답입니다!"
                    )


                    # 중복 클릭 방지
                    if "counted" not in st.session_state:

                        st.session_state.counted = True

                        st.session_state.score += 1



                else:


                    st.error(
                        f"❌ 오답입니다. 정답은 {correct}번 입니다."
                    )


                    save_wrong_answer(
                        quiz
                    )


                st.info(
                    f"""
                    📖 해설

                    {quiz.get('해설','해설 없음')}
                    """
                )



                st.divider()



                # 다음 문제

                if st.session_state.index < len(
                    st.session_state.exam
                ) - 1:



                    if st.button(
                        "➡ 다음 문제",
                        use_container_width=True
                    ):


                        st.session_state.index += 1

                        st.session_state.checked = False

                        st.session_state.selected_answer = ""

                        if "counted" in st.session_state:

                            del st.session_state.counted


                        st.rerun()



                else:



                    if st.button(
                        "🏁 결과 확인",
                        use_container_width=True
                    ):


                        total = len(
                            st.session_state.exam
                        )


                        score = st.session_state.score



                        rate = round(
                            score / total * 100,
                            1
                        )


                        st.balloons()



                        st.success(
                            f"""
                            시험 종료

                            점수 : {score} / {total}

                            정답률 : {rate}%
                            """
                        )



                        if rate >= 60:

                            st.success(
                                "🎉 합격권입니다!"
                            )

                        else:

                            st.warning(
                                "📚 복습이 필요합니다."
                            )


                        # 초기화 버튼

                        if st.button(
                            "🔄 다시 시험보기"
                        ):

                            st.session_state.exam = []

                            st.session_state.index = 0

                            st.session_state.score = 0

                            st.session_state.checked = False

                            st.rerun()
                            # ==============================
# 오답노트 복습
# ==============================

elif menu == "📝 오답노트 복습":


    st.subheader(
        "📝 내 오답노트"
    )


    wrong_list = load_wrong_answers()



    if len(wrong_list) == 0:


        st.info(
            "아직 저장된 오답이 없습니다."
        )



    else:



        st.success(
            f"저장된 오답 : {len(wrong_list)}문제"
        )



        # 틀린 횟수 많은 순서

        wrong_list = sorted(
            wrong_list,
            key=lambda x: x.get(
                "틀린횟수",
                1
            ),
            reverse=True
        )



        for idx, item in enumerate(
            wrong_list,
            start=1
        ):



            with st.expander(
                f"{idx}. {item['문제']} (틀린 횟수 : {item.get('틀린횟수',1)}회)"
            ):


                st.write(
                    f"📌 과목 : {item.get('과목','')}"
                )


                st.write(
                    "보기"
                )


                for choice in item["보기"]:

                    st.write(
                        choice
                    )


                st.success(
                    f"정답 : {item['정답']}번"
                )


                st.info(
                    f"해설 : {item.get('해설','')}"
                )




# ==============================
# 사이드바
# ==============================

st.sidebar.divider()


st.sidebar.title(
    "⚡ 전기기능사 CBT"
)


st.sidebar.write(
    "기출 중심 학습 시스템"
)


st.sidebar.write(
    """
    기능

    ✅ 실전 모의고사

    ✅ 즉시 채점

    ✅ 해설 제공

    ✅ 오답 저장

    ✅ 오답 복습
    """
)
