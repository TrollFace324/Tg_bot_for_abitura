import requests

URL = "https://urfu.ru/api/ratings/info/90/1268"
SAVE_URL = "localSite.html"
ENCODING = "utf-8"

def get_html_tables() -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(URL, headers=headers)

        data = resp.json()  # сразу распарсим JSON
        relative_url = data["url"]  # достаём относительный путь
        full_url = "https://urfu.ru" + relative_url

        # Теперь получаем сам HTML
        resp_html = requests.get(full_url, headers=headers)

        # Явно указываем правильную кодировку
        resp_html.encoding = ENCODING
        html_text = resp_html.text
    except:
        # Получаем сам HTML
        html_text = "".join(open(SAVE_URL, "r", encoding=ENCODING).readlines())

    return html_text