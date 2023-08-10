from dotenv import load_dotenv
load_dotenv()

import os
import httpx
import json
import sys
import asyncio

class EndCaptcha:
    def __init__(self):
        raw_creds = os.getenv("ENDCAPTCHA_CREDS").split(":")
        self.USERNAME, self.PASSWORD = raw_creds[0], raw_creds[1]
        self.request_id = None
        self.captcha_key = None

    async def get_captcha_key(self, method, sitekey, pageurl):
        await self.send_solve_request(method, sitekey, pageurl)
        await self.get_solve_response()

        return self.captcha_key

    async def send_solve_request(self, method, sitekey, pageurl):
        payload = {
            "username":self.USERNAME,
            "password":self.PASSWORD,
        }

        if method == "hcaptcha":
            payload["type"] = 7
            payload["hcaptcha_params"] = json.dumps({
                "sitekey":sitekey,
                "pageurl":pageurl
            })

        async with httpx.AsyncClient() as client:
            r = await client.post("http://api.endcaptcha.com/upload", data=payload)
        
        if "UNSOLVED_YET" in r.text:
            self.request_id = r.text.split(":")[1].split("/")[2]

        else:
            sys.exit(f"{r.status_code} | {r.text}")

    async def get_solve_response(self):
        is_error, is_finished_requesting = False, False

        async with httpx.AsyncClient() as client:
            while (not is_finished_requesting) and (not is_error):
                r = await client.get(f"http://api.endcaptcha.com/poll/{self.request_id}")

                if "UNSOLVED_YET" in r.text:
                    await asyncio.sleep(3)
                    continue

                elif "ERROR" in r.text:
                    is_error = True
                
                else:
                    self.captcha_key = r.text
                    is_finished_requesting = True
        
        if is_error:
            sys.exit(f"{r.status_code} | {r.text}")

    async def refund_captcha(self):
        payload = {
            "username":self.USERNAME,
            "password":self.PASSWORD,
            "captcha_id":self.request_id
        }

        async with httpx.AsyncClient() as client:
            r = await client.post("http://api.endcaptcha.com/report", data=payload)
        
        if "ERROR" in r.text:
            sys.exit(f"{r.status_code} | {r.text}")
