import re

def NewlineJoin(*strings) -> str:
    return '\n'.join(strings)

def EnumerateStrings(*strings) -> list[str]:
    return [f'{i+1}. {s}' for i, s in enumerate(strings)]


yadisk_patterns = [
    r'https?://(?:www\.)?yadi\.sk/d/[\w-]+',
    r'https?://(?:www\.)?disk\.yandex\.\w{2,3}/d/[\w-]+',
    r'https?://(?:www\.)?disk\.yandex\.\w{2,3}/client/disk[\w-]*',
    r'https?://(?:www\.)?yadi\.sk/i/[\w-]+',
    r'https?://(?:www\.)?disk\.yandex\.\w{2,3}/i/[\w-]+',
]

def IsCorrectReportUrl(url: str) -> bool:
    """Проверяет, является ли строка корректной ссылкой на Яндекс.Диск.
    
    Args:
        url (str): Строка для проверки.
        
    Returns:
        bool: True если ссылка корректна, иначе False.
    """

    
    for pattern in yadisk_patterns:
        if re.fullmatch(pattern, url):
            return True
            
    return False