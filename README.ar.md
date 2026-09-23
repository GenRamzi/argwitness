# ArgWitness

**لا تكتفِ بقول إن تغيير الأداة كاسر؛ اعرض الاستدعاء الذي يكسره.**

[English](README.md)

أداة مفتوحة المصدر تفحص تعريفات أدوات الذكاء الاصطناعي. تبحث عن مدخلات JSON يقبلها التعريف القديم ويرفضها الجديد، وتقلّص المثال لتسهيل مراجعته. تدعم ملفات أدوات MCP وOpenAI وAnthropic، بالإضافة إلى ملفات MCP Description (`mcpdesc`) ولقطات mcp-contracts، دون استدعاء خوادم أو نماذج أو الحاجة لمفتاح API.

مثلًا: إذا خفضت الحد الأقصى لعدد نتائج البحث من 100 إلى 20، فقد يصبح استدعاء قديم صالح مكسورًا. تعطيك ArgWitness هذا الاستدعاء وتعيد التحقق منه مقابل التعريفين.

## التشغيل

تحتاج Python 3.10 أو أحدث. ثبّت الإصدار العام من PyPI:

```bash
python -m pip install argwitness
argwitness --version
```

ولتجربة مثال المستودع من المصدر:

```bash
git clone https://github.com/GenRamzi/argwitness.git
cd argwitness
python -m pip install .
python examples/demo.py
```

التثبيت يحتاج تنزيل الاعتماديات، ثم يعمل التحليل محليًا دون استدعاء خدمات أو نماذج.

```bash
argwitness compare examples/before.mcp.json examples/after.mcp.json --show-values
argwitness replay examples/after.mcp.json examples/calls.jsonl
argwitness verify examples/before.mcp.json examples/after.mcp.json examples/witness.json

# لملف mcpdesc متعدد إصدارات البروتوكول:
argwitness normalize server.mcpdesc.json --protocol-version 2026-07-28
```

الأمر `replay` يفحص المدخلات المسجلة فقط ولا ينفذ الاستدعاءات. لا تستخدم `--show-values` مع بيانات خاصة تريد إخفاءها؛ القيم محذوفة من التقارير افتراضيًا، لكن أسماء الأدوات ومسارات الحقول تبقى ظاهرة.

## معنى النتيجة

| الحالة | المعنى |
| --- | --- |
| `breaking` | مثال مثبت على مدخلات صارت مرفوضة، أو إزالة أداة |
| `review` | تغيير يحتاج مراجعة؛ غياب مثال كاسر لا يثبت التوافق |
| `unchanged` | التعريفات والبيانات الوصفية لم تتغير؛ لم نختبر السلوك الفعلي |
| `added` | أضيفت أدوات مع بقاء الأدوات السابقة دون تغيير |

هذه نسخة أولية `0.3.0`. تستخدم JSON Schema Draft 2020-12. وعند وجود نسخ متعددة من الأداة نفسها داخل ملف `mcpdesc` متعدد البروتوكولات يجب تحديد النسخة صراحةً عبر `--protocol-version`. لا تثبت صحة منطق الخادم أو أمانه، ولا تختبر جودة اختيار النموذج للأداة. البحث محدود، وتبقى التغييرات المعقدة بحاجة إلى أمثلة فعلية أو مراجعة بشرية.

التفاصيل والحدود والاختبارات في [README الإنجليزي](README.md). الترخيص MIT.
