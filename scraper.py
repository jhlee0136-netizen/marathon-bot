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
    
    # 💡 브라우저인 것처럼 속여서 접속합니다.
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    try:
        res = requests.get(URL, headers={'User-Agent': user_agent})
        res.encoding = 'euc-kr'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 💡 "view.php?no=" 글자가 포함된 모든 줄을 찾습니다.
        results = []
        seen_no = set()

        # 페이지의 모든 tr 태그를 검사
        for tr in soup.find_all('tr'):
            text = tr.get_text()
            # 마라톤 일정 줄인지 확인 (날짜 형식이 있는지 등)
            if 'view.php?no=' in str(tr) and ('.' in text):
                tds = tr.find_all('td')
                if len(tds) >= 5:
                    try:
                        link = tr.find('a', href=True)['href']
                        no = link.split('no=')[1].split('&')[0]
                        if no in seen_no: continue

                        name = tds[1].get_text(strip=True)
                        date_raw = tds[0].get_text(strip=True)
                        location = tds[2].get_text(strip=True)
                        reg = tds[3].get_text(strip=True)
                        dist = tds[4].get_text(strip=True)
                        
                        # 날짜 키 정리 (2026.4.3 형태)
                        pure_date = date_raw.split('(')[0].strip()
                        parts = pure_date.split('.')
                        if len(parts) >= 3:
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
            # 한 번에 너무 많이 보내면 오류가 날 수 있으니 나눠서 보냅니다.
            r = requests.post(SB_URL, headers=headers, data=json.dumps(results))
            print(f"성공! {len(results)}개의 데이터를 보냈습니다.")
        else:
            print("여전히 데이터를 찾지 못했습니다. 사이트 보안 수단이 변경되었을 수 있습니다.")
            
    except Exception as e:
        print(f"접속 중 오류 발생: {e}")

if __name__ == "__main__":
    run()
