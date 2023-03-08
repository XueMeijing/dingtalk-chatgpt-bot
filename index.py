import base64
import hmac
import hashlib
import requests
from pygpt import PyGPT
import datetime
from quart import Quart, request
import asyncio

from sql import init_db, query_db
import config

app = Quart(__name__)

init_db()

chat_gpt = None

@app.route('/', methods=['GET', 'POST'])
async def get_data():
    # 第一步验证：是否是post请求
    if request.method == "POST":
        try:
            # 签名验证 获取headers中的Timestamp和Sign
            req_data = await request.get_json()
            timestamp = request.headers.get('Timestamp')
            sign = request.headers.get('Sign')
            print('request.data-----\n', req_data)
            # 第二步验证：签名是否有效
            if check_sig(timestamp) == sign:
                print('签名验证成功-----')
                # 调用数据处理函数
                await handle_info(req_data)
                return str(req_data)
            else:
                result = '签名验证失败-----'
                print(result)
                return result
        except Exception as e:
            result = '出错啦～～'
            print('error', repr(e))
        return str(result)
    return '钉钉机器人:' + str(datetime.datetime.now())

# 处理自动回复消息
async def handle_info(req_data):
    # 解析用户发送消息 通讯webhook_url 
    text_info = req_data['text']['content'].strip()
    webhook_url = req_data['sessionWebhook']
    senderid = req_data['senderId']
    # 打开新聊天窗口
    if (text_info == '/reset'):
        sqlite_delete_data_query = """ DELETE FROM 'user' WHERE id = ? """
        query_db(sqlite_delete_data_query, (senderid,))
        send_md_msg(senderid, '聊天上下文已重置', webhook_url)
        return
    # 请求GPT回复，失败重新请求三次
    retry_count = 0
    max_retry_count = 3
    global chat_gpt
    while retry_count < max_retry_count:
        try:
            if chat_gpt is None:
                connect_task = asyncio.create_task(init_connect())
                await connect_task
            answer = await chat_gpt.ask(text_info, query_db, senderid)
            print('answer:\n', answer)
            print('--------------------------')
            break
        except Exception as e:
            retry_count = retry_count + 1
            print('retry_count', retry_count)
            print('error\n', repr(e))
            answer = ''
            if retry_count == 2:
                connect_task = asyncio.create_task(init_connect())
                await connect_task
            continue
    if not answer:
        answer = '请求接口失败，请稍后重试'
    # 调用函数，发送markdown消息
    send_md_msg(senderid, answer, webhook_url)

# 发送markdown消息
def send_md_msg(userid, message, webhook_url):
    '''
    userid: @用户 钉钉id
    title : 消息标题
    message: 消息主体内容
    webhook_url: 通讯url
    '''
    message = '<font color=#008000>@%s </font>  \n\n %s' % (userid, message)
    title = '大聪明说'

    data = {
        "msgtype": "markdown",
        "markdown": {
            "title":title,
            "text": message
        },
        # "msgtype": "text",
        # "text": {
        #     "content": message
        # },
        "at": {
            "atDingtalkIds": [
                userid
            ],
        }
    }
    # 利用requests发送post请求
    req = requests.post(webhook_url, json=data)

# 消息数字签名计算核对
def check_sig(timestamp):
    app_secret = config.APP_SECRET
    app_secret_enc = app_secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, app_secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign

async def init_connect():
    # 建立连接
    retry_count = 0
    max_retry_count = 3

    while retry_count < max_retry_count:
        try:
            global chat_gpt
            chat_gpt = PyGPT(config.GPT_SESSION)
            await chat_gpt.connect()
            await chat_gpt.wait_for_ready()
            break
        except Exception as e: 
            retry_count = retry_count + 1
            print('retry_count', retry_count)
            print('error\n', repr(e))
            continue

if __name__ == '__main__':
    # 指定host和port，0.0.0.0可以运行在服务器上对外访问，记得开服务器的网络防火墙端口
    # GCP在VPC network -> firewalls -> 增加一条 VPC firewall rules 指定端口，target填 http-server或https-server
    app.run(host='0.0.0.0', port=8083)