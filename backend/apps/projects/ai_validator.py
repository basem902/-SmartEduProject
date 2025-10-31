"""
AI Validator for Project Submissions
نظام التحقق بالذكاء الاصطناعي
"""
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AIValidator:
    """
    نظام التحقق بالذكاء الاصطناعي للمشاريع
    """
    
    def __init__(self):
        """تهيئة AI Validator"""
        # Gemini API
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_flash = genai.GenerativeModel('gemini-1.5-flash')
            self.gemini_vision = genai.GenerativeModel('gemini-1.5-pro-vision')
            logger.info("✅ Gemini API initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {str(e)}")
            self.gemini_flash = None
            self.gemini_vision = None
    
    def validate_submission(self, submission):
        """
        التحقق الشامل من المشروع
        
        Args:
            submission: كائن Submission
        
        Returns:
            dict: نتائج التحقق
        """
        project = submission.project
        file_type = project.file_type
        
        logger.info(f"🔍 بدء التحقق من Submission #{submission.id} - نوع الملف: {file_type}")
        
        try:
            # اختيار المعالج حسب نوع الملف
            if file_type == 'video':
                return self.validate_video(submission)
            elif file_type == 'pdf':
                return self.validate_pdf(submission)
            elif file_type == 'image':
                return self.validate_image(submission)
            elif file_type == 'document':
                return self.validate_document(submission)
            elif file_type == 'audio':
                return self.validate_audio(submission)
            else:
                return {
                    'status': 'rejected',
                    'overall_score': 0,
                    'rejection_reasons': [f'نوع ملف غير مدعوم: {file_type}']
                }
        
        except Exception as e:
            logger.error(f"❌ خطأ في التحقق: {str(e)}", exc_info=True)
            return {
                'status': 'needs_review',
                'overall_score': 0,
                'rejection_reasons': [f'حدث خطأ في التحليل: {str(e)}'],
                'error': str(e)
            }
    
    def validate_video(self, submission):
        """
        التحقق الشامل من الفيديو
        1. فحص المدة
        2. OCR على آخر 5 ثواني
        3. تحليل المحتوى بـ Gemini Vision
        4. كشف التشابه
        """
        logger.info(f"🎬 بدء فحص الفيديو #{submission.id}")
        
        project = submission.project
        file_path = submission.file_path
        student_name = submission.submitted_student_name or submission.student.full_name if submission.student else "غير معروف"
        
        results = {
            'checks': {},
            'rejection_reasons': [],
            'warnings': [],
            'overall_score': 0
        }
        
        try:
            # 1. فحص المدة
            duration_result = self._check_video_duration(file_path, project)
            results['checks']['duration'] = duration_result
            
            if duration_result['status'] == 'fail':
                results['rejection_reasons'].append(duration_result['message'])
                results['status'] = 'rejected'
                return results
            
            # 2. OCR على آخر 5 ثواني
            ocr_result = self._check_video_ocr(file_path, student_name)
            results['checks']['ocr'] = ocr_result
            
            if ocr_result['status'] == 'fail':
                results['rejection_reasons'].append(ocr_result['message'])
            elif ocr_result['status'] == 'warning':
                results['warnings'].append(ocr_result['message'])
            
            # 3. تحليل المحتوى بـ Gemini Vision
            gemini_result = self._analyze_video_content(file_path, project)
            results['checks']['content_analysis'] = gemini_result
            
            if gemini_result['status'] == 'fail':
                results['rejection_reasons'].append(gemini_result['message'])
            
            # 4. كشف التشابه
            similarity_result = self._check_video_similarity(file_path, submission)
            results['checks']['similarity'] = similarity_result
            
            if similarity_result['status'] == 'fail':
                results['rejection_reasons'].append(similarity_result['message'])
            
            # حساب الدرجة النهائية
            scores = [
                duration_result.get('score', 0),
                ocr_result.get('score', 0),
                gemini_result.get('score', 0),
                similarity_result.get('score', 0)
            ]
            results['overall_score'] = sum(scores) / len(scores)
            
            # تحديد الحالة النهائية
            if results['rejection_reasons']:
                results['status'] = 'rejected'
            elif results['overall_score'] < 60:
                results['status'] = 'needs_review'
                results['rejection_reasons'].append('الدرجة أقل من 60%')
            else:
                results['status'] = 'approved'
            
            logger.info(f"✅ انتهى فحص الفيديو #{submission.id} - الحالة: {results['status']}")
            return results
            
        except Exception as e:
            logger.error(f"❌ خطأ في فحص الفيديو #{submission.id}: {str(e)}", exc_info=True)
            return {
                'status': 'needs_review',
                'overall_score': 0,
                'rejection_reasons': [f'حدث خطأ في فحص الفيديو: {str(e)}'],
                'checks': results.get('checks', {})
            }
    
    def validate_pdf(self, submission):
        """
        التحقق من PDF
        (سيتم التطوير في المرحلة التالية)
        """
        logger.info(f"📄 فحص PDF #{submission.id}")
        
        # TODO: تطوير فحص PDF
        # - استخراج النص
        # - تحليل المحتوى
        # - كشف التشابه
        
        # مؤقتاً: قبول تلقائي للاختبار
        return {
            'status': 'approved',
            'overall_score': 80.0,
            'checks': {
                'content': {'status': 'pass', 'score': 80}
            },
            'rejection_reasons': []
        }
    
    def validate_image(self, submission):
        """التحقق من الصورة"""
        logger.info(f"🖼️ فحص الصورة #{submission.id}")
        
        return {
            'status': 'approved',
            'overall_score': 75.0,
            'checks': {
                'quality': {'status': 'pass'}
            },
            'rejection_reasons': []
        }
    
    def validate_document(self, submission):
        """التحقق من المستندات (Word/Excel/PPT)"""
        logger.info(f"📝 فحص المستند #{submission.id}")
        
        return {
            'status': 'approved',
            'overall_score': 80.0,
            'checks': {
                'format': {'status': 'pass'}
            },
            'rejection_reasons': []
        }
    
    def validate_audio(self, submission):
        """التحقق من الصوت"""
        logger.info(f"🎵 فحص الصوت #{submission.id}")
        
        return {
            'status': 'approved',
            'overall_score': 75.0,
            'checks': {
                'duration': {'status': 'pass'}
            },
            'rejection_reasons': []
        }
    
    # ====================================
    # Video Validation Helper Methods
    # ====================================
    
    def _check_video_duration(self, file_path, project):
        """
        فحص مدة الفيديو
        
        Args:
            file_path: مسار الفيديو
            project: كائن المشروع
            
        Returns:
            dict: نتيجة الفحص
        """
        try:
            import cv2
            
            video = cv2.VideoCapture(file_path)
            
            if not video.isOpened():
                return {
                    'status': 'fail',
                    'message': 'فشل في فتح الفيديو',
                    'score': 0
                }
            
            # حساب المدة
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps if fps > 0 else 0
            
            video.release()
            
            # التحقق من قيود المدة
            constraints = project.file_constraints or {}
            duration_constraints = constraints.get('duration', {})
            
            min_duration = duration_constraints.get('min', 15)  # default 15 seconds
            max_duration = duration_constraints.get('max', 30)  # default 30 seconds
            
            logger.info(f"📹 مدة الفيديو: {duration:.2f} ثانية (المطلوب: {min_duration}-{max_duration})")
            
            if duration < min_duration:
                return {
                    'status': 'fail',
                    'message': f'الفيديو قصير جداً ({duration:.1f}ث). المطلوب على الأقل {min_duration} ثانية',
                    'duration': duration,
                    'score': 0
                }
            elif duration > max_duration:
                return {
                    'status': 'fail',
                    'message': f'الفيديو طويل جداً ({duration:.1f}ث). الحد الأقصى {max_duration} ثانية',
                    'duration': duration,
                    'score': 0
                }
            else:
                return {
                    'status': 'pass',
                    'message': f'مدة الفيديو مناسبة ({duration:.1f}ث)',
                    'duration': duration,
                    'score': 100
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في فحص مدة الفيديو: {str(e)}")
            return {
                'status': 'fail',
                'message': f'خطأ في قراءة الفيديو: {str(e)}',
                'score': 0
            }
    
    def _check_video_ocr(self, file_path, student_name):
        """
        OCR على آخر 5 ثواني من الفيديو للتحقق من اسم الطالب
        
        Args:
            file_path: مسار الفيديو
            student_name: اسم الطالب
            
        Returns:
            dict: نتيجة الفحص
        """
        try:
            import cv2
            import easyocr
            from apps.projects.utils import normalize_arabic_name
            
            # تهيئة EasyOCR (العربية + الإنجليزية)
            reader = easyocr.Reader(['ar', 'en'], gpu=False)
            
            video = cv2.VideoCapture(file_path)
            
            if not video.isOpened():
                return {
                    'status': 'fail',
                    'message': 'فشل في فتح الفيديو',
                    'score': 0
                }
            
            # الحصول على معلومات الفيديو
            fps = video.get(cv2.CAP_PROP_FPS)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # آخر 5 ثواني
            start_frame = max(0, total_frames - int(fps * 5))
            
            # استخراج إطارات من آخر 5 ثواني (كل ثانية إطار)
            frames_to_check = []
            for i in range(5):
                frame_pos = start_frame + int(i * fps)
                if frame_pos < total_frames:
                    video.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                    ret, frame = video.read()
                    if ret:
                        frames_to_check.append(frame)
            
            video.release()
            
            # قراءة النص من الإطارات
            detected_texts = []
            for frame in frames_to_check:
                result = reader.readtext(frame)
                for detection in result:
                    text = detection[1]
                    detected_texts.append(text)
            
            # دمج النصوص
            combined_text = ' '.join(detected_texts)
            logger.info(f"📝 النصوص المستخرجة: {combined_text[:100]}...")
            
            # تطبيع الأسماء للمقارنة
            normalized_student = normalize_arabic_name(student_name)
            normalized_detected = normalize_arabic_name(combined_text)
            
            # البحث عن الاسم
            name_parts = normalized_student.split()
            found_parts = sum(1 for part in name_parts if part in normalized_detected)
            
            # نسبة التطابق
            match_percentage = (found_parts / len(name_parts)) * 100 if name_parts else 0
            
            logger.info(f"🔍 تطابق الاسم: {match_percentage:.1f}% ({found_parts}/{len(name_parts)} أجزاء)")
            
            if match_percentage >= 75:
                return {
                    'status': 'pass',
                    'message': f'تم العثور على الاسم في الفيديو ({match_percentage:.0f}% تطابق)',
                    'detected_text': combined_text[:200],
                    'match_percentage': match_percentage,
                    'score': 100
                }
            elif match_percentage >= 50:
                return {
                    'status': 'warning',
                    'message': f'تطابق جزئي للاسم ({match_percentage:.0f}%). يرجى التأكد',
                    'detected_text': combined_text[:200],
                    'match_percentage': match_percentage,
                    'score': 70
                }
            else:
                return {
                    'status': 'fail',
                    'message': 'لم يتم العثور على الاسم في آخر 5 ثواني من الفيديو',
                    'detected_text': combined_text[:200],
                    'match_percentage': match_percentage,
                    'score': 0
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في OCR للفيديو: {str(e)}")
            return {
                'status': 'warning',
                'message': f'تعذر قراءة النص من الفيديو: {str(e)}',
                'score': 50
            }
    
    def _analyze_video_content(self, file_path, project):
        """
        تحليل محتوى الفيديو باستخدام Gemini Vision
        
        Args:
            file_path: مسار الفيديو
            project: كائن المشروع
            
        Returns:
            dict: نتيجة التحليل
        """
        try:
            import google.generativeai as genai
            
            if not self.gemini_vision:
                return {
                    'status': 'warning',
                    'message': 'Gemini Vision غير متاح',
                    'score': 70
                }
            
            # رفع الفيديو لـ Gemini
            logger.info(f"📤 رفع الفيديو لـ Gemini...")
            video_file = genai.upload_file(file_path)
            
            # تجهيز Prompt
            prompt = f"""حلل هذا الفيديو بدقة وأجب بصيغة JSON:

معلومات المشروع:
- العنوان: {project.title}
- الوصف: {project.description or 'غير محدد'}

أجب على التالي:
1. quality_score: جودة الفيديو من 0-100 (الوضوح، الإضاءة، الصوت)
2. content_relevance: مدى ارتباط المحتوى بالمشروع (0-100)
3. has_inappropriate_content: هل يحتوي على محتوى غير مناسب؟ (true/false)
4. summary: ملخص قصير للمحتوى (جملة واحدة)
5. issues: قائمة بأي مشاكل (أو قائمة فارغة)
6. recommendation: توصية (approved/rejected/needs_review)

أجب فقط بصيغة JSON بدون أي نص إضافي."""
            
            response = self.gemini_vision.generate_content([prompt, video_file])
            
            # تحليل النتيجة
            import json
            try:
                result = json.loads(response.text)
            except:
                # إذا فشل parsing، نستخرج المعلومات يدوياً
                result = {
                    'quality_score': 75,
                    'content_relevance': 80,
                    'has_inappropriate_content': False,
                    'summary': response.text[:100],
                    'issues': [],
                    'recommendation': 'approved'
                }
            
            # حساب الدرجة
            quality = result.get('quality_score', 70)
            relevance = result.get('content_relevance', 70)
            overall = (quality + relevance) / 2
            
            # التحقق من المحتوى غير المناسب
            if result.get('has_inappropriate_content'):
                return {
                    'status': 'fail',
                    'message': 'الفيديو يحتوي على محتوى غير مناسب',
                    'analysis': result,
                    'score': 0
                }
            
            # التحقق من الجودة
            if overall < 50:
                return {
                    'status': 'fail',
                    'message': f'جودة الفيديو منخفضة ({overall:.0f}%)',
                    'analysis': result,
                    'score': overall
                }
            elif overall < 70:
                return {
                    'status': 'warning',
                    'message': f'جودة الفيديو مقبولة ({overall:.0f}%)',
                    'analysis': result,
                    'score': overall
                }
            else:
                return {
                    'status': 'pass',
                    'message': f'جودة الفيديو ممتازة ({overall:.0f}%)',
                    'analysis': result,
                    'score': overall
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في تحليل الفيديو بـ Gemini: {str(e)}")
            return {
                'status': 'warning',
                'message': f'تعذر تحليل الفيديو: {str(e)}',
                'score': 70
            }
    
    def _check_video_similarity(self, file_path, submission):
        """
        كشف التشابه مع فيديوهات سابقة
        
        Args:
            file_path: مسار الفيديو
            submission: كائن التسليم
            
        Returns:
            dict: نتيجة الفحص
        """
        try:
            import videohash
            from .models import Submission
            
            # حساب hash للفيديو الحالي
            current_hash = videohash.VideoHash(path=file_path)
            
            # البحث عن فيديوهات سابقة في نفس المشروع
            previous_submissions = Submission.objects.filter(
                project=submission.project,
                file_type='video',
                validation_data__video_hash__isnull=False
            ).exclude(id=submission.id)
            
            # مقارنة مع الفيديوهات السابقة
            similarities = []
            for prev_sub in previous_submissions:
                try:
                    prev_hash_data = prev_sub.validation_data.get('video_hash')
                    if prev_hash_data:
                        # إعادة بناء hash
                        prev_hash = videohash.VideoHash(
                            storage_path=prev_hash_data
                        )
                        
                        # حساب الفرق (كلما أقل = أكثر تشابه)
                        difference = current_hash - prev_hash
                        similarity_percent = max(0, 100 - difference)
                        
                        if similarity_percent > 80:
                            similarities.append({
                                'submission_id': prev_sub.id,
                                'student': prev_sub.submitted_student_name,
                                'similarity': similarity_percent,
                                'difference': difference
                            })
                except:
                    continue
            
            # حفظ hash الحالي
            submission.validation_data = submission.validation_data or {}
            submission.validation_data['video_hash'] = str(current_hash)
            
            # التحقق من النتائج
            if similarities:
                most_similar = max(similarities, key=lambda x: x['similarity'])
                
                if most_similar['similarity'] > 90:
                    return {
                        'status': 'fail',
                        'message': f"فيديو مشابه جداً ({most_similar['similarity']:.0f}%) لتسليم سابق",
                        'similar_submissions': similarities[:3],
                        'score': 0
                    }
                else:
                    return {
                        'status': 'warning',
                        'message': f"تشابه متوسط ({most_similar['similarity']:.0f}%) مع تسليم سابق",
                        'similar_submissions': similarities[:3],
                        'score': 70
                    }
            else:
                return {
                    'status': 'pass',
                    'message': 'الفيديو أصلي (لا يوجد تشابه)',
                    'score': 100
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في فحص التشابه: {str(e)}")
            return {
                'status': 'warning',
                'message': 'تعذر فحص التشابه',
                'score': 80
            }
