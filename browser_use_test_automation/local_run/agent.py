
from browser_use.agent.service import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatZhipuAI
# from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import SecretStr
from dotenv import load_dotenv
import os

load_dotenv()

def initialize_agent(task):

    llm_deepseek = ChatOpenAI(
        base_url='https://api.deepseek.com/v1',
        model='deepseek-chat', 
        api_key=SecretStr(os.getenv('DEEPSEEK_API_KEY'))
        )

    llm_siliconflow = ChatOpenAI(
        base_url='https://api.siliconflow.cn/v1',
        model='Pro/deepseek-ai/DeepSeek-V3',
        api_key=SecretStr(os.getenv('SILICONFLOW_API_KEY'))
    )
    
    llm_gemini = ChatGoogleGenerativeAI(
        model='gemini-2.0-flash-exp', 
        api_key=SecretStr(os.getenv('GEMINI_API_KEY'))
    )
    
    llm_zhipu = ChatZhipuAI(
        base_url='https://api.zhipu.ai/v1',
        model='glm-4', 
        api_key=os.getenv('ZHIPU_API_KEY'),
        # temperature=0.5
        
    )

    agent = Agent(
        task=task, 
        llm=llm_zhipu, 
        use_vision=False, 
        save_conversation_path='../logs/conversation'
        # controller=Controller()
        )
    
    return agent
