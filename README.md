# DingTalk ChatGPT Bot(Unofficial API)
Uses API by [PawanOsman](https://github.com/PawanOsman/PyGPT)

# Disclaimer
This is not open source. [PawanOsman](https://github.com/PawanOsman/) can see all your requests and your session token.
`
# Prerequisites
- DingTalk admin role to create DingTalk bot, [how to create a DingTalk bot](https://xie.infoq.cn/article/3340770024c49b5b1a54597d5)
- ChatGPT session, [how to get ChatGPT session](https://github.com/XueMeijing/dingtalk-chatgpt-bot/blob/main/config.py)

# Usage
1. install dependencies
    ```
    pip3 install -r requirements.txt
    ```
2. Update config.py variables with your own info
3. execute script
    ```
    python3 rt_data.py
    ```
    or execute script in background
    ```
    nohup python3 -u rt_data.py > nohup.out 2>&1 &
    ```
4. watch logs
    ```
    tail -30f nohup.out
    ```
5. If you @YourBotName in DingTalk group, it will get ChatGPT answer and reply.

   E.g. 

   ![demo](https://user-images.githubusercontent.com/35559153/216219243-4df07e62-090a-470d-af99-e64a0c8a36a4.png)
