import requests
import json

'''開発用のテスト的なコードです'''
URL="http://172.17.0.1:8080/programs/search_by_datetime?date=2025-05-20&time=10:00"
r=requests.get(URL)
# print(r.json())

# data = json.loads(r)

# print(data.get("contents"))

j = r.json()

for program in j:
    print(program.get("contents"))