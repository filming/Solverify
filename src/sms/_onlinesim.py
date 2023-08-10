from dotenv import load_dotenv
load_dotenv()

import os
import httpx
import sys
import asyncio
import json

class OnlineSim:
    def __init__(self):
        self.API_KEY = os.getenv("ONLINESIM_API_KEY")
        self.request_id = None
        self.phone_number = None
        self.sms_code = None
    
    async def get_phone_number(self, service, country):
        query = {
            "apikey":self.API_KEY,
            "service":service,
            "country":country,
            "number":True
        }
        
        async with httpx.AsyncClient() as client:
            r = await client.get("https://onlinesim.io/api/getNum.php", params=query)
        
        resp = json.loads(r.text)

        if resp["response"] == 1:
            self.request_id = resp["tzid"]
            self.phone_number = resp["number"].split("+")[1]

        else:
            sys.exit(f"{r.status_code} | {r.text}")
        
        return self.phone_number

    async def get_sms_code(self):
        query = {
            "apikey":self.API_KEY,
            "tzid":self.request_id,
            "message_to_code":1
        }

        is_error, attempts = False, 0
        
        async with httpx.AsyncClient() as client:
            while (not is_error) and (attempts <= 60) and (not self.sms_code):
                r = await client.get("https://onlinesim.io/api/getState.php", params=query)

                resp = json.loads(r.text)
                attempts += 1

                if isinstance(resp, list):
                    resp = resp[0]

                    if resp["response"] == "TZ_NUM_WAIT":
                        await asyncio.sleep(3)
                        continue

                    elif resp["response"] == "TZ_NUM_ANSWER":
                        self.sms_code = resp["msg"]
                    
                    else:
                        is_error = True

                else:
                    is_error = True
        
        if is_error:
            sys.exit(f"{r.status_code} | {r.text}")
        
        return self.sms_code

    async def change_current_status(self, status = None):
        query = {
            "apikey":self.API_KEY,
            "tzid":self.request_id
        }

        async with httpx.AsyncClient() as client:
            r = await client.get("https://onlinesim.io/api/setOperationOk.php", params=query)

        resp = json.loads(r.text)

        if resp["response"] != 1:
            sys.exit(f"{r.status_code} | {r.text}")

    async def refund_number(self):
        await self.change_current_status()

    async def close_number(self):
        await self.change_current_status()
