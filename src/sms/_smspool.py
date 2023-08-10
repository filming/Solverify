from dotenv import load_dotenv
load_dotenv()
import httpx

import os
import json
import sys
import asyncio

class SMSPool:
    def __init__(self):
        self.API_KEY = os.getenv("SMSPOOL_API_KEY")
        self.request_id = None
        self.phone_number = None
        self.sms_code = None

    async def get_phone_number(self, service, country):
        query = {
            "key":self.API_KEY,
            "country":country,
            "service":service
        }

        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.smspool.net/purchase/sms", params=query)
        
        resp = json.loads(r.text)

        if resp["success"]:
            self.request_id = resp["order_id"]
            self.phone_number = resp["number"]
        
        else:
            sys.exit(f"{r.status_code} | {r.text}")
        
        return self.phone_number

    async def get_sms_code(self):
        query = {
            "key":self.API_KEY,
            "orderid":self.request_id
        }

        is_error, attempts = False, 0

        async with httpx.AsyncClient() as client:
            while (not is_error) and (attempts <= 60) and (not self.sms_code):
                r = await client.get("https://api.smspool.net/sms/check", params=query)

                resp = json.loads(r.text)
                attempts += 1

                if "status" not in resp:
                    is_error = True
                
                else:
                    if resp["status"] == 1:
                        await asyncio.sleep(3)
                        continue

                    elif resp["status"] == 3:
                        self.sms_code = resp["sms"]
                    
                    else:
                        is_error = True
            
        if is_error:
            sys.exit(f"{r.status_code} | {r.text}")
        
        return self.sms_code
    
    async def change_current_status(self, status = None):
        query = {
            "key":self.API_KEY,
            "orderid":self.request_id
        }

        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.smspool.net/sms/cancel", params=query)
        
        resp = json.loads(r.text)
        
        if not resp["success"]:
            sys.exit(f"{r.status_code} | {r.text}")

    async def refund_number(self):
        await self.change_current_status()

    async def close_number(self):
        await self.change_current_status()
