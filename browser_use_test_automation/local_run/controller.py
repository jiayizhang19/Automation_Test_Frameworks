import json
from browser_use import Controller
from browser_use.agent.service import Agent
from browser_use.browser.context import BrowserContext
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI 
from pydantic import BaseModel, SecretStr
import os
from dotenv import load_dotenv
import asyncio



# Define a Pydantic model to structure the expected result of the checkout process
class CheckoutResult(BaseModel):
    login_status: str  
    product_name: str  
    price: str  
    quantity: int  
    total_price: str  
    confirmation_status: str
    payment_status: str  
    order_status: str  
    order_number: str  
    
controller = Controller(output_model=CheckoutResult)

@controller.action('账号 19900000042，密码 aa123456 登录')
async def login(browser: BrowserContext):
    page = await browser.get_current_page()
    await page.wait_for_selector('input[type="text"]')
    await page.wait_for_selector('input[type="password"]')
    await page.fill('input[type="text"]', '19900000042')
    await page.fill('input[type="password"]', 'aa123456')
    await page.wait_for_selector('button[type="submit"]')
    await page.click('button[type="submit"]')



