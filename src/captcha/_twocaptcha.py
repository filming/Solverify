from dotenv import load_dotenv
load_dotenv()
import httpx

import asyncio
import os
import json
import sys

class TwoCaptcha:
    def __init__(self):
        self.API_KEY = os.getenv("2CAPTCHA_API_KEY")
        self.request_id = None
        self.captcha_key = None

    async def get_captcha_key(self, method, sitekey, pageurl):
        await self.send_solve_request(method, sitekey, pageurl)
        await self.get_solve_response()

        return self.captcha_key

    async def send_solve_request(self, method, sitekey, pageurl):
        query = {
            "key":self.API_KEY,
            "method":method,
            "sitekey":sitekey,
            "pageurl":pageurl,
            "json":1,
        }

        async with httpx.AsyncClient() as client:
            r = await client.get(f"http://2captcha.com/in.php", params=query)

        resp = json.loads(r.text)

        if resp["status"] == 1:
            self.request_id = resp["request"]
        else:
            sys.exit(f"{r.status_code} | {r.text}")

    async def get_solve_response(self):
        query = {
            "key":self.API_KEY,
            "action":"get",
            "id":self.request_id,
            "json":1,
        }

        is_error, is_finished_requesting = False, False

        async with httpx.AsyncClient() as client:
            while (not is_finished_requesting) and (not is_error):
                r = await client.get(f"http://2captcha.com/res.php", params=query)
                resp = json.loads(r.text)

                if resp["status"] == 0:
                    await asyncio.sleep(3)
                    continue

                elif resp["status"] == 1:
                    self.captcha_key = resp["request"]

                    if isinstance(self.captcha_key, dict):
                        self.captcha_key = resp["request"]["token"]
                        
                    is_finished_requesting = True
                
                else:
                    is_error = True
        
        if is_error:
            sys.exit(f"{r.status_code} | {r.text}")
    
    async def refund_captcha(self):
        pass
