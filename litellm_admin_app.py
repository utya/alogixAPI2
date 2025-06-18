
import streamlit as st
import requests
import json

st.set_page_config(page_title="LiteLLM API Tester", layout="wide")

st.title("🧪 LiteLLM API Инструмент для управления пользователями и ключами")

# Ввод Base URL и токена
st.sidebar.header("🔐 Настройки подключения")
base_url = st.sidebar.text_input("Base URL", "url")
auth_token = st.sidebar.text_input("API Token", type="password")

headers = {"Authorization": f"Bearer {auth_token}"}

def display_response(response):
    st.code(f"Status: {response.status_code}", language="text")
    try:
        json_data = response.json()
        st.json(json_data)
    except:
        st.text(response.text)

# --- Tabs for different actions ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Проверить пользователя",
    "👤 Создать пользователя",
    "🔑 Ключи пользователя",
    "➕ Сгенерировать ключ",
    "🚫 Отключить ключ",
    "🗑 Удалить ключ"
])

with tab1:
    st.subheader("🔍 Проверка существования пользователя")
    user_id_check = st.text_input("User ID", key="check_user")
    if st.button("Проверить пользователя"):
        if user_id_check:
            resp = requests.get(f"{base_url}/user/info?user_id={user_id_check}", headers=headers)
            display_response(resp)

with tab2:
    st.subheader("👤 Создать нового пользователя")
    new_user_id = st.text_input("User ID", key="create_user_id")
    new_user_alias = st.text_input("User Alias", key="create_user_alias")
    max_budget = st.number_input("Максимальный бюджет", value=10.0)
    if st.button("Создать пользователя"):
        data = {
            "user_email": new_user_id,
            "user_id": new_user_id,
            "user_alias": new_user_alias,
            "user_role": "internal_user",
            "teams": ["46f41e55-1133-40e9-9687-bd8197f2d957"],
            "max_budget": max_budget,
            "budget_duration": "30d"
        }
        resp = requests.post(f"{base_url}/user/new", headers=headers, json=data)
        display_response(resp)

with tab3:
    st.subheader("🔑 Список ключей пользователя")
    key_user_id = st.text_input("User ID", key="list_keys_user")
    if st.button("Показать ключи"):
        if key_user_id:
            resp = requests.get(f"{base_url}/key/list?user_id={key_user_id}", headers=headers)
            display_response(resp)

with tab4:
    st.subheader("➕ Генерация нового ключа")
    key_user_id = st.text_input("User ID", key="gen_key_user")
    key_alias = st.text_input("Key Alias", value="default-key")
    key_budget = st.number_input("Бюджет ключа", value=5.0)
    if st.button("Создать ключ"):
        data = {
            "user_id": key_user_id,
            "key_alias": key_alias,
            "max_budget": key_budget
        }
        resp = requests.post(f"{base_url}/key/generate", headers=headers, json=data)
        display_response(resp)

with tab5:
    st.subheader("🚫 Отключить ключ")
    key_to_disable = st.text_input("Key ID", key="disable_key_id")
    if st.button("Отключить"):
        data = {"key": key_to_disable}
        resp = requests.patch(f"{base_url}/key/disable", headers=headers, json=data)
        display_response(resp)

with tab6:
    st.subheader("🗑 Удалить ключ")
    key_to_delete = st.text_input("Key ID", key="delete_key_id")
    if st.button("Удалить"):
        data = {"key": key_to_delete}
        resp = requests.post(f"{base_url}/key/delete", headers=headers, json=data)
        display_response(resp)
