import requests, time, hashlib


key = 'asdgasgewfqsef'
url = 'http://127.0.0.1:8000/server.html'


# # 方式一：自定义请求头，发送key进行认证
# response = requests.get(url, headers={"auth-key": key})
# # 自定义请求头： headers={key: value} 注意：auth-key --> HTTP_AUTH_KEY （request.META）
# print(response.text)
# # 特点：实现了简单的认证，但是key写死了；请求被截获后，他人也可以像服务器发送请求

# 方式二：对Key和当前时间 进行加密后作为密钥发送过去 --> 动态key
timestamp = time.time()
print('now is ...',timestamp)
temp = '{key}|{time}'.format(key=key.encode('utf-8'),time=timestamp)
md5_str = hashlib.md5(temp.encode('utf-8')).hexdigest()
print('md5_str...',md5_str)
token = '{md5_str}|{time}'.format(md5_str=md5_str, time=timestamp)
response = requests.get(url, headers={"auth-key": token})
print(response.text)

fake = token
time.sleep(6)
response = requests.get(url, headers={"auth-key": fake})
print('second...',response.text)

# 特点：实现了动态key；但是请求被截获后，他人直接用这个token就可以发送请求

# 方式三：服务端增加有效期5s





