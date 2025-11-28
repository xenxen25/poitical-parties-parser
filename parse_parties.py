import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
## подглядела в нейронке так как предыдуший мой код не хотел ниче делать и я так и не особо понял, что меняют следующие 2 строки:
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def get_absolute_url(relative_url):
    """Преобразует относительную ссылку в абсолютную"""
    base_url = "https://minjust.gov.ru"
    if relative_url.startswith('/'):
        return urljoin(base_url, relative_url)
    return relative_url

def clean_url(url):
    """Очищает URL от лишних параметров и исправляет протокол"""
    if not url or url == 'None':
        return None
    
    clean_url = url.split('?')[0]
        
    if clean_url.startswith('http://'):
        clean_url = clean_url.replace('http://', 'https://')
    
    return clean_url

def extract_party_name(link_text):
    """Достает просто название партии из текста ссылки"""
    clean_text = ' '.join(link_text.split())
    
    if 'Всероссийская политическая партия' in clean_text:
        clean_text = clean_text.replace('Всероссийская политическая партия', '').strip()
            # Убираем лишние пробелы вокруг кавычек
    clean_text = clean_text.replace('&nbsp;', ' ').strip()
    
    return clean_text
def parse_political_parties():
    """Основная функция парсинга политических партий"""
    url = "https://minjust.gov.ru/ru/pages/politicheskie-partii/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    parties_data = []
    
    try:
        print("🔄 Загружаем страницу...")
        
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        
        
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        print("✅ Страница успешно загружена!")
        
        party_links = soup.select('li a')
        
        print(f"🔍 Найдено ссылок: {len(party_links)}")
        
        for link in party_links:
            href = link.get('href', '')
            link_text = link.get_text(strip=True)
            

            if '/documents/' in href and 'политическая партия' in link_text.lower():
                party_name = extract_party_name(link_text)
                
                absolute_url = get_absolute_url(href)
                clean_doc_url = clean_url(absolute_url)
                

                party_data = {
                    "name": party_name,
                    "doc_url": clean_doc_url
                }
                
                parties_data.append(party_data)
                print(f"✅ Найдена партия: {party_name}")
        
        print(f"📊 Итого найдено партий: {len(parties_data)}")
        
        return parties_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при загрузке страницы: {e}")
        return []

def main():
    """Главный деф для проека"""
    print("🚀 Запуск парсера политических партий...")
    
    parties = parse_political_parties()
    
    if parties:
        print(f"✅ Успешно извлечено {len(parties)} партий")        

        with open('parties.json', 'w', encoding='utf-8') as f:
            json.dump(parties, f, ensure_ascii=False, indent=2)
        print("💾 Данные сохранены в parties.json")
        
        print("\n📋 Результат:")
        for i, party in enumerate(parties, 1):
            print(f"{i}. {party['name']}")
            print(f"   Документ: {party['doc_url']}\n")
    else:
        print("❌ Не удалось извлечь данные о партиях")

if __name__ == "__main__":
    main()