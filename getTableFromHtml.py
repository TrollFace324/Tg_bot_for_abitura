from bs4 import BeautifulSoup

def extract_applicants(html: str, program: str, contest_type: str):
    soup = BeautifulSoup(html, "html.parser")

    # ищем все шапки таблиц (с описанием конкурса)
    headers = soup.find_all("table", {"class": "supp table-header"})

    for header in headers:
        rows = header.find_all("tr")
        header_data = {row.find("th").get_text(strip=True): row.find("td").get_text(strip=True) for row in rows}

        # проверяем, совпадают ли условия
        if (header_data.get("Направление (образовательная программа)") == program and
            header_data.get("Вид конкурса") == contest_type):

            # берём следующую таблицу (с абитуриентами)
            applicants_table = header.find_next_sibling("table")
            applicants = []
            for tr in applicants_table.find_all("tr")[1:]:  # пропускаем заголовок
                tds = [td.get_text(strip=True, separator=" ") for td in tr.find_all("td")]
                applicants.append(tds)

            return applicants

    return []
