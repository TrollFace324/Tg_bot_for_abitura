from pathlib import Path
from typing import Union

def save_html(html: str,
              path: Union[str, Path] = "output.html",
              encoding: str = "utf-8",
              exist_ok: bool = False) -> Path:
    """
    Сохраняет HTML-код в файл.

    :param html: HTML-код в виде строки.
    :param path: Путь к файлу (с .html). Папки будут созданы автоматически.
    :param encoding: Кодировка файла (по умолчанию UTF-8).
    :param exist_ok: Если False и файл уже существует — будет исключение FileExistsError.
    :return: Полный путь к созданному/перезаписанному файлу (Path).
    """
    p = Path(path)

    # Если расширение не указано — добавим .html
    if p.suffix == "":
        p = p.with_suffix(".html")

    # Создадим родительские директории при необходимости
    if p.parent and not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)

    if p.exists() and not exist_ok:
        raise FileExistsError(f"Файл уже существует: {p}")

    # Гарантируем перевод строки в конце файла (полезно для некоторых инструментов)
    text = html if html.endswith("\n") else html + "\n"

    # Запишем в файл
    p.write_text(text, encoding=encoding, newline="\n")
    return p
