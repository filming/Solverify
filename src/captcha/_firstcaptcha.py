from dotenv import load_dotenv
load_dotenv()
import httpx

import os
import json
import asyncio
import sys

class FirstCaptcha:
    def __init__(self):
        self.API_KEY = os.getenv("FIRSTCAPTCHA_API_KEY")
        self.request_id = None
        self.captcha_key = None
    
    async def get_captcha_key(self, method, sitekey, pageurl):
        await self.send_solve_request(method, sitekey, pageurl)
        await self.get_solve_response()

        return self.captcha_key

    async def send_solve_request(self, method, sitekey, pageurl):
        query = {
            "apikey":self.API_KEY,
            "sitekey":sitekey,
            "siteurl":pageurl
        }

        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://api.1stcaptcha.com/{method}", params=query)
        
        resp = json.loads(r.text)

        if resp["Code"] == 1:
            sys.exit(f"{r.status_code} | {r.text}")

        self.request_id = resp["TaskId"]

    async def get_solve_response(self):
        query = {
            "apikey":self.API_KEY,
            "taskid":self.request_id
        }
        
        is_error, is_finished_requesting = False, False
        
        async with httpx.AsyncClient() as client:
            while (not is_finished_requesting) and (not is_error):
                r = await client.get("https://api.1stcaptcha.com/getResult", params=query)
                resp = json.loads(r.text)

                if resp["Status"] in ("PENDING", "PROCESSING"):
                    await asyncio.sleep(3)
                    continue

                elif resp["Status"] == "SUCCESS":
                    self.captcha_key = resp["Data"]["Token"]
                    is_finished_requesting = True

                else:
                    is_error = True
        
        if is_error:
            sys.exit(f"{r.status_code} | {r.text}")
    
    async def refund_captcha(self):
        pass
