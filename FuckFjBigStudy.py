import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64encode
import requests
from urllib.parse import urlparse
from difflib import SequenceMatcher
import getpass
import time

from combineDB import combineWithExam,combineWithSelfStudy

'''TEST'''


'''combine q database'''
#combineWithExam('tkS1894070.json')
#combineWithSelfStudy('tk2.json')

import os

# 指定目录
directory = "./NetDB"

'''
# 遍历当前目录下的文件
for file in os.listdir(directory):
    file_path = os.path.join(directory, file)
    if os.path.isfile(file_path):  # 确保是文件
        combineWithSelfStudy(file_path)


exit()
'''

session = requests.Session()
# 大学习oauth id 8486f6909598db9a
client_id = '8486f6909598db9a'
redirect_uri = "http://f.yiban.cn/iapp254007"
response = session.get('https://oauth.yiban.cn/code/html?client_id='+ client_id +'&redirect_uri=http://f.yiban.cn/iapp254007&state=STATE')
print(f"Response Status: {response.status_code}")

# 查看响应的 Cookies
print("Cookies from Response:")
for cookie in session.cookies:
    print(f"{cookie.name} = {cookie.value}")

'''
# 保存 cookies 到文件
cookies_dict = requests.utils.dict_from_cookiejar(session.cookies)
with open('cookies.txt', 'w') as file:
    for key, value in cookies_dict.items():
        file.write(f"{key}={value}\n")

print("\nCookies saved to 'cookies.txt'.")


with open('cookies.txt', 'r') as file:
    cookies = {}
    for line in file:
        key, value = line.strip().split('=')
        cookies[key] = value

session.cookies = requests.utils.cookiejar_from_dict(cookies)
'''

#提取rsa公钥
html_content = response.text
start_marker = '-----BEGIN PUBLIC KEY-----'
end_marker = '-----END PUBLIC KEY-----'

try:
    # 找到起点和终点
    start_index = html_content.index(start_marker)
    end_index = html_content.index(end_marker, start_index) + len('-----END PUBLIC KEY-----')
    
    # 提取公钥内容
    public_key_pem = html_content[start_index:end_index]
    print("Extracted Public Key:")
    print(public_key_pem)
except ValueError:
    print("Public key not found in the HTML content.")

#提取sign
start_marker = "var page_use = '"
end_marker = "';"

try:
    # 找到起点和终点
    start_index = html_content.index(start_marker) + len(start_marker)
    end_index = html_content.index(end_marker, start_index)
    
    # 提取公钥内容
    page_use = html_content[start_index:end_index]
    print("Extracted sign:")
    print(page_use)
except ValueError:
    print("Sign not found in the HTML content.")


username = str(input("输入易班手机号"))
password = str(getpass.getpass("输入易班密码"))

info = {
    'user':username,
    'pwd':password
}
with open('pwd'+str(username)+'.json', 'w') as file:
    json.dump(info, file)

# 加载公钥
public_key = RSA.import_key(public_key_pem)
# 创建加密对象
cipher = PKCS1_v1_5.new(public_key)
# 待加密的明文
plaintext = password
# 加密并编码为Base64
ciphertext = cipher.encrypt(plaintext.encode())
ciphertext_base64 = b64encode(ciphertext).decode()

print("密码加密结果(Base64): ", ciphertext_base64)



# 请求数据
data = {
    'oauth_uname': username,  # 替换为实际的用户名
    'oauth_upwd': ciphertext_base64,  # 替换为实际的密码
    'client_id': client_id,  # 替换为实际的客户端ID
    'redirect_uri': redirect_uri,  # 替换为实际的重定向URI
    'state': "STATE",  # 替换为实际的状态值
    'scope': "1,2,3,4,100,",  # 替换为实际的作用域
    'display': 'authorize'
}

