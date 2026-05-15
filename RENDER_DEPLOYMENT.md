# 🚀 نشر البوت على Render - خطوات نهائية

## ✅ تم إكمال:

- ✅ إنشاء repository على GitHub
- ✅ رفع جميع الملفات
- ✅ إصلاح مشاكل encoding
- ✅ تثبيت جميع المكتبات

---

## 🎯 الخطوات النهائية - نشر على Render:

### الخطوة 1: سجل دخول على Render

1. اذهب إلى: https://render.com
2. اضغط **Sign Up**
3. اختر **GitHub** للتسجيل

### الخطوة 2: أنشئ Web Service جديد

1. من الـ Dashboard، اضغط **New +**
2. اختر **Web Service**
3. اختر **Connect Repository**
4. اختر: `ahmed-walid28/Exam-Finder-Bot`
5. اضغط **Connect**

### الخطوة 3: ملأ البيانات

#### الجزء الأول - المعلومات الأساسية:

| الحقل | القيمة |
|-------|--------|
| **Name** | `Exam-Finder-Bot` |
| **Language** | `Python 3` |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python bot.py` |
| **Region** | `Oregon (US West)` (أو أي منطقة قريبة) |
| **Instance Type** | `Free` (المجاني) |

#### الجزء الثاني - متغيرات البيئة:

1. اضغط **Add Environment Variable**
2. أدخل:
   - **Key:** `BOT_TOKEN`
   - **Value:** `7999344211:AAEOumhsZYYQZ8OLcsKI2f-zg7L68i8LbIg`
3. اضغط **Add**

### الخطوة 4: نشر البوت

1. اضغط الزر الأزرق **Create Web Service**
2. انتظر 2-3 دقائق
3. ستشاهد رسالة النجاح: `Live`

---

## 📱 اختبر البوت بعد النشر:

1. افتح Telegram
2. ابحث عن البوت الخاص بك
3. اكتب `/start`
4. جرب اختيار مادة والبحث عن طالب

---

## 📊 معلومات الرابط:

بعد النشر بنجاح، ستحصل على رابط مثل:
```
https://exam-finder-bot.onrender.com
```

البوت سيعمل **24/7** على هذا الرابط! 🎉

---

## 🔍 استكشاف المشاكل:

### إذا لم يعمل البوت:

1. **تحقق من الـ Logs:**
   - في لوحة Render، اضغط **Logs**
   - ابحث عن رسائل الخطأ

2. **تحقق من متغيرات البيئة:**
   - تأكد من أن `BOT_TOKEN` محفوظ بشكل صحيح

3. **أعد تشغيل الخدمة:**
   - اضغط **Manual Deploy**
   - اختر **Clear Build Cache & Deploy**

---

## 📝 الملفات المهمة:

- `bot.py` - البوت الرئيسي
- `requirements.txt` - المكتبات
- `.env` - البيانات المحلية (محمية بـ .gitignore)
- `Data/` - ملفات الامتحانات

---

## 💡 نصائح:

- ✅ البوت يعمل في الخلفية تلقائياً
- ✅ يمكنك متابعة الـ Logs في الوقت الفعلي
- ✅ البوت يعيد التشغيل تلقائياً عند حدوث خطأ
- ✅ لا تحتاج لأي تكاليف (المستوى المجاني كافي)

---

## 🎓 أنت جاهز الآن!

البوت الخاص بك:
- ✅ مرفوع على GitHub
- ✅ جاهز للنشر على Render
- ✅ يدعم اللغة العربية
- ✅ يعرض معلومات الامتحانات

**استمتع بـ Telegram Bot الخاص بك!** 🚀

---

## 📞 للمساعدة:

- Render Support: https://support.render.com
- GitHub: https://github.com/ahmed-walid28/Exam-Finder-Bot
- Telegram Bot API: https://core.telegram.org/bots

