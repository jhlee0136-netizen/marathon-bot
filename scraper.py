import requests
from bs4 import BeautifulSoup
import json
import os

# 환경 설정 (GitHub에서 설정한 열쇠 사용)
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
    
    res = requests.get(URL)
    res.encoding = 'euc-kr'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    rows = soup.select('table[width="600"] tr')[1:]
    
    results = []
    for row in rows:
        tds = row.find_all('td')
        if len(tds) < 6: continue
        try:
            link = tds[1].find('a')['href']
            no = link.split('no=')[1]
            name = tds[1].get_text(strip=True)
            date = tds[0].get_text(strip=True)
            location = tds[2].get_text(strip=True)
            reg = tds[3].get_text(strip=True)
            dist = tds[4].get_text(strip=True)
            dk = date.split('(')[0].replace('.','-').strip()
            # 0을 없애주는 작업 (04 -> 4)
            dk = "-".join([str(int(x)) for x in dk.split('-')])
            
            results.append({
                "no": no, "name": name, "date": date,
                "location": location, "registration": reg,
                "distances": dist, "dateKey": dk
            })
        except: continue

    if results:
        requests.post(SB_URL, headers=headers, data=json.dumps(results))
        print(f"성공! {len(results)}개의 데이터를 보냈습니다.")

if __name__ == "__main__":
    run()