# 发起 POST 请求
try:
    response = session.post('https://oauth.yiban.cn/code/usersure?ajax_sign='+page_use, data=data)

    # 检查响应状态
    if response.status_code == 200:
        print("Response received:")
        #print(response.json())  # 假设返回 JSON 格式数据
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

res = response.json()
print(res)
if(res['code']!='s200'):
    print("登录失败")
    exit()

print("Extracting token")
response = session.get('https://f.yiban.cn/iapp254007')
final_url = response.url

# get target
print("认证的地址: ", final_url)
parsed_url = urlparse(final_url)
# 获取主机名和端口
DXXurl = parsed_url.netloc


#get token
html_content = response.text
start_marker = "var token = '"
end_marker = "';"

try:
    # 找到起点和终点
    start_index = html_content.index(start_marker) + len(start_marker)
    end_index = html_content.index(end_marker, start_index)
    
    # 提取公钥内容
    token = html_content[start_index:end_index]
    print("Extracted token:")
    print(token)
except ValueError:
    print("token not found in the HTML content.")

#get User info
session.headers['token']=token

response = session.get('http://'+DXXurl+'/api/mobile/mine/getUserInfo')

res = response.json()

if(res['code']!=200):
    print("获取用户信息失败")
    exit()
print("获取用户信息成功: ")
print(res['data']['school_name']+" "+res['data']['college_name']+" "+res['data']['class_name']+" "+res['data']['real_name'])

#get exam info

response = session.get('http://'+DXXurl+'/api/mobile/examInfo/getExamList?examType=QP0001')
res = response.json()
if(res['code']!=200):
    print("获取考试信息失败")
    exit()
print("获取考试信息成功: ")
data = res['data']
#print(data)
for item in data:
    print(f"ID: {item['id']}")
    print(f"名称: {item['name']}")
    print(f"规则名称: {item['rule_name']}")
    print(f"开始时间: {item['begin_time']}")
    print(f"截至时间: {item['end_time']}")
    print(f"类别: {item['exam_type']}")
    print(f"总分: {item['exam_sum_score']}")
    print(f"考试时间 (秒): {item['exam_time']}")
    print(f"总次数: {item['second']}")
    print(f"剩余次数: {item['second']-item['cnt']}")
    print("-" * 40)
exampId = str(input("Which exam Id U fuck: "))

#check time
# 请求数据
data = {
    'examInfoId': exampId,  # 考试ID
}
response = session.post('http://'+DXXurl+'/api/mobile/examInfo/checkTime',data=data)
res = response.json()
if(res['code']!=200):
    print("考试过期")
    exit()
#begin exam
data = {
    'examInfoId': exampId,  # 考试ID
}
response = session.post('http://'+DXXurl+'/api/mobile/examInfo/beginExam',data=data)
res = response.json()
if(res['code']!=200):
    print("开始考试失败")
    exit()
examMetaData = res['data']
#get question
response = session.get('http://'+DXXurl+'/api/mobile/examInfo/getExam?recordId='+str(examMetaData['id']))
res = response.json()
if(res['code']!=200):
    print("获得题目失败")
    exit()
questionsMetaData = res['data']
questionsList = questionsMetaData['questionList']

#load combine DB
with open('tk.json', 'r', encoding='utf-8') as file:
    combine = json.load(file)  
dT = combine['data']

userAnswer = {}
i = 0
for item in questionsList:
    i = i+1
    qId = item['id']
    existing_ids = {entry['q'] for entry in dT}

    if qId not in existing_ids:
        
        userAnswer['answer_'+str(i)] = "A"
        print("第",i,"题没找到答案")
        continue
    ans = next((entry for entry in dT if entry['q'] == qId), None)
    print("第",i,"题找到答案")
    userAnswer['answer_'+str(i)] = ans['a']



#考试id
print(examMetaData)
#sumbit Answer
# 1.calc <qs>

