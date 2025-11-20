import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(page_title="재봉틀 챗봇", page_icon="🧵", layout="wide")

# 제목 및 설명
st.title("🧵 재봉틀 챗봇")

# secrets.toml에서 API 키 로드
try:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("❌ OPENAI_API_KEY가 설정되지 않았습니다. .streamlit/secrets.toml을 확인해주세요.")
    st.stop()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=openai_api_key)

# 기본 시스템 프롬프트 (재봉틀 전문 챗봇)
DEFAULT_SYSTEM_PROMPT = """당신은 친근하고 창의적인 재봉틀 전문 스타일리스트입니다.
사용자의 요구사항(예: 기술 수준, 용도, 선호하는 스타일, 시간 제약 등)을 이해하고,
그에 맞춰 만들 수 있는 작품을 추천합니다.

당신의 역할:
1. 사용자의 요구사항을 친근하게 묻기
2. 구체적이고 실현 가능한 프로젝트 추천
3. 각 프로젝트의 난이도, 필요한 시간, 재료 등 설명
4. 초보자부터 숙련자까지 모든 수준의 사람들을 위한 조언 제공
5. 창의적인 아이디어와 응용 방법 제시
6. 친근하고 격려하는 톤 유지

항상 한국어로 응답하며, 구체적이고 도움이 되는 조언을 제공합니다."""

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

# 시스템 프롬프트 수정 섹션
st.markdown("### 📝 시스템 프롬프트 커스터마이징")

col1, col2 = st.columns([4, 1])

with col1:
    custom_prompt = st.text_area(
        "시스템 프롬프트 수정",
        value=st.session_state.system_prompt,
        height=150,
        placeholder=DEFAULT_SYSTEM_PROMPT,
        label_visibility="collapsed"
    )

with col2:
    st.markdown("")  # 간격 조정
    if st.button("✅ 적용", use_container_width=True, key="apply_prompt"):
        st.session_state.system_prompt = custom_prompt
        st.success("프롬프트가 적용되었습니다!", icon="✨")
    
    if st.button("🔄 초기화", use_container_width=True, key="reset_prompt"):
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
        st.info("기본 프롬프트로 초기화되었습니다.", icon="🔁")

st.divider()
st.markdown("### 💬 챗봇")

# 채팅 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력 필드
if prompt := st.chat_input("원하는 작품이나 프로젝트에 대해 말씀해주세요..."):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # OpenAI API 호출 (gpt-4o-mini 모델 사용)
    messages_for_api = [{"role": "system", "content": st.session_state.system_prompt}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]
    
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_for_api,
        stream=True,
    )

    # 스트리밍으로 응답 표시
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    
    # 어시스턴트 메시지 저장
    st.session_state.messages.append({"role": "assistant", "content": response})
