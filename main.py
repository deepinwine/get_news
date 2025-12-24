# 安装依赖（只需运行一次）
# !pip install selenium pandas openpyxl webdriver-manager

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# ------------------ 配置 Chrome 浏览器 ------------------
options = Options()
options.add_argument("--headless=new")   # 无界面模式
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# ------------------ 搜索页面 URL ------------------
start_url = "https://www.ifnews.com/searchColumn.html?search=XXXXXXX"
driver.get(start_url)
time.sleep(3)  # 等待页面加载

results = []
current_page = 1

while True:
    print(f"抓取第 {current_page} 页...")
    
    # ------------------ 抓取文章列表 ------------------
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a"))
    )
    
    items = driver.find_elements(By.CSS_SELECTOR, "a")
    for a in items:
        href = a.get_attribute("href")
        if href and "news.html?aid=" in href:
            title = a.text.strip()
            results.append({"title": title, "link": href})
    
    # ------------------ 翻页 ------------------
    try:
        # 获取所有数字页码 li
        page_items = driver.find_elements(By.CSS_SELECTOR, "li.number")
        next_page_li = None
        for li in page_items:
            if li.text.strip() == str(current_page + 1):
                next_page_li = li
                break
        
        if next_page_li:
            driver.execute_script("arguments[0].scrollIntoView();", next_page_li)
            next_page_li.click()
            current_page += 1
            time.sleep(2)  # 等待新一页加载
        else:
            print("已到最后一页")
            break
    except Exception as e:
        print("翻页失败，结束抓取", e)
        break

driver.quit()

# ------------------ 导出 Excel ------------------
df = pd.DataFrame(results)
df.drop_duplicates(subset=["link"], inplace=True)
df.to_excel("ifnews_search_results_all_pages.xlsx", index=False)
print(f"抓取完成，总文章数：{len(df)}，已导出 Excel。")
