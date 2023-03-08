'''
Uses API by [PawanOsman](https://github.com/PawanOsman/PyGPT)
'''

import uuid
import asyncio
import socketio
import datetime
import json
import base64

class PyGPT:
    def __init__(self, session_token, timeout=120, bypass_node='https://gpt.pawan.krd'):
        self.ready = False
        self.socket = socketio.AsyncClient()
        self.socket.on('connect', self.on_connect)
        self.socket.on('disconnect', self.on_disconnect)
        self.socket.on('serverMessage', print)
        self.session_token = session_token
        self.conversations = []
        self.timeout = timeout
        self.auth = None
        self.expires = datetime.datetime.now()
        self.pause_token_checks = False
        self.bypass_node = bypass_node
        asyncio.create_task(self.cleanup_conversations())

    async def connect(self):
        await self.socket.connect(f'{self.bypass_node}/?client=python&version=1.0.4&versionCode=104')

    async def disconnect(self):
        await self.socket.disconnect()

    def on_connect(self):
        print('Connected to server')
        asyncio.create_task(self.check_tokens())

    def on_disconnect(self):
        print('Disconnected from server')
        self.ready = False

    async def check_tokens(self):
        while True:
            if self.pause_token_checks:
                await asyncio.sleep(0.5)
                continue
            self.pause_token_checks = True
            now = datetime.datetime.now()
            offset = datetime.timedelta(minutes=2)
            if self.expires < (now - offset) or not self.auth:
                await self.get_tokens()
            self.pause_token_checks = False
            await asyncio.sleep(0.5)

    async def cleanup_conversations(self):
        while True:
            await asyncio.sleep(60)
            now = datetime.datetime.now()
            self.conversations = [c for c in self.conversations if
                                  now - c['last_active'] < datetime.timedelta(minutes=60)]

    def add_conversation(self, id):
        conversation = {
            'id': id,
            'conversation_id': None,
            'parent_id': uuid.uuid4(),
            'last_active': datetime.datetime.now()
        }
        self.conversations.append(conversation)
        return conversation

    def get_conversation_by_id(self, id):
        conversation = next((c for c in self.conversations if c['id'] == id), None)
        if conversation is None:
            conversation = self.add_conversation(id)
        else:
            conversation['last_active'] = datetime.datetime.now()
        return conversation

    async def wait_for_ready(self):
        while not self.ready:
            await asyncio.sleep(0.025)
        print('Ready!!')

    async def ask(self, prompt, query_db, id='default'):
        if not self.auth or not self.validate_token(self.auth):
            await self.get_tokens()
        conversation = self.get_conversation_by_id(id)
        
        sqlite_get_data_query = """ SELECT * FROM user WHERE id = ? """
        user_record = query_db(sqlite_get_data_query, (id,), True)
        print('user_record', user_record)

        # Fix for timeout issue by Ulysses0817: https://github.com/Ulysses0817
        data = await self.socket.call(event='askQuestion', data={
            'prompt': prompt,
            'parentId': user_record['parent_id'] if user_record else str(conversation['parent_id']),
            'conversationId': user_record["conversation_id"] if user_record else str(conversation['conversation_id']),
            'auth': self.auth
        }, timeout=self.timeout)
        print('ask data---\n', data)
        if 'error' in data:
            print(f'Error: {data["error"]}')
            return f'Error: {data["error"]}'
        try:
            if user_record is None:
                # 插入数据
                sqlite_insert_data_query = """  INSERT INTO user
                                                ('id', 'name', 'conversation_id', 'parent_id', 'create_at')
                                                VALUES (?,?,?,?,?);  """
                query_db(sqlite_insert_data_query, (id, None, data['conversationId'], data['messageId'], datetime.datetime.now()))
                print('插入数据')
            else:
                # 更新数据
                sqlite_update_data_query = """ UPDATE user SET id = ?, name = ?, conversation_id = ?, parent_id = ?, create_at = ? WHERE id = ? """
                query_db(sqlite_update_data_query, (id, None, data['conversationId'], data['messageId'], datetime.datetime.now(), id))
                print('更新数据')
        except Exception as e:
            print('database error\n', repr(e))
        conversation['parent_id'] = data['messageId']
        conversation['conversation_id'] = data['conversationId']
        return data['answer']

    def validate_token(self, token):
        if not token:
            return False
        parsed = json.loads(base64.b64decode(f'{token.split(".")[1]}==').decode())
        return datetime.datetime.now() <= datetime.datetime.fromtimestamp(parsed['exp'])

    async def get_tokens(self):
        await asyncio.sleep(1)
        # Fix for timeout issue by Ulysses0817: https://github.com/Ulysses0817
        data = await self.socket.call(event='getSession', data=self.session_token, timeout=self.timeout)

        if 'error' in data:
            print(f'Error getting session: {data["error"]}')
        else:
            self.auth = data['auth']
            self.expires = datetime.datetime.strptime(data['expires'], '%Y-%m-%dT%H:%M:%S.%fZ')
            self.session_token = data['sessionToken']
            self.ready = True