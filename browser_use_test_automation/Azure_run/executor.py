
import asyncio
from azure_agent import initialize_agent
from case import *


async def execute(task):
    agent = initialize_agent(task)
    history = await agent.run()
    test_result = history.final_result()
    print('test result:',test_result)
    # print('Raw API Response:', json.dumps(test_result, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    asyncio.run(
    execute(other_task)
    # execute(login_bfd_task)
)
