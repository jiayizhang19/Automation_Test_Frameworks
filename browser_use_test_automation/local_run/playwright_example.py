from playwright.async_api import async_playwright, expect
import asyncio

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://corp.m.stage.dongfangfuli.com/bfd-app?union=dfshwx')
        await page.wait_for_selector('input[placeholder="请输入账号"]', timeout=5000)
        await page.fill('input[placeholder="请输入账号"]', '19900000042')
        await page.wait_for_selector('input[placeholder="请输入密码"]', timeout=5000)
        await page.fill('input[placeholder="请输入密码"]', 'aa12345')
        await page.wait_for_selector('button.user-login-signIn', timeout=5000)
        await page.click('button.user-login-signIn')

# Run the async function
asyncio.run(main())
