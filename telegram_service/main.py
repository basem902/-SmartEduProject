"""
FastAPI Telegram Service
خدمة منفصلة لإدارة Telegram Sessions
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from telegram_manager import TelegramSessionManager

# تحميل المتغيرات
load_dotenv()

# إنشاء التطبيق
app = FastAPI(
    title="Telegram Service",
    description="خدمة إدارة جلسات Telegram",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في الإنتاج: حدد النطاقات المسموحة
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# إنشاء المدير
API_ID = int(os.getenv('TELEGRAM_API_ID'))
API_HASH = os.getenv('TELEGRAM_API_HASH')
telegram_manager = TelegramSessionManager(API_ID, API_HASH)


# Models
class SendCodeRequest(BaseModel):
    phone_number: str


class VerifyCodeRequest(BaseModel):
    phone_number: str
    code: str
    phone_code_hash: str


class VerifyPasswordRequest(BaseModel):
    phone_number: str
    password: str


class DeleteSessionRequest(BaseModel):
    phone_number: str


# Routes
@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "service": "Telegram Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """فحص الصحة"""
    return {"status": "healthy"}


@app.post("/telegram/send-code")
async def send_code(request: SendCodeRequest):
    """إرسال كود التحقق"""
    result = await telegram_manager.send_code(request.phone_number)
    
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result)
    
    return result


@app.post("/telegram/resend-code")
async def resend_code(request: SendCodeRequest):
    """إعادة إرسال الكود"""
    result = await telegram_manager.resend_code(request.phone_number)
    
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result)
    
    return result


@app.post("/telegram/verify-code")
async def verify_code(request: VerifyCodeRequest):
    """التحقق من الكود"""
    result = await telegram_manager.verify_code(
        request.phone_number,
        request.code,
        request.phone_code_hash
    )
    
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result)
    
    return result


@app.post("/telegram/verify-password")
async def verify_password(request: VerifyPasswordRequest):
    """التحقق من كلمة مرور 2FA"""
    result = await telegram_manager.verify_password(
        request.phone_number,
        request.password
    )
    
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result)
    
    return result


@app.get("/telegram/session-status")
async def session_status(phone_number: str):
    """التحقق من حالة الجلسة"""
    exists = telegram_manager.is_session_exists(phone_number)
    return {
        "phone_number": phone_number,
        "session_exists": exists,
        "status": "connected" if exists else "disconnected"
    }


@app.delete("/telegram/delete-session")
async def delete_session(request: DeleteSessionRequest):
    """حذف الجلسة"""
    success = telegram_manager.delete_session(request.phone_number)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "status": "success",
        "message": "تم حذف الجلسة بنجاح"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('FASTAPI_PORT', 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
