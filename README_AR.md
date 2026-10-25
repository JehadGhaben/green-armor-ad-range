<div align="center">

<img src="assets/cover.svg" alt="GREEN ARMOR ACADEMY — Operation Directory" width="100%" />

# GREEN ARMOR AD RANGE
### OPERATION DIRECTORY

مختبر Active Directory تدريبي خفيف باستخدام Docker

**إعداد وتطوير: JEHAD GHABEN — GREEN ARMOR ACADEMY**

[English README](README.md) · [تاسك الطلاب](docs/STUDENT_TASK.md) · [المعمارية](docs/ARCHITECTURE.md) · [حلول مشاكل التشغيل](docs/TROUBLESHOOTING.md)

</div>

---

## فكرة اللاب

بيئة صغيرة ومعزولة لتعليم أساسيات Active Directory عبر **Samba AD**، تضم حاويتين فقط: **Domain Controller** وأدوات الطالب. تتضمن 4 تحديات متسلسلة في SMB وLDAP وكشف بيانات حساب خدمة وصلاحيات الوصول إلى أرشيف محمي.

**تنبيه تقني:** اللاب لا يشغّل Microsoft Windows Server؛ بل يحاكي خدمات الدومين باستخدام Samba. لا يتضمن Windows Workstations أو GPO أو AD CS.

## المتطلبات

- Linux + **Docker Engine** و**Docker Compose v2** (مفضل).
- Python 3.9+، واتصال بالإنترنت لبناء الصور أول مرة.
- نحو 2 GB RAM فارغة و3 GB من مساحة القرص كتقدير مبدئي غير مقاس.
- على Parrot: إذا ظهر `Emulate Docker CLI using podman` فهذا يعني أنك تستخدم Podman بدل Docker الفعلي؛ وقد تختلف التوافقية.

## تثبيت وتشغيل المختبر

**بعد إنشاء مستودع GitHub عام جديد ورفع الملفات إليه** (الاسم المقترح: `green-armor-ad-range`):

```bash
git clone https://github.com/JehadGhaben/green-armor-ad-range.git
cd green-armor-ad-range
python3 armorlab.py doctor
python3 armorlab.py up
python3 scripts/smoke-test.py
python3 armorlab.py info
python3 armorlab.py shell
```

إذا استلمت ZIP بدل GitHub، فك ضغطه وادخل إلى مجلد `green-armor-ad-range` ونفّذ الأوامر ابتداءً من `doctor`.

**مهم جدًا:** لا ترسل اللاب للطلاب قبل نجاح `smoke-test.py`؛ فهو يفحص SMB وLDAP وإمكانية استخراج الـ4 Flags وحدود الصلاحيات فعليًا.

## بيانات الدخول للطالب

| العنصر | القيمة |
| --- | --- |
| Domain | `ARMOR.TEST` |
| Server | `dc` |
| Username | `ARMOR\student01` |
| Password | `GreenArmor2026!` |

من داخل حاوية الطالب:

```bash
dig @dc _ldap._tcp.armor.test SRV
smbclient -L //dc -U 'ARMOR\student01'
ldapsearch -x -H ldap://dc -D 'student01@armor.test' -W \
  -b 'DC=armor,DC=test' '(objectClass=user)' sAMAccountName description
```

## التحديات

| المرحلة | موضوع المهمة | العلامة |
| --- | --- | ---: |
| 01 | اكتشاف الخدمات وSMB Shares | 15 |
| 02 | استعراض Users وAttributes باستخدام LDAP | 20 |
| 03 | إثبات تسرب بيانات حساب Service Account | 25 |
| 04 | إثبات الوصول لأرشيف مقيد باستخدام صلاحية متسربة | 40 |
| **المجموع** | | **100** |

الـFlags تتغير عند إعادة إنشاء اللاب. نتائج `score` محلية للتدريب الذاتي، وليست وسيلة امتحان تمنع الغش؛ اطلب من الطلاب تقديم أدلة وتقرير بجانب النتائج.

## أوامر المدرّس والطالب (على الجهاز المضيف)

```bash
python3 armorlab.py info
python3 armorlab.py hint 02 1
python3 armorlab.py submit 'GA{...}'
python3 armorlab.py score
python3 armorlab.py status
python3 armorlab.py logs
python3 armorlab.py down
python3 armorlab.py reset --yes
```

**احذر:** `reset --yes` يحذف قاعدة بيانات الدومين والـFlags ونتائج الطلاب، ويولّد قيمًا جديدة في التشغيل القادم.

## التحقق قبل النشر

أضفنا GitHub Actions لاختبار الكود، ثم بناء الحاويات وتشغيل Samba وفحص التحديات الأربعة على Docker فعلي داخل GitHub. بعد الرفع افتح تبويب **Actions** وانتظر نتيجة `real-docker-smoke`؛ علامة النجاح الخضراء مهمة قبل توزيع المشروع. فحص Docker لم يكن ممكنًا داخل بيئة إنشاء الملف؛ لذلك لا تدّعي أن التشغيل مضمون قبل نجاح الاختبار.

**السلامة:** يحتوي اللاب على ضعف أمني متعمد، والشبكة داخل Docker فقط دون منافذ مكشوفة على جهاز المضيف. لا تربطه بشبكة الجامعة أو الشبكات الحقيقية. لا ترفع مجلد `runtime/` أو دليل حلول المدرّس إلى GitHub.

**GREEN ARMOR ACADEMY — JEHAD GHABEN**  
https://www.greenarmor.academy
