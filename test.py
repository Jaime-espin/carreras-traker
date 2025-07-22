import requests

url = "https://www.global-tempo.com"

response = requests.get(url)
print(response.status_code)
print(response.text[:500])  # ver parte del HTML
