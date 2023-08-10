from ._smsactivate import SMSActivate
from ._smspool import SMSPool
from ._onlinesim import OnlineSim

class SMS:
    def __init__(self, sms_service):
        self.sms_service = sms_service
        self.sms_obj = None
    
    def setup(self):
        if self.sms_service == "smsactivate":
            self.sms_obj = SMSActivate()

        elif self.sms_service == "smspool":
            self.sms_obj = SMSPool()
        
        elif self.sms_service == "onlinesim":
            self.sms_obj = OnlineSim()

    async def get_phone_number(self, service, country):
        return await self.sms_obj.get_phone_number(service, country)

    async def change_current_status(self, status):
        await self.sms_obj.change_current_status(status)
    
    async def get_sms_code(self):
        return await self.sms_obj.get_sms_code()
    
    async def refund_number(self):
        await self.sms_obj.refund_number()
    
    async def close_number(self):
        await self.sms_obj.close_number()
