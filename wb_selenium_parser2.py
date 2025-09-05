from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import csv
import datetime
import time

def get_wildberries_price_selenium(product_id):
    """Получаем цену товара с помощью Selenium"""
    url = f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx"
    
    try:
        # Настройки Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"🔍 Открываю страницу товара {product_id}...")
        driver.get(url)
        time.sleep(3)
        
        price = None
        
        # Поиск цены
        try:
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='priceBlockFinalPrice']"))
            )
            price = price_element.text.strip()
        except:
            pass
        
        if not price:
            try:
                price_elements = driver.find_elements(By.TAG_NAME, "ins")
                for element in price_elements:
                    if '₽' in element.text and any(char.isdigit() for char in element.text):
                        price = element.text.strip()
                        break
            except:
                pass
        
        driver.quit()
        
        return price if price else "Цена не найдена"
                
    except Exception as e:
        return f"Ошибка: {str(e)}"

def save_to_json(data, filename="prices.json"):
    """Сохраняет данные в JSON файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Данные сохранены в {filename}")
    except Exception as e:
        print(f"❌ Ошибка сохранения JSON: {e}")

def save_to_csv(data, filename="prices.csv"):
    """Сохраняет данные в CSV файл"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID товара', 'Цена', 'Дата проверки', 'Ссылка'])
            for item in data:
                writer.writerow([
                    item['product_id'],
                    item['price'],
                    item['date'],
                    item['url']
                ])
        print(f"✅ Данные сохранены в {filename}")
    except Exception as e:
        print(f"❌ Ошибка сохранения CSV: {e}")

def save_to_excel(data, filename="prices.xlsx"):
    """Сохраняет данные в Excel файл"""
    try:
        import pandas as pd
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        print(f"✅ Данные сохранены в {filename}")
    except ImportError:
        print("❌ Для сохранения в Excel установите pandas: pip install pandas")
    except Exception as e:
        print(f"❌ Ошибка сохранения Excel: {e}")

def main():
    """Основная функция"""
    print("=" * 60)
    print("           ПАРСЕР ЦЕН WILDBERRIES")
    print("=" * 60)
    
    # Массив ID товаров
    product_ids = [4143984,454254829,4143985,450899573,462230522]  # Добавьте нужные ID
    
    results = []
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for product_id in product_ids:
        print(f"\n📦 Обрабатываю товар ID: {product_id}")
        print(f"🌐 Ссылка: https://www.wildberries.ru/catalog/{product_id}/detail.aspx")
        
        price = get_wildberries_price_selenium(product_id)
        print(f"💰 Цена: {price}")
        
        # Сохраняем результат
        result = {
            'product_id': product_id,
            'price': price,
            'date': current_date,
            'url': f'https://www.wildberries.ru/catalog/{product_id}/detail.aspx'
        }
        results.append(result)
        
        print("-" * 60)
    
    # Сохраняем результаты в файлы
    if results:
        print("\n💾 Сохраняю результаты...")
        save_to_json(results, "wb_prices.json")
        save_to_csv(results, "wb_prices.csv")
        
        # Пытаемся сохранить в Excel если установлен pandas
        try:
            import pandas
            save_to_excel(results, "wb_prices.xlsx")
        except ImportError:
            print("ℹ️  Для сохранения в Excel установите: pip install pandas openpyxl")
    
    print(f"\n🎯 Готово! Обработано товаров: {len(results)}")

if __name__ == "__main__":
    main()