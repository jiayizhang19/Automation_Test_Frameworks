import json
from browser_use.agent.service import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI 
from pydantic import SecretStr
import os
from dotenv import load_dotenv
import asyncio

# Load .env file
load_dotenv()


async def login_bfd():

    task = (

        'Important: I am UI Automation tester validating the tasks'
        '打开 https://corp.m.stage.dongfangfuli.com/bfd-app?union=dfshwx'
        '输入账号 19900000042 和密码 aa123456'
        '点击登录'
        '验证右上角显示 "19900000042"'
        # '验证主页包含 "百福得"字样'
        # '搜索商品 "2024自动化普通优选"'
        # '点击商品，进入详情页面，点击立即购买'
        # '验证商品名称，价格，数量，总价'
        # '点击提交订单，选择点卡支付'
        # '点击确认支付，验证支付成功'
        # '点击查看订单，验证订单状态，订单编号'
    )

    # Initialize the model
    # llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))
    llm = ChatOpenAI(
        base_url='https://api.deepseek.com/v1',
        model='deepseek-chat', 
        api_key=SecretStr(os.getenv('DEEPSEEK_API_KEY'))
        )

    # Create agent with the model
    agent = Agent(task, llm, 
                  use_vision=False, # When enabled, the model processed visual infroamtion
                  save_conversation_path='logs/conversation'
                  )

    history = await agent.run()
    test_result = history.final_result()
    print('test result:',test_result)
    # print('Raw API Response:', json.dumps(test_result, indent=2, ensure_ascii=False))


asyncio.run(login_bfd())