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
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    # 💡 브라우저 헤더를 더 상세하게 설정합니다.
    browser_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'http://marathon.pe.kr/'
    }
    
    try:
        # 사이트 소스 코드를 직접 가져옵니다.
        res = requests.get(URL, headers=browser_headers, timeout=30)
        res.encoding = 'euc-kr'
        html_content = res.text

        # 💡 정규표현식(글자 패턴 찾기)으로 대회 번호와 정보를 한꺼번에 낚아챕니다.
        # 패턴: view.php?no=숫자 ... <a>대회명</a>
        pattern = r'view\.php\?no=(\d+).*?>(.*?)</a>'
        matches = re.findall(pattern, html_content, re.DOTALL)
        
        results = []
        seen_no = set()

        # 찾은 결과들을 하나씩 정리합니다.
        for no, name in matches:
            if no in seen_no: continue
            
            # 태그 제거 및 깨끗하게 정리
            clean_name = re.sub(r'<.*?>', '', name).strip()
            if not clean_name or len(clean_name) < 2: continue

            # 해당 대회 번호 근처에서 날짜와 장소를 찾습니다.
            # (가장 단순하고 확실한 더미 데이터를 먼저 넣어 테스트합니다.)
            results.append({
                "no": no,
                "name": clean_name,
                "date": "일정 참조",
                "location": "상세페이지 참조",
                "registration": "확인 필요",
                "distances": "정보 없음",
                "dateKey": "2026-01-01" # 임시 날짜
            })
            seen_no.add(no)

        if results:
            # 수집된 데이터를 Supabase에 전송
            r = requests.post(SB_URL, headers=headers, data=json.dumps(results))
            print(f"성공! {len(results)}개의 대회를 찾아서 보냈습니다.")
        else:
            print("데이터 패턴을 찾지 못했습니다. 사이트 소스를 직접 분석해야 합니다.")
            # 디버깅을 위해 가져온 글자 일부를 출력합니다.
            print("사이트 앞부분 내용:", html_content[:200])

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    run()
