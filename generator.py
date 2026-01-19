import streamlit as st
import requests
import json
import time

# --- ЗАГРУЖАЕМ КЛЮЧИ ИЗ СЕКРЕТНОГО ХРАНИЛИЩА STREAMLIT ---
try:
    SECRET_KEY = st.secrets["SECRET_KEY"]
    FOLDER_ID = st.secrets["FOLDER_ID"]
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    GOOGLE_CX_ID = st.secrets["GOOGLE_CX_ID"]
except (KeyError, FileNotFoundError):
    # Это нужно, чтобы приложение не ломалось локально, если нет secrets-файла
    st.error("ОШИБКА: Не удалось загрузить API-ключи. Убедитесь, что они добавлены в Secrets в настройках Streamlit Cloud.")
    st.stop() # Останавливаем выполнение, если ключей нет

# --- СПЕЦИАЛИЗИРОВАННЫЕ ФУНКЦИИ (без изменений) ---
def make_yandex_request(system_prompt, user_prompt):
    prompt = {"modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite", "completionOptions": {"stream": False, "temperature": 0.6, "maxTokens": "1000"},"messages": [{"role": "system", "text": system_prompt}, {"role": "user", "text": user_prompt}]}
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {"Content-Type": "application/json", "Authorization": f"Api-Key {SECRET_KEY}"}
    try:
        response = requests.post(url, headers=headers, json=prompt)
        response.raise_for_status()
        return response.json()['result']['alternatives'][0]['message']['text'].strip()
    except Exception as e:
        st.error(f"Ошибка запроса к Яндексу: {e}")
        return None

def get_seo_title(product_name):
    prompt = "Напиши SEO-заголовок (80-100 символов) для товара. Только заголовок, без лишних слов."
    return make_yandex_request(prompt, product_name)
def get_description(product_name):
    prompt = "Напиши подробное продающее описание (400-500 символов) для товара, ориентированное на пользу для покупателя на маркетплейсе."
    return make_yandex_request(prompt, product_name)
def get_benefits(product_name):
    prompt = "Напиши 5 главных преимуществ товара. Каждый пункт с новой строки, без нумерации и знаков в начале."
    response = make_yandex_request(prompt, product_name)
    return response.split('\n') if response else []
def get_features(product_name):
    prompt = "Напиши 5-7 ключевых технических характеристик товара. Каждая характеристика с новой строки, без нумерации."
    response = make_yandex_request(prompt, product_name)
    return response.split('\n') if response else []

def get_image_from_google(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {'key': GOOGLE_API_KEY, 'cx': GOOGLE_CX_ID, 'q': query, 'searchType': 'image', 'num': 1, 'safe': 'high'}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get("items")
        if results:
            return results[0]['link']
    except Exception as e:
        st.error(f"Ошибка при поиске картинки в Google: {e}")
    return None

# --- НОВЫЙ, УЛУЧШЕННЫЙ ИНТЕРФЕЙС ---
st.set_page_config(page_title="Генератор карточек", layout="wide")

# 1. Чистый заголовок
st.title('🤖 Генератор карточек товаров')
st.write('Ваш ИИ-помощник для создания продающих описаний.')

# 2. Поле для ввода
product_name_input = st.text_input('Название товара', placeholder='Например: робот-пылесос с влажной уборкой', label_visibility="hidden")

# 3. Большая кнопка по центру
if st.button('Создать ✨', use_container_width=True, type="primary"):
    if product_name_input:
        col1, col2 = st.columns(2)
        
        with col2:
            with st.spinner('1/4: Придумываю SEO-название...'):
                seo_title = get_seo_title(product_name_input)
                st.subheader('SEO-название:')
                st.text_area("SEO-название", value=seo_title or "Не удалось сгенерировать", height=50, key="seo", label_visibility="hidden")
            time.sleep(1)
            with st.spinner('2/4: Пишу продающее описание...'):
                description = get_description(product_name_input)
                st.subheader('Описание товара:')
                st.text_area("Описание товара", value=description or "Не удалось сгенерировать", height=200, key="desc", label_visibility="hidden")
            time.sleep(1)
            with st.spinner('3/4: Выделяю преимущества...'):
                benefits = get_benefits(product_name_input)
                st.subheader('Ключевые преимущества:')
                for benefit in benefits: st.markdown(f"- {benefit}")
            time.sleep(1)
            with st.spinner('4/4: Собираю характеристики...'):
                features = get_features(product_name_input)
                st.subheader('Характеристики:')
                for feature in features: st.markdown(f"- {feature}")

        with col1:
            with st.spinner('Ищу картинку в Google...'):
                image_url = get_image_from_google(product_name_input)
            if image_url:
                st.image(image_url, caption=f"Пример из Google для: {product_name_input}")
            else:
                st.warning("Не удалось найти картинку.")
        
        st.success('🎉 Всё готово!')
    else:
        st.warning('Пожалуйста, введите название товара.')

# 4. Версия приложения в самом низу
st.caption("Версия 6.4")

