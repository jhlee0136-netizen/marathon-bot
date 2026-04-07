import requests
from bs4 import BeautifulSoup
import json
import os

# 환경 설정
URL = "http://marathon.pe.kr/index_calendar.html"
SB_URL = os.environ.get("SUPABASE_URL") + "/rest/v1/marathon_data"
SB_KEY = os.environ.get("SUPABASE_KEY")

def run():
    headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    # 사이트 접속
    res = requests.get(URL)
    res.encoding = 'euc-kr'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # ⚠️ 데이터가 들어있는 표(Table)를 더 정확하게 찾도록 수정했습니다.
    tables = soup.find_all('table', {'width': '600'})
    target_table = None
    for t in tables:
        if "대회명" in t.text:
            target_table = t
            break

    if not target_table:
        print("데이터 표를 찾지 못했습니다.")
        return

    rows = target_table.find_all('tr')[1:] # 제목 줄 제외
    
    results = []
    for row in rows:
        tds = row.find_all('td')
        if len(tds) < 5: continue
        
        try:
            name_tag = tds[1].find('a')
            if not name_tag: continue
            
            link = name_tag['href']
            no = link.split('no=')[1]
            name = name_tag.get_text(strip=True)
            date_raw = tds[0].get_text(strip=True)
            location = tds[2].get_text(strip=True)
            reg = tds[3].get_text(strip=True)
            dist = tds[4].get_text(strip=True)
            
            # 날짜 정리 (2026.04.03 -> 2026-4-3)
            pure_date = date_raw.split('(')[0].strip()
            date_parts = pure_date.split('.')
            dk = f"{int(date_parts[0])}-{int(date_parts[1])}-{int(date_parts[2])}"
            
            results.append({
                "no": no, "name": name, "date": date_raw,
                "location": location, "registration": reg,
                "distances": dist, "dateKey": dk
            })
        except Exception as e:
            continue

    # Supabase에 전송
    if results:
        r = requests.post(SB_URL, headers=headers, data=json.dumps(results))
        print(f"성공! {len(results)}개의 데이터를 보냈습니다.")
    else:
        print("수집된 데이터가 없습니다.")

if __name__ == "__main__":
    run()
