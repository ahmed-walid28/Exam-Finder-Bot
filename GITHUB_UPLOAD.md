# 🚀 خطوات رفع البوت على GitHub

## الخطوة 1️⃣: إنشاء حساب GitHub

1. اذهب إلى [github.com](https://github.com)
2. اضغط **Sign up**
3. أكمل بيانات الحساب (email, password, username)
4. تحقق من البريد الإلكتروني

---

## الخطوة 2️⃣: تثبيت Git

### Windows:
1. اذهب إلى [git-scm.com](https://git-scm.com)
2. حمّل Git for Windows
3. شغّل المثبّت واتبع الخطوات الافتراضية
4. أعد تشغيل الـ PowerShell

### تحقق من التثبيت:
```bash
git --version
```

---

## الخطوة 3️⃣: إعداد Git

افتح PowerShell واكتب:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

مثال:
```bash
git config --global user.name "Ahmed"
git config --global user.email "ahmed@example.com"
```

---

## الخطوة 4️⃣: إنشاء Repository على GitHub

1. اذهب إلى [github.com](https://github.com) وسجل الدخول
2. اضغط **+** في الزاوية العلوية اليمين
3. اختر **New repository**
4. أملأ البيانات:

   | الحقل | القيمة |
   |-------|--------|
   | Repository name | `exam-bot` (أو أي اسم) |
   | Description | `Telegram exam information bot` |
   | Public/Private | Public (اختر Public) |
   | Add .gitignore | **لا تختر** (لدينا واحد موجود) |
   | Add a license | اختياري |

5. اضغط **Create repository**

---

## الخطوة 5️⃣: رفع ملفات البوت

افتح PowerShell في مجلد المشروع:

### أ) انسخ الأوامر التالية واحدة تلو الأخرى:

```bash
# تهيئة Git
git init

# إضافة Remote
git remote add origin https://github.com/YOUR_USERNAME/exam-bot.git

# إضافة جميع الملفات
git add .

# التعليق على التغييرات (commit)
git commit -m "Initial commit: Telegram exam bot"

# رفع إلى GitHub
git branch -M main
git push -u origin main
```

### ب) سيطلب منك Username و Password:
- **Username:** اسم المستخدم على GitHub
- **Password:** (إذا كنت تستخدم 2FA، استخدم Personal Access Token بدل Password)

---

## الخطوة 6️⃣: إعداد متغيرات البيئة

### أ) على جهازك محلياً:

1. أنشئ ملف `.env` في مجلد المشروع
2. أضف:
```
BOT_TOKEN=your_actual_bot_token_here
```

3. استبدل `your_actual_bot_token_here` بالتوكن الحقيقي من BotFather

### ب) على Render/Railway (عند الرفع للسحابة):

ستضيف متغيرات البيئة من لوحة التحكم بدل الملف `.env`

---

## الخطوة 7️⃣: التحقق من الرفع

1. اذهب إلى repository على GitHub
2. يجب أن ترى جميع ملفاتك:
   - ✅ `bot.py`
   - ✅ `requirements.txt`
   - ✅ `README.md`
   - ✅ `SETUP.md`
   - ✅ `test_data.py`
   - ✅ `.gitignore`
   - ✅ `.env.example`
   - ✅ `Data/` (المجلد)

---

## 📝 خطوات التحديث المستقبلية

عند إضافة تحديثات للبوت:

```bash
# أضف التعديلات
git add .

# سجل التغيير
git commit -m "وصف التحديث"

# ارفع
git push
```

---

## ⚠️ نقاط مهمة:

### ✅ الملفات التي سيتم رفعها:
- جميع ملفات Python
- `requirements.txt`
- `.env.example` (بدون البيانات الحقيقية)
- `README.md` و `SETUP.md`
- `Data/` (ملفات البيانات)

### ❌ الملفات التي **لن** تُرفع (محمية بـ .gitignore):
- `.env` (الملف الذي يحتوي على البوت توكن الحقيقي)
- `__pycache__/`
- `venv/`
- `*.pyc`

---

## 🔑 الحصول على Personal Access Token (للأمان):

### الطريقة الحديثة (أفضل):

بدل استخدام كلمة المرور، استخدم Personal Access Token:

1. اذهب إلى GitHub Settings → Developer settings → Personal access tokens
2. اضغط **Generate new token**
3. أعطه الصلاحيات: `repo` و `read:user`
4. انسخ التوكن
5. استخدمه بدل كلمة المرور عند الرفع

---

## 🆘 مشاكل شائعة:

### ❌ "fatal: 'origin' does not appear to be a 'git' repository"
```bash
git remote add origin https://github.com/YOUR_USERNAME/exam-bot.git
```

### ❌ "error: src refspec main does not match any"
```bash
git branch -M main
git push -u origin main
```

### ❌ "Permission denied"
تأكد من استخدام SSH key أو Personal Access Token

---

## ✅ بعد الرفع بنجاح:

يمكنك الآن:
1. ✅ نسخ المشروع على أي جهاز: `git clone https://github.com/YOUR_USERNAME/exam-bot.git`
2. ✅ رفع البوت على Render أو Railway
3. ✅ مشاركة الكود مع فريقك
4. ✅ إضافة تحديثات بسهولة

---

## 📚 موارد إضافية:

- [GitHub Hello World](https://guides.github.com/activities/hello-world/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Desktop](https://desktop.github.com/) (إذا كنت تفضل الواجهة الرسومية)

---

**جاهز للرفع! 🚀**
