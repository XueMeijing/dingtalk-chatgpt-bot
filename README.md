# Change Log
- 2022-03-08
    - 优化代码，修复代理服务器偶尔connect refused的问题
- 2022-03-03
    - 使用sqlite3增加上下文功能, @bot /reset 命令会重新打开新聊天窗口
        ![image](https://user-images.githubusercontent.com/35559153/222692011-d4ac1d37-cd66-41ef-9d87-9baf423c3edd.png)

- 2022-02-14
    - 增加docker部署
- 2022-02-10
    - 机器人名字叫ChatGPT会被禁止使用, 可以换成其他的
        ![image](https://user-images.githubusercontent.com/35559153/217995508-6916bceb-188f-4bfd-b945-8841616d2ade.png)

# DingTalk ChatGPT Bot(Unofficial API)
Uses API by [PawanOsman](https://github.com/PawanOsman/PyGPT)

# Disclaimer
This is not open source. [PawanOsman](https://github.com/PawanOsman/) can see all your requests and your session token.

# Prerequisites
- DingTalk admin role to create DingTalk bot, [how to create a DingTalk bot](https://xie.infoq.cn/article/3340770024c49b5b1a54597d5)
- OpenAi ChatGPT session
# Feature
## chat conversation context
## reset conversation

# Usage
## python
1. install dependencies
    ```
    pip3 install -r requirements.txt
    ```
2. Update config.py variables with your own info
3. execute script in background
    ```
    nohup python3 -u index.py > nohup.out 2>&1 &
    ```
4. watch logs
    ```
    tail -30f nohup.out
    ```
## docker
1. get docker image and run
    ```
    docker run -dp 8083:8083 fengcailing/dingtalk-chatgpt-bot:1.0.2
    ```
2. show docker list and get docker container id
    ```
    docker ps
    ```
3. cd docker
    ```
    docker exec -it <containerId> /bin/sh
    ```
4. update config.py(GPT_SESSION、APP_SECRET)
5. exit docker
    ```
    exit
    ```
6. create new iamge
    ```
    docker commit -m 'update config' <containerId> dingtalk-chatgpt-bot:v1
    ```
7. stop pre container and run new image
    ```
    docker stop <containerId>
    docker run -dp 8083:8083 dingtalk-chatgpt-bot:v1
    ```
8. watch logs
    ```
    docker logs -n 30 -f <new containerId>
    ```

If you @YourBotName in DingTalk group, it will get ChatGPT answer and reply.

   E.g. 

   ![demo](https://user-images.githubusercontent.com/35559153/216219243-4df07e62-090a-470d-af99-e64a0c8a36a4.png)

