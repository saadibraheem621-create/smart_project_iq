# Smart Project IQ

موقع بسيط لبيع خدمات تحليل البيانات والبرمجة مع دفع USDT عبر Binance.

## التشغيل

1. افتح المجلد في VS Code
2. افتح Terminal
3. نفذ:

```bash
pip install -r requirements.txt
python app.py
```

4. افتح المتصفح على:

```text
http://127.0.0.1:5000
```

## تغيير عنوان المحفظة

افتح ملف `app.py` وبدل:

```python
PUT_YOUR_USDT_TRC20_ADDRESS_HERE
```

بعنوان محفظتك USDT TRC20 من Binance.

## ملاحظات أمان

- لا تضع API Secret داخل الكود.
- لا تشارك Seed Phrase أو Private Key.
- هذا النظام يبدأ بتأكيد دفع يدوي من لوحة admin.
- لاحقاً يمكن إضافة تحقق تلقائي عبر Blockchain API أو بوابة دفع Crypto.
