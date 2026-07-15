# Mission Layer — أول طبقة لازم تشتغل

هذا الكود ينفّذ TASK-011 (Mission Layer Implementation) كأولوية Blocker
قبل أي طبقة تانية، حسب قاعدة NR-002 (Mission Before Product).

## الملفات
- `contracts/mission_contract.py` — تعريف شكل الـ Mission (الحقول المطلوبة والممنوعة)
- `marketing_brain_os/mission_builder.py` — يبني Mission من إجابات المستخدم
- `marketing_brain_os/mission_validator.py` — يتحقق إن الـ Mission مكتمل وسليم
- `marketing_brain_os/mission_repository.py` — يخزن الـ Mission في ملف JSON (data/memory/missions.json)
- `marketing_brain_os/mission_engine.py` — ينسّق كل الخطوات، وفيه الأسئلة الأربعة بالعربي
- `scripts/onboarding_cli.py` — نقطة التشغيل: شغّله تلاقي نفسك بتجاوب على الأسئلة في التيرمينال

## طريقة التشغيل
```
python scripts/onboarding_cli.py
```

ضع هذه الملفات داخل مجلد المشروع الأصلي (Marketing_Brain_OS_1.0) في نفس الأماكن،
فهي تستخدم نفس بنية المجلدات والـ imports الموجودة بالفعل في المشروع.

## ملاحظة مهمة
لا يجوز لأي كود آخر (Acquisition, Research, Strategy...) أن يعمل قبل أن
ينتج هذا الجزء Mission صالح ومحفوظ. أي طبقة تالية يجب أن تقرأ الـ Mission
عبر `MissionRepository().get_latest()` قبل أن تبدأ أي عمل.