# 加载公钥
qs_key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCYL1DAA0V2++SIrxjaq+8SdsH5ihM5VT3G2pKjB3YkZiyMpjdg+DH4k7be5t7TEMlK9FoSHez1BckEnGqv2JcnUoqTKBtPvqew4d/Tx+aPadBWEDYj93BOxCcCoj1g2lHGELTyrMiRgrbNNIZ4ilswCAdgD2KdA4swY4oHcnll6wIDAQAB\n-----END PUBLIC KEY-----"
qs_public_key = RSA.import_key(qs_key)
# 创建加密对象
qs_cipher = PKCS1_v1_5.new(qs_public_key)
# 待加密的明文
qs_plaintext = str(examMetaData['id'])+"_csit"
# 加密并编码为Base64
qs_ciphertext = qs_cipher.encrypt(qs_plaintext.encode())
qs_ciphertext_base64 = b64encode(qs_ciphertext).decode()

print("qs加密结果(Base64): ", qs_ciphertext_base64)
qs = qs_ciphertext_base64

text = json.dumps(userAnswer)
print(text)
#'{"answer_1":"D","answer_2":"D","answer_3":"B"}'
data = {
    'recordId': str(examMetaData['id']),  # 考试ID
    'userAnswer':text,#'{"answer_1":"A"}',
    'qs':qs
}
#骗出答案先随便交一次
# 延迟 9 分钟 39 秒（即 579 秒）
#time.sleep(579)
response = session.post('http://'+DXXurl+'/api/mobile/examInfo/submitExam',data=data)
res = response.json()
if(res['code']!=200):
    print("提交失败")
    exit()
#get Score
response = session.get('http://'+DXXurl+'/api/mobile/examInfo/getSumScore?examId='+str(examMetaData['id']))
res = response.json()
if(res['code']!=200):
    print("获得得分失败")
    exit()
print("得分: ", res['data'])

#getAnswer
#get Score
response = session.get('http://'+DXXurl+'//api/mobile/examInfo/getRecord?id='+str(examMetaData['id']))
res = response.json()
if(res['code']!=200):
    print("获得答案失败")
    exit()

print("构建题库中")
questionsDatabase = []
detail = res['data']['detail']
with open('tkS'+str(examMetaData['id'])+'.txt', 'w') as file:
    json.dump(detail, file)


for item in detail:
    '''
    options = {
        'A':item['option_a'],
        'B':item['option_b'],
        'C':item['option_c'],
        'D':item['option_d'],
        'E':item['option_e'],
        'F':item['option_f']
    }
    answer = []
    for char in item['answer']:
        answer.append(options[char])
        
    
    temp = {
        'q':item['question_remark'],
        'qId':item['id'],
        'a':answer,
        'aSp':item['answer']
    }
    '''
    temp = {
        'q':item['id'],
        'a':item['answer']
    }
    questionsDatabase.append(temp)

print('题库构建完成')

print(questionsDatabase)
with open('tkD'+str(examMetaData['id'])+'.json', 'w') as file:
    json.dump(questionsDatabase, file)

#Auto fuck exam




'''
def get_similarity_ratio(str1, str2):
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, str1, str2).ratio()

def search_question(database,qType, queryQ, queryA, threshold=0.7):
    qa = {
        'a':'xxxx',
        'b':'xxxx'
    }
    """
    在题库中搜索与查询接近的问题
    - database: 题库列表
    - query: 搜索的字符串
    - threshold: 相似度阈值
    """
    results = []
    for item in database:
        similarity = get_similarity_ratio(queryQ, item['q'])
        if similarity >= threshold:  # 如果相似度大于等于阈值
            results.append({
                'question': item['q'],
                'answer':item['a'],
                'similarity': similarity
            })
    if(len(results) == 0):
        return 'A'
    # 按相似度排序
    results.sort(key=lambda x: x['similarity'], reverse=True)
    if(results)
    #handle opt
    if qType = 1 : #only opt
        
    return results
'''
