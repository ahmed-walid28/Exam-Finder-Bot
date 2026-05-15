# خطوات إعداد البوت 🤖

## خطوة 1️⃣: الحصول على البوت توكن

### أ) فتح Telegram BotFather
1. افتح تطبيق Telegram
2. ابحث عن `@BotFather` (أو انقر على الرابط)
3. ابدأ المحادثة واكتب `/newbot`

### ب) إنشاء البوت
```
/newbot
الرد: ما اسم البوت؟ 
أكتب: ExamInfoBot (أو أي اسم تريده)

الرد: ما معرف البوت (username)؟
أكتب: exam_info_bot_YOURNAME (يجب أن ينتهي بـ bot)
```

### ج) الحصول على التوكن
ستحصل على رسالة تحتوي على:
```
Done! Congratulations on your new bot. You will find it at t.me/your_bot_username. 
You can now add a description, about section and profile picture for your bot, see /help for a list of commands.

Use this token to access the HTTP API:
1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij
```

**العدد الطويل = البوت توكن الخاص بك** 📝

---

## خطوة 2️⃣: تثبيت المكتبات

افتح PowerShell أو Command Prompt وأكتب:
```bash
cd C:\Users\ahmed\سطح المكتب\Exam
pip install -r requirements.txt
```

---

## خطوة 3️⃣: تعديل البوت

### افتح ملف `bot.py`:

ابحث عن هذا السطر (حوالي السطر 92):
```python
application = Application.builder().token("YOUR_BOT_TOKEN_HERE").build()
```

استبدله بـ (ضع التوكن الحقيقي):
```python
application = Application.builder().token("1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij").build()
```

**مثال:**
```python
# قبل:
application = Application.builder().token("YOUR_BOT_TOKEN_HERE").build()

# بعد (مثال):
application = Application.builder().token("1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij").build()
```

---

## خطوة 4️⃣: تشغيل البوت

افتح PowerShell في مجلد المشروع واكتب:
```bash
python bot.py
```

يجب أن تشاهد رسالة:
```
✓ تم تحميل: {12} - (Embedded Systems and Automation) - 8-6-2026 (عدد الطلاب)
✓ تم تحميل: ...

تم تحميل عدد المواد بنجاح

🤖 البوت يعمل الآن... (اضغط Ctrl+C للإيقاف)
```

---

## خطوة 5️⃣: اختبار البوت

1. افتح Telegram
2. ابحث عن البوت الخاص بك (باسم username)
3. اضغط `/start`
4. اتبع الخطوات:
   - اختر المادة
   - أدخل كود الطالب
   - ستحصل على المعلومات 🎉

---

## كود توضيحي 📝

عند اختيار الطالب برمز **4221006** من مادة **Embedded Systems**:

```
✅ تم العثور على البيانات!

📚 المادة: {12} - (Embedded Systems and Automation) - 8-6-2026
👤 اسم الطالب: محمد ابراهيم السيد احمد علي ارز
🆔 كود الطالب: 4221006
📍 مكان الامتحان: Lab 1
🕐 الوقت: 9:30 AM-11:30 AM
```

---

## نصائح مهمة 💡

### ✅ ما يعمل:
- استخدام البوت من أي مكان في العالم
- البحث في أي وقت
- البوت يعمل طالما القائم يعمل البرنامج

### ⚠️ ملاحظات:
- البوت يحتاج للاتصال بالإنترنت
- بيانات الطلاب تُحمّل من ملفات txt في مجلد Data
- الكود يجب أن يكون موجوداً في الملف بالضبط

### 🔄 إيقاف البوت:
اضغط `Ctrl+C` في PowerShell

---

## الملفات المطلوبة ✅

تأكد من وجود هذه الملفات:
```
Exam/
├── bot.py              (البوت الرئيسي)
├── requirements.txt    (المكتبات المطلوبة)
├── README.md          (شرح عام)
├── SETUP.md           (هذا الملف)
└── Data/
    ├── {12} - ... .txt
    ├── {15} - ... .txt
    ├── {2} - ... .txt
    ├── {6} - ... .txt
    ├── {8} - ... .txt
    └── Cloud Architecture and Computing.txt
```

---

## استكشاف الأخطاء 🔧

### ❌ "ModuleNotFoundError: No module named 'telegram'"
**الحل:** اكتب:
```bash
pip install python-telegram-bot
```

### ❌ "Invalid token"
**الحل:** تأكد من نسخ التوكن الصحيح من BotFather بدون مسافات

### ❌ "لا توجد بيانات متاحة"
**الحل:** تأكد من وجود ملفات .txt في مجلد Data بالصيغة الصحيحة

### ❌ "Timeout" أو عدم استجابة البوت
**الحل:** 
1. تأكد من الاتصال بالإنترنت
2. أعد تشغيل البوت: `Ctrl+C` ثم `python bot.py`

---

## معلومات إضافية 📚

- **موقع BotFather:** https://t.me/botfather
- **Telegram API Docs:** https://core.telegram.org/bots
- **python-telegram-bot Docs:** https://python-telegram-bot.readthedocs.io/

---

**جاهز! 🚀 استمتع بالبوت الخاص بك!**
