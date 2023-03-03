import base64
import hmac
import hashlib
import requests
from pygpt import PyGPT
import datetime
from quart import Quart, request, g
import sqlite3

import config

app = Quart(__name__)

DATABASE = 'database.db'

# 查询结果元组转字典
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def init_db():
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    cursor = db.cursor()
    sqlite_create_table_query = ''' CREATE TABLE IF NOT EXISTS USER(
                                    ID                TEXT PRIMARY KEY     NOT NULL,
                                    NAME              TEXT                        ,
                                    CONVERSATION_ID   TEXT                NOT NULL,
                                    PARENT_ID         TEXT                NOT NULL,
                                    CREATE_AT         timestamp           NOT NULL); '''

    cursor.execute(sqlite_create_table_query)
    cursor.close()
    db.close()
    print('数据库初始化成功')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        init_db()
        db = g._database = sqlite3.connect(DATABASE, check_same_thread=False)
    # db  = sqlite3.connect(DATABASE, check_same_thread=False)
    db.row_factory = dict_factory
    return db

def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    db.commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv

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

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# 处理自动回复消息
async def handle_info(req_data):
    # 解析用户发送消息 通讯webhook_url 
    text_info = req_data['text']['content'].strip()
    webhook_url = req_data['sessionWebhook']
    senderid = req_data['senderId']
    # 打开新聊天窗口
    if (text_info == '/reset'):
        sqlite_delete_data_query = """ DELETE FROM 'USER' WHERE id = ? """
        query_db(sqlite_delete_data_query, (senderid,))
        send_md_msg(senderid, '聊天上下文已重置', webhook_url)
        return
    # 请求GPT回复，失败重新请求三次
    retry_count = 0
    max_retry_count = 3

    while retry_count < max_retry_count:
        try:
            chat_gpt = PyGPT(config.GPT_SESSION)
            await chat_gpt.connect()
            await chat_gpt.wait_for_ready()
            answer = await chat_gpt.ask(text_info, query_db, senderid)
            print('answer:\n', answer)
            await chat_gpt.disconnect()
            print('--------------------------')
            break
        except Exception as e:
            retry_count = retry_count + 1
            print('retry_count', retry_count)
            print('error\n', repr(e))
            answer = ''
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


if __name__ == '__main__':
    # 指定host和port，0.0.0.0可以运行在服务器上对外访问，记得开服务器的网络防火墙端口
    # GCP在VPC network -> firewalls -> 增加一条 VPC firewall rules 指定端口，target填 http-server或https-server
    app.run(host='0.0.0.0', port=8083)