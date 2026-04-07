import requests
import json
import os
import re

# ⚠️ 주소 뒤에 의미 없는 숫자를 붙여서 '무조건 인터넷에서 새로 가져오게' 만들었습니다.
URL = "http://marathon.pe.kr/index_calendar.html?refresh=1"
SB_URL = os.environ.get("SUPABASE_URL") + "/rest/v1/marathon_data"
SB_KEY = os.environ.get("SUPABASE_KEY")

def run():
    headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    # 💡 브라우저인 것처럼 속여서 진짜 마라톤 사이트에 접속합니다.
    try:
        print(f"접속 시도 중: {URL}")
        res = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        res.encoding = 'euc-kr' # 마라톤 사이트 전용 한글 설정
        html = res.text

        # 💡 진짜 마라톤 사이트인지 확인 (대회명이라는 글자가 있는지)
        if "대회명" not in html:
            print("대회 정보를 찾을 수 없습니다. 주소를 다시 확인해야 합니다.")
            print("가져온 내용 일부:", html[:100])
            return

        # 정보 낚아채기 패턴
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
            requests.post(SB_URL, headers=headers, data=json.dumps(results))
            print(f"성공! {len(results)}개의 데이터를 Supabase에 보냈습니다.")
        else:
            print("데이터 패턴을 찾지 못했습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    run()
