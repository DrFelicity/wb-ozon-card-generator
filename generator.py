import streamlit as st
import requests
import json
import time
import streamlit.components.v1 as components # <<< ИМПОРТИРУЕМ КОМПОНЕНТЫ

# --- ЗАГРУЖАЕМ КЛЮЧИ ИЗ СЕКРЕТНОГО ХРАНИЛИЩА STREAMLIT ---
try:
    SECRET_KEY = st.secrets["SECRET_KEY"]
    FOLDER_ID = st.secrets["FOLDER_ID"]
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    GOOGLE_CX_ID = st.secrets["GOOGLE_CX_ID"]
    YANDEX_METRIKA_COUNTER = st.secrets["YANDEX_METRIKA_COUNTER"]
except (KeyError, FileNotFoundError):
    st.error("ОШИБКА: Не удалось загрузить API-ключи. Убедитесь, что они добавлены в Secrets.")
    st.stop()

# --- СПЕЦИАЛИЗИРОВАННЫЕ ФУНКЦИИ (без изменений) ---
# ... (все ваши функции get_seo_title, get_description и т.д. остаются здесь) ...
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
        if results: return results[0]['link']
    except Exception as e: st.error(f"Ошибка при поиске картинки в Google: {e}")
    return None

# --- ИНТЕРФЕЙС (с вашими улучшениями) ---
st.set_page_config(page_title="Генератор карточек", layout="wide")

# --- ВСТАВЛЯЕМ КОД МЕТРИКИ ВРУЧНУЮ ---
components.html(f"""
<!-- Yandex.Metrika counter -->
<script type="text/javascript" >
   (function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
   m[i].l=1*new Date();
   for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
   k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})
   (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");

   ym({YANDEX_METRIKA_COUNTER}, "init", {{
        clickmap:true,
        trackLinks:true,
        accurateTrackBounce:true,
        webvisor:true
   }});
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/{YANDEX_METRIKA_COUNTER}" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->
""", height=0, width=0)
# ---------------------------------------------

st.title('🤖 Генератор карточек товаров')
st.write('Ваш ИИ-помощник для создания продающих описаний.')
# ... (остальной интерфейс без изменений) ...
product_name_input = st.text_input('Название товара', placeholder='Например: робот-пылесос с влажной уборкой', label_visibility="hidden")

if st.button('Создать ✨', use_container_width=True, type="primary"):
    if product_name_input:
        col1, col2 = st.columns(2)
        with col2:
            # ... (логика генерации)
            pass
        with col1:
            # ... (логика картинки)
            pass
        st.success('🎉 Всё готово!')
    else:
        st.warning('Пожалуйста, введите название товара.')

st.caption("v6.6")

