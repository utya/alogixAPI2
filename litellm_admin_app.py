import streamlit as st
import requests
import os
import time
from openai import OpenAI, AuthenticationError, OpenAIError
from dotenv import load_dotenv

# --- Загрузка переменных ---
load_dotenv()

# --- Получение из .env ---
default_base_url = os.getenv("BASE_URL", "")
default_api_token = os.getenv("API_TOKEN", "")
default_chat_model = os.getenv("MODEL_NAME", "aLogix Pro 2")

default_balance_url = os.getenv("BALANCE_URL", "")
default_login_url = os.getenv("LOGIN_URL", "")
default_login_user = os.getenv("LOGIN_USER", "")
default_login_pass = os.getenv("LOGIN_PASS", "")

# --- Streamlit config ---
st.set_page_config(page_title="LiteLLM + Chat + Balance", layout="wide")
st.title("🧪 Управление LiteLLM + 💬 Чат с ботом")

# --- Session State Init ---
if "balance" not in st.session_state:
    st.session_state.balance = "💰 —"
if "balance_token" not in st.session_state:
    st.session_state.balance_token = None

balance_placeholder = st.empty()

def show_balance():
    balance_placeholder.markdown(
        f"<div style='text-align:right; font-size:20px;'>{st.session_state.balance}</div>",
        unsafe_allow_html=True
    )

# --- Функция: запрос баланса ---
def fetch_balance():
    try:
        token = st.session_state.get("balance_token", "")
        if not token.lower().startswith("bearer "):
            token = f"Bearer {token}"

        headers = {
            "Authorization": token,
            "Accept": "*/*",
            "User-Agent": "PostmanRuntime/7.43.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        print("[fetch_balance] REQUEST HEADERS:", headers)
        print("[fetch_balance] REQUEST URL:", st.session_state.get("balance_url", ""))
        resp = requests.get(st.session_state.get("balance_url", ""), headers=headers)
        print("[fetch_balance] RAW RESPONSE:", resp.text)
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.balance = f"💰 {data.get('balance', {}).get('formatted', '—')}"
        else:
            st.error(f"Ошибка при получении баланса: {resp.status_code} - {resp.text}")
            st.session_state.balance = "💰 ошибка"
    except Exception as e:
        st.exception(e)
        st.session_state.balance = "💰 ❌"

# --- Сайдбар: API и чат ---
st.sidebar.header("🔐 API для OpenAI")
base_url = st.sidebar.text_input("Base URL", value=default_base_url)
api_token = st.sidebar.text_input("API Token", type="password", value=default_api_token)
chat_model = st.sidebar.text_input("Chat Model", value=default_chat_model)

# --- Сайдбар: Авторизация баланса ---
st.sidebar.markdown("---")
st.sidebar.header("🔐 Авторизация баланса")
balance_url = st.sidebar.text_input("Balance URL", value=default_balance_url)
login_url = st.sidebar.text_input("Login URL", value=default_login_url)
login_user = st.sidebar.text_input("Логин", value=default_login_user)
login_pass = st.sidebar.text_input("Пароль", type="password", value=default_login_pass)

# Сохраняем в session_state
st.session_state.balance_url = balance_url
st.session_state.login_url = login_url

if st.sidebar.button("🔓 Войти и получить токен"):
    try:
        resp = requests.post(login_url, data={"username": login_user, "password": login_pass})
        if resp.status_code == 200:
            token = (
                resp.json().get("accessToken")
                or resp.json().get("token")
                or resp.json().get("data", {}).get("token")
                or resp.json().get("data", {}).get("access_token")
            )
            if token:
                st.success("✅ Токен получен")
                st.session_state.balance_token = token
                fetch_balance()
                show_balance()
            else:
                st.error("❌ Токен не найден в ответе")
        else:
            st.error(f"Ошибка авторизации: {resp.status_code}")
    except Exception as e:
        st.error(f"⚠️ Ошибка при авторизации: {e}")

# --- Отображение баланса вверху справа ---
show_balance()

# --- Tabs ---
tab1, tab2, tab3, tab_chat = st.tabs([
    "🔍 Проверить пользователя",
    "👤 Создать пользователя",
    "🔑 Ключи пользователя",
    "💬 Чат с ботом"
])

# --- Проверка пользователя ---
with tab1:
    st.subheader("🔍 Проверка пользователя")
    user_id_check = st.text_input("User ID", key="check_user")
    if st.button("Проверить пользователя"):
        try:
            headers = {"Authorization": f"Bearer {api_token}"}
            resp = requests.get(f"{base_url}/user/info?user_id={user_id_check}", headers=headers)
            st.code(f"Status: {resp.status_code}")
            st.json(resp.json())
        except Exception as e:
            st.error(f"Ошибка: {e}")

# --- Создание пользователя ---
with tab2:
    st.subheader("👤 Создать пользователя")
    new_user_id = st.text_input("User ID", key="create_user_id")
    new_user_alias = st.text_input("User Alias", key="create_user_alias")
    max_budget = st.number_input("Максимальный бюджет", value=10.0)
    if st.button("Создать пользователя"):
        try:
            data = {
                "user_email": new_user_id,
                "user_id": new_user_id,
                "user_alias": new_user_alias,
                "user_role": "internal_user",
                "teams": ["46f41e55-1133-40e9-9687-bd8197f2d957"],
                "max_budget": max_budget,
                "budget_duration": "30d"
            }
            headers = {"Authorization": f"Bearer {api_token}"}
            resp = requests.post(f"{base_url}/user/new", headers=headers, json=data)
            st.code(f"Status: {resp.status_code}")
            st.json(resp.json())
        except Exception as e:
            st.error(f"Ошибка: {e}")

# --- Ключи пользователя ---
with tab3:
    st.subheader("🔑 Ключи пользователя")
    key_user_id = st.text_input("User ID", key="list_keys_user")
    if st.button("Показать ключи"):
        try:
            headers = {"Authorization": f"Bearer {api_token}"}
            resp = requests.get(f"{base_url}/key/list?user_id={key_user_id}", headers=headers)
            st.code(f"Status: {resp.status_code}")
            st.json(resp.json())
        except Exception as e:
            st.error(f"Ошибка: {e}")

# --- Чат с ботом ---
with tab_chat:
    st.subheader("💬 Чат с ботом")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_message = st.text_input("Введите сообщение", key="chat_input")

    if st.button("📨 Отправить сообщение"):
        if user_message and api_token and base_url:
            try:
                client = OpenAI(api_key=api_token, base_url=base_url)
                with st.spinner("Бот думает..."):
                    response = client.chat.completions.create(
                        model=chat_model,
                        messages=[{"role": "user", "content": user_message}],
                        max_tokens=500
                    )
                    reply = response.choices[0].message.content
                    st.session_state.chat_history.append(("👤", user_message))
                    st.session_state.chat_history.append(("🤖", reply))

                # Обновление баланса через 3 секунды
                with st.spinner("Обновляем баланс..."):
                    time.sleep(3)
                    fetch_balance()
                    show_balance()

            except AuthenticationError as e:
                st.error(f"❌ Ошибка авторизации: {e}")
            except OpenAIError as e:
                st.error(f"⚠️ Ошибка OpenAI API: {e}")
            except Exception as e:
                st.error(f"❗ Неизвестная ошибка: {e}")

    for sender, msg in st.session_state.chat_history:
        st.markdown(f"**{sender}**: {msg}")

# --- Первичный запрос баланса (если токен есть) ---
if st.session_state.get("balance_token") and st.session_state.get("balance_url"):
    fetch_balance()
    show_balance()