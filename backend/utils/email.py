"""
نظام إرسال البريد الإلكتروني
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class EmailService:
    """خدمة إرسال البريد الإلكتروني"""
    
    @staticmethod
    def send_activation_email(email: str, full_name: str, code: str) -> bool:
        """
        إرسال إيميل كود التفعيل
        
        Args:
            email: البريد الإلكتروني للمعلم
            full_name: الاسم الكامل
            code: كود التفعيل
            
        Returns:
            bool: True إذا تم الإرسال بنجاح
        """
        try:
            subject = 'تفعيل حسابك في مشروعي الذكي - SmartEduProject'
            
            # HTML template
            html_content = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f4f7fa;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 10px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #00ADEF 0%, #0088CC 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .greeting {{
                        font-size: 20px;
                        color: #333;
                        margin-bottom: 20px;
                    }}
                    .message {{
                        font-size: 16px;
                        color: #666;
                        line-height: 1.6;
                        margin-bottom: 30px;
                    }}
                    .code-box {{
                        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                        border: 2px dashed #00ADEF;
                        border-radius: 10px;
                        padding: 25px;
                        text-align: center;
                        margin: 30px 0;
                    }}
                    .code {{
                        font-size: 36px;
                        font-weight: bold;
                        color: #00ADEF;
                        letter-spacing: 8px;
                        margin: 10px 0;
                    }}
                    .code-label {{
                        font-size: 14px;
                        color: #666;
                        margin-bottom: 10px;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border-right: 4px solid #ffc107;
                        padding: 15px;
                        margin: 20px 0;
                        border-radius: 5px;
                    }}
                    .warning p {{
                        margin: 0;
                        color: #856404;
                        font-size: 14px;
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        padding: 20px 30px;
                        text-align: center;
                        font-size: 14px;
                        color: #666;
                    }}
                    .footer a {{
                        color: #00ADEF;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎓 مشروعي الذكي</h1>
                        <p style="margin: 10px 0 0 0;">SmartEduProject</p>
                    </div>
                    
                    <div class="content">
                        <div class="greeting">
                            👋 مرحباً {full_name}
                        </div>
                        
                        <div class="message">
                            <p>شكراً لتسجيلك في منصة <strong>مشروعي الذكي</strong>!</p>
                            <p>لإكمال عملية التسجيل وتفعيل حسابك، يرجى استخدام كود التفعيل التالي:</p>
                        </div>
                        
                        <div class="code-box">
                            <div class="code-label">كود التفعيل الخاص بك</div>
                            <div class="code">{code}</div>
                        </div>
                        
                        <div class="warning">
                            <p>⚠️ <strong>تنبيه:</strong> هذا الكود صالح لمدة 30 دقيقة فقط. لا تشارك هذا الكود مع أي شخص.</p>
                        </div>
                        
                        <div class="message">
                            <p>بعد إدخال كود التفعيل، ستحصل على كلمة مرور مؤقتة يمكنك تغييرها لاحقاً من الإعدادات.</p>
                            <p>إذا لم تقم بإنشاء هذا الحساب، يرجى تجاهل هذه الرسالة.</p>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>© 2025 SmartEduProject - مشروعي الذكي</p>
                        <p>جميع الحقوق محفوظة</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = f"""
            مرحباً {full_name}،
            
            شكراً لتسجيلك في منصة مشروعي الذكي!
            
            كود التفعيل الخاص بك: {code}
            
            هذا الكود صالح لمدة 30 دقيقة فقط.
            
            بعد التفعيل، ستحصل على كلمة مرور مؤقتة يمكنك تغييرها من الإعدادات.
            
            مع تحيات فريق مشروعي الذكي
            """
            
            # إنشاء الرسالة
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            
            # إضافة HTML version
            msg.attach_alternative(html_content, "text/html")
            
            # إرسال الرسالة
            msg.send()
            
            logger.info(f"Activation email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending activation email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def send_password_email(email: str, full_name: str, password: str) -> bool:
        """
        إرسال إيميل كلمة المرور المؤقتة
        
        Args:
            email: البريد الإلكتروني
            full_name: الاسم الكامل
            password: كلمة المرور المؤقتة
            
        Returns:
            bool: True إذا تم الإرسال بنجاح
        """
        try:
            subject = 'كلمة المرور المؤقتة - مشروعي الذكي'
            
            html_content = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f4f7fa;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 10px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .greeting {{
                        font-size: 20px;
                        color: #333;
                        margin-bottom: 20px;
                    }}
                    .message {{
                        font-size: 16px;
                        color: #666;
                        line-height: 1.6;
                        margin-bottom: 30px;
                    }}
                    .password-box {{
                        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                        border: 2px solid #28a745;
                        border-radius: 10px;
                        padding: 25px;
                        text-align: center;
                        margin: 30px 0;
                    }}
                    .password {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #28a745;
                        letter-spacing: 2px;
                        margin: 10px 0;
                        font-family: 'Courier New', monospace;
                    }}
                    .password-label {{
                        font-size: 14px;
                        color: #666;
                        margin-bottom: 10px;
                    }}
                    .success {{
                        background-color: #d4edda;
                        border-right: 4px solid #28a745;
                        padding: 15px;
                        margin: 20px 0;
                        border-radius: 5px;
                    }}
                    .success p {{
                        margin: 0;
                        color: #155724;
                        font-size: 14px;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border-right: 4px solid #ffc107;
                        padding: 15px;
                        margin: 20px 0;
                        border-radius: 5px;
                    }}
                    .warning p {{
                        margin: 0;
                        color: #856404;
                        font-size: 14px;
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        padding: 20px 30px;
                        text-align: center;
                        font-size: 14px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ تم تفعيل حسابك بنجاح!</h1>
                    </div>
                    
                    <div class="content">
                        <div class="greeting">
                            🎉 مبروك {full_name}!
                        </div>
                        
                        <div class="success">
                            <p>✓ تم تفعيل حسابك بنجاح في منصة <strong>مشروعي الذكي</strong></p>
                        </div>
                        
                        <div class="message">
                            <p>يمكنك الآن تسجيل الدخول باستخدام بريدك الإلكتروني وكلمة المرور المؤقتة التالية:</p>
                        </div>
                        
                        <div class="password-box">
                            <div class="password-label">كلمة المرور المؤقتة</div>
                            <div class="password">{password}</div>
                        </div>
                        
                        <div class="warning">
                            <p>⚠️ <strong>مهم جداً:</strong> يرجى تغيير كلمة المرور المؤقتة فور تسجيل الدخول من صفحة الإعدادات.</p>
                        </div>
                        
                        <div class="message">
                            <p><strong>خطوات تسجيل الدخول:</strong></p>
                            <ol style="color: #666; line-height: 1.8;">
                                <li>افتح صفحة تسجيل الدخول</li>
                                <li>أدخل بريدك الإلكتروني: <strong>{email}</strong></li>
                                <li>أدخل كلمة المرور المؤقتة أعلاه</li>
                                <li>اذهب إلى الإعدادات وقم بتغيير كلمة المرور</li>
                            </ol>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>© 2025 SmartEduProject - مشروعي الذكي</p>
                        <p>نتمنى لك تجربة رائعة!</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            مبروك {full_name}!
            
            تم تفعيل حسابك بنجاح في منصة مشروعي الذكي.
            
            كلمة المرور المؤقتة: {password}
            
            البريد الإلكتروني: {email}
            
            يرجى تغيير كلمة المرور المؤقتة فور تسجيل الدخول من صفحة الإعدادات.
            
            مع تحيات فريق مشروعي الذكي
            """
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Password email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending password email to {email}: {str(e)}")
            return False


# إنشاء نسخة واحدة من EmailService
email_service = EmailService()
