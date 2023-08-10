from ._twocaptcha import TwoCaptcha
from ._firstcaptcha import FirstCaptcha
from ._endcaptcha import EndCaptcha

class Captcha:
    def __init__(self, captcha_service):
        self.captcha_service = captcha_service
        self.captcha_obj = None
    
    def setup(self):
        if self.captcha_service == "2captcha":
            self.captcha_obj = TwoCaptcha()
            
        elif self.captcha_service == "1stcaptcha":
            self.captcha_obj = FirstCaptcha()
        
        elif self.captcha_service == "encaptcha":
            self.captcha_obj = EndCaptcha()

    async def get_captcha_key(self, method, sitekey, pageurl):
        return await self.captcha_obj.get_captcha_key(method, sitekey, pageurl)
    
    async def refund_captcha(self):
        await self.captcha_obj.refund_captcha()
