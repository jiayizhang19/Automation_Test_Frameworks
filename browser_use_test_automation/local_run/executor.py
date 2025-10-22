
import asyncio
from agent import initialize_agent
from case import *
from playwright.async_api import async_playwright


async def execute(task):
    agent = initialize_agent(task)
    history = await agent.run()
    test_result = history.final_result()
    print('test result:',test_result)
    # print('Raw API Response:', json.dumps(test_result, indent=2, ensure_ascii=False)

# # Dismiss the below function if run with playwright chromium
# async def run_with_custom_chrome(task):
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False,executable_path="G:\ProgramFiles\chromium-win64\chrome-win\chrome.exe")
#         await execute(task)
#         await browser.close()

if __name__ == '__main__':
    asyncio.run(
    execute(login_bfd_task)
    # run_with_custom_chrome(other_task)
)
