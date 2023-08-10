from dotenv import load_dotenv
load_dotenv()

import os
import httpx
import sys
import asyncio

class SMSActivate:
    def __init__(self):
        self.API_KEY = os.getenv("SMSACTIVATE_API_KEY")
        self.request_id = None
        self.phone_number = None
        self.sms_code = None
    
    async def get_phone_number(self, service, country):
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://sms-activate.org/stubs/handler_api.php?api_key={self.API_KEY}&action=getNumber&service={service}&country={country}")

        if "ACCESS_NUMBER" in r.text:
            resp = r.text.split(":")
            self.request_id, self.phone_number = resp[1], resp[2]

        else:
            sys.exit(f"{r.status_code} | {r.text}")
        
        return self.phone_number

    async def get_sms_code(self):
        is_error, attempts = False, 0

        async with httpx.AsyncClient() as client:
            while (not is_error) and (not self.sms_code) and (attempts <= 60):
                r = await client.get(f"https://api.sms-activate.org/stubs/handler_api.php?api_key={self.API_KEY}&action=getStatus&id={self.request_id}")

                attempts += 1
                
                if "STATUS_WAIT_CODE" in r.text:
                    await asyncio.sleep(3)
                    continue

                elif "STATUS_OK" in r.text:
                    resp = r.text.split(":")
                    self.sms_code = resp[1]

                else:
                    is_error = True
        
        if is_error:
            sys.exit(f"{r.status_code} | {r.text}")
        
        return self.sms_code

    async def change_current_status(self, status = None):
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://api.sms-activate.org/stubs/handler_api.php?api_key={self.API_KEY}&action=setStatus&status={status}&id={self.request_id}")

        if "ACCESS" not in r.text:
            sys.exit(f"{r.status_code} | {r.text}")

    async def refund_number(self):
        await self.change_current_status(8)

    async def close_number(self):
        await self.change_current_status(6)
