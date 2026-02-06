import csv
import time
import requests

API_URL = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={}"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.dhlottery.co.kr/",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "ko-KR,ko;q=0.9",
})

def get_lotto_numbers(draw_no: int):
    url = API_URL.format(draw_no)
    r = session.get(url, timeout=15)
    r.raise_for_status()

    ctype = (r.headers.get("Content-Type") or "").lower()
    if "application/json" not in ctype:
        txt = r.text[:300]
        raise RuntimeError(f"[{draw_no}회] JSON 응답이 아님 (차단/대기 가능)\n{txt}")

    data = r.json()

    if data.get("returnValue") != "success":
        return None

    return {
        "round": data["drwNo"],
        "date": data["drwNoDate"],
        "nums": [data[f"drwtNo{i}"] for i in range(1, 7)],
        "bonus": data["bnusNo"]
    }

def main():
    # 최신 회차는 파일에서 읽음
    with open("latest_round.txt", "r", encoding="utf-8") as f:
        max_round = int(f.read().strip())

    with open("lottoRes.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["회차", "날짜", "번호1", "번호2", "번호3", "번호4", "번호5", "번호6", "보너스"])

        for n in range(1, max_round + 1):
            res = get_lotto_numbers(n)

            if not res:
                print(f"[{n}회] 스킵")
                continue

            writer.writerow([res["round"], res["date"], *res["nums"], res["bonus"]])
            print(f"[{n}회] 저장 완료")

            time.sleep(0.3)  # 과호출 방지

    print("완료: lottoRes.csv 생성")

if __name__ == "__main__":
    main()
