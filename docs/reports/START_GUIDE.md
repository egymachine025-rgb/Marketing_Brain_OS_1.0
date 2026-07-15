# Marketing Brain OS — دليل التشغيل الكامل
# ===========================================

## الخطوة 0: امسح البيانات القديمة (مرة واحدة)

افتح PowerShell في مجلد المشروع:

```powershell
cd E:\Marketing_Brain_OS_1.0

# امسح كل البيانات القديمة
Remove-Item -Recurse -Force data/products/*
Remove-Item -Recurse -Force data/raw/telegram/*
Remove-Item -Recurse -Force data/exports/*
Remove-Item -Recurse -Force data/reports/*

# أو استخدم --clean مع الـ Pipeline
python scripts/run_pipeline.py --clean
```

---

## الخطوة 1: شغّل الـ Flask API

افتح **Terminal 1**:

```powershell
cd E:\Marketing_Brain_OS_1.0
python src/api/app.py
```

انتظر حتى يظهر:
```
  MARKETING BRAIN OS — FLASK API
  Endpoint: http://0.0.0.0:5000/api/
  Dashboard: http://0.0.0.0:5000/
```

افتح المتصفح: `http://localhost:5000/`

---

## الخطوة 2: شغّل Telegram Bot

افتح **Terminal 2** (جديد):

```powershell
cd E:\Marketing_Brain_OS_1.0

# ضبط البيانات (مرة واحدة)
$env:TELEGRAM_API_ID="37441228"
$env:TELEGRAM_API_HASH="0e7deb1778b5755c01230e42ac67c2b7"
$env:TELEGRAM_PHONE="+201016320190"
$env:CHANNELS="@cjfhjch4764gd36e,@EgyStore005"

# تشغيل البوت
python src/bot/telegram_bot.py --continuous
```

### أول مرة — Login:
```
Enter login code from Telegram: _____
```

- افتح Telegram على هاتفك
- ستجد رسالة من Telegram بكود
- أدخل الكود في Terminal

إذا طلب 2FA:
```
Enter 2FA password: _____
```

---

## الخطوة 3: تأكد من البيانات

افتح **Terminal 3** (جديد):

```powershell
cd E:\Marketing_Brain_OS_1.0

# شوف القنوات اللي نزلت
Get-ChildItem data/raw/telegram/ -Recurse
```

لازم تشوف:
```
data/raw/telegram/
├── cjfhjch4764gd36e/
│   ├── 000001.json
│   ├── 000002.json
│   └── ...
└── EgyStore005/
    ├── 000001.json
    └── ...
```

---

## الخطوة 4: شغّل الـ Pipeline

في نفس Terminal 3:

```powershell
python scripts/run_pipeline.py
```

انتظر حتى يكتمل:
```
[1/5] Loading Telegram messages...
      Loaded: 25 messages
[2/5] Parsing messages...
      Parsed: 25 messages
[3/5] Building products...
      Products built: 25
[4/5] Running duplicate detection...
      Unique products: 25
      Duplicates found: 0
[5/5] Building dashboard...
      Dashboard products: 25
```

---

## الخطوة 5: refresh الـ Dashboard

في المتصفح (localhost:5000):
- اضغط **🔄 Refresh** أو F5
- لازم تشوف منتجات جديدة حقيقية

---

## 🔄 التشغيل التلقائي (Continuous)

الـ Bot يعمل في background وينزل رسائل جديدة كل 5 دقائق.

كل ما تحتاجه:
1. الـ API شغال (Terminal 1)
2. الـ Bot شغال (Terminal 2)
3. الـ Dashboard يتحدث تلقائياً

---

## ❌ أخطاء شائعة

### الخطأ: "Connection failed: 'NoneType' object has no attribute 'first_name'"
**الحل:** أدخل كود التحقق من Telegram

### الخطأ: "No messages found"
**الحل:** تأكد إن الـ Bot شغال ونزل رسائل

### الخطأ: "0 Unique products, 5 Duplicates"
**الحل:** امسح `data/products/` وشغّل الـ Pipeline من جديد

---

## 📁 الملفات المطلوبة

انسخ هذه الملفات من ZIP لمشروعك:

```
E:\Marketing_Brain_OS_1.0\
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── app.py              ← Flask API
│   └── bot/
│       ├── __init__.py
│       └── telegram_bot.py     ← Telegram Bot
├── scripts/
│   └── run_pipeline.py         ← Pipeline (محدّث)
├── templates/
│   └── dashboard.html          ← Widget
└── .env                        ← بياناتك
```
