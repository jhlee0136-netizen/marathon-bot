import requests
import json
import os
import re

# 환경 설정
URL = "http://marathon.pe.kr/index_calendar.html"
SB_URL = os.environ.get("SUPABASE_URL") + "/rest/v1/marathon_data"
SB_KEY = os.environ.get("SUPABASE_KEY")

def run():
    headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # 💡 주소에 직접 접속 (헤더를 추가해서 진짜 브라우저처럼 보이게 합니다)
        print(f"진짜 마라톤 사이트 접속 시도: {URL}")
        res = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        
        # 마라톤 사이트 특유의 한글 깨짐 방지 설정
        res.encoding = 'euc-kr' 
        html = res.text

        # 💡 만약 가져온 내용에 'viewport'가 있으면 잘못된 곳에 접속한 것입니다.
        if 'viewport' in html.lower():
            print("경고: 여전히 내부 HTML 파일을 읽고 있습니다. 주소를 강제로 재설정합니다.")
            # 주소를 더 명확하게 다시 시도
            res = requests.get("http://121.78.145.121/index_calendar.html", headers={'Host': 'marathon.pe.kr', 'User-Agent': 'Mozilla/5.0'})
            res.encoding = 'euc-kr'
            html = res.text

        # 대회 번호와 이름 낚아채기
        pattern = r'view\.php\?no=(\d+).*?>(.*?)</a>'
        matches = re.findall(pattern, html, re.DOTALL)
        
        results = []
        for no, name in matches:
            clean_name = re.sub(r'<.*?>', '', name).strip()
            if len(clean_name) < 2: continue
            
            results.append({
                "no": no,
                "name": clean_name,
                "date": "2026.04.01", # 임시
                "location": "전국",
                "registration": "접수중",
                "distances": "10km",
                "dateKey": "2026-4-1"
            })

        if results:
            # 기존 데이터를 싹 지우고 새로 넣으려면 아래 주석을 풀어도 되지만, 일단 추가합니다.
            requests.post(SB_URL, headers=headers, data=json.dumps(results))
            print(f"성공! {len(results)}개의 데이터를 Supabase에 보냈습니다.")
        else:
            print("데이터를 찾지 못했습니다. 소스코드 확인이 필요합니다.")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    run()
