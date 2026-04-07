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
    
    # ⚠️ 모든 tr 태그 중에서 'no=' 링크가 있는 행을 바로 찾습니다.
    rows = soup.find_all('tr')
    
    results = []
    for row in rows:
        tds = row.find_all('td')
        # 한 줄에 데이터 칸이 보통 5~6개 있습니다.
        if len(tds) < 5: continue
        
        name_tag = tds[1].find('a')
        # 링크에 'no=' 이 들어있는 행이 진짜 대회 정보입니다.
        if name_tag and 'no=' in name_tag.get('href', ''):
            try:
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
            except:
                continue

    # Supabase에 전송
    if results:
        # 중복 방지를 위해 데이터를 하나씩 보내지 않고 뭉쳐서 보냅니다.
        r = requests.post(SB_URL, headers=headers, data=json.dumps(results))
        print(f"성공! {len(results)}개의 데이터를 보냈습니다.")
    else:
        print("데이터를 찾지 못했습니다. 사이트 구조를 다시 확인해야 합니다.")

if __name__ == "__main__":
    run()
