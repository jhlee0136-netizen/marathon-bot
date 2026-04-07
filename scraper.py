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
    
    # 💡 모든 링크(a 태그)를 다 뒤져서 'view.php?no='가 들어있는 걸 찾습니다.
    all_links = soup.find_all('a', href=True)
    
    results = []
    seen_no = set() # 중복 방지

    for link_tag in all_links:
        href = link_tag['href']
        if 'view.php?no=' in href:
            try:
                # 1. 대회 번호 추출
                no = href.split('no=')[1].split('&')[0]
                if no in seen_no: continue
                
                # 2. 이 링크가 포함된 줄(tr)을 찾습니다.
                row = link_tag.find_parent('tr')
                if not row: continue
                
                tds = row.find_all('td')
                if len(tds) < 5: continue
                
                # 3. 데이터 정리
                name = link_tag.get_text(strip=True)
                date_raw = tds[0].get_text(strip=True)
                location = tds[2].get_text(strip=True)
                reg = tds[3].get_text(strip=True)
                dist = tds[4].get_text(strip=True)
                
                # 날짜 키 정리 (2026.04.03 -> 2026-4-3)
                pure_date = date_raw.split('(')[0].strip()
                if '.' in pure_date:
                    parts = pure_date.split('.')
                    dk = f"{int(parts[0])}-{int(parts[1])}-{int(parts[2])}"
                else:
                    dk = pure_date

                results.append({
                    "no": no, "name": name, "date": date_raw,
                    "location": location, "registration": reg,
                    "distances": dist, "dateKey": dk
                })
                seen_no.add(no)
            except:
                continue

    # Supabase에 전송
    if results:
        r = requests.post(SB_URL, headers=headers, data=json.dumps(results))
        print(f"성공! {len(results)}개의 데이터를 보냈습니다.")
    else:
        # 마지막 수단: 페이지 전체 텍스트 출력 (디버깅용)
        print("데이터를 여전히 찾지 못했습니다. 로직을 더 단순화해야 합니다.")

if __name__ == "__main__":
    run()
