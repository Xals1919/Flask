import requests

response = requests.post(url='http://localhost:5000/ticket/',
                         json={
                             "description": "super pyper paper123",
                             "owner": "Viktor123",
                         }
                         )

print(response.text)
print(response.status_code)
