from bs4 import BeautifulSoup
from getHTMLsite import get_html_tables

user_id = "4032518"
user_tables = []
user_inf = []

html = get_html_tables()
soup = BeautifulSoup(html, "html.parser")


def get_tables() -> list[list]:
    def get_head_table(head_table) -> dict:
        table_data = {}

        for row in head_table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:  # проверяем, что есть обе ячейки
                key = th.get_text(strip=True)
                value = td.get_text(strip=True)
                table_data[key] = value
        
        return table_data
    
    def get_body_table(body_table) -> list[list]:
        rows = []

        for tr in body_table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cells:  # пропускаем пустые строки
                rows.append(cells)

        return rows
    
    result = []

    # Находим все таблицы
    tables = soup.find_all("table")

    for i in range(0, len(tables), 2):
        headAndBodyTable = []
        head_table = tables[i]
        body_table = tables[i+1]
        
        headAndBodyTable.append(get_head_table(head_table))
        headAndBodyTable.extend(get_body_table(body_table))

        result.append(headAndBodyTable)
        
    return result

def get_user_table(user_id: str, all_tables: list[list]):
    result = []

    for table in all_tables:
        for raw in table:
            if user_id in raw:
                result.append(table)
                break
    
    return result

def get_user_info(user_tables: list[list]):
    result = []

    for table in user_tables:
        for row in table:
            if row != table[0] and user_id == row[1]:
                result.append([int(row[2]), int(row[0]), table[0]["Направление (образовательная программа)"]])
    
    return sorted(result, key=lambda x: x[0])


for data in get_user_info(get_user_table(user_id, get_tables())):
    print(data)
