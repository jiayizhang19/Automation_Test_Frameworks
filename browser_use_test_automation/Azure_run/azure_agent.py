
from browser_use.agent.service import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from dotenv import load_dotenv
import os
import requests

GEMINI_API = "http://20.0.147.210:5000/gemini"

def call_gemini_api(prompt):
    try:
        response = requests.post(GEMINI_API, json={"prompt": prompt},timeout=50, proxies={"http": None, "https": None})
        return response.json()['response']
    except Exception as e:
        raise Exception(f"Failed to call Gemini API: {e}")


def initialize_agent(task):
    response = call_gemini_api(task)
    print("Response from Azure:",response)
    dummy_llm = ChatGoogleGenerativeAI(model="gemini-2.0", api_key=SecretStr("DUMMY"))
    agent = Agent(task=task, 
                  llm=dummy_llm, 
                context=response,
                use_vision=False, 
                save_conversation_path='logs/conversation')
    
    return agent


# task = """
# Open website https://rahulshettyacademy.com/loginpagePractise/.
# Login with username and password. Login credentials are available on the same page.
# After login, select the first 2 products and add them to the cart.
# Checkout and save the total value of the products.
# Complete the purchase and select the country as India.
# Agree to the terms and conditions and close the promoted window if applicable.
# Verify thank you message is displayed.
# """

# print(call_gemini_api(task))
