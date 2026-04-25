from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import urllib.parse
from flask import Flask, render_template, jsonify

@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    return jsonify({"message": "تم استلام طلبك، سيتم التحقق من الدفع"})

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# عنوان محفظتك
USDT_TRC20_WALLET = "TTDgpsoLSry46z2cXaiXd9uxN8vj8pL3ov"

# الخدمات
SERVICES = [
    {"id": "data-analysis", "name": "Data Analysis Report", "price": 50, "desc": "تحليل بيانات + رسوم بيانية + تقرير PDF"},
    {"id": "dashboard", "name": "Excel / Power BI Dashboard", "price": 80, "desc": "داشبورد احترافي للمبيعات أو المخزون"},
    {"id": "ai-model", "name": "AI / ML Model", "price": 150, "desc": "موديل تنبؤ أو تصنيف باستخدام Python"},
]

# جدول الطلبات
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    service_id = db.Column(db.String(80), nullable=False)
    service_name = db.Column(db.String(160), nullable=False)
    price = db.Column(db.Float, nullable=False)
    note = db.Column(db.Text, nullable=True)
    txid = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(30), default="waiting_payment")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# إنشاء الداتا بيز تلقائياً
@app.before_request
def create_tables():
    db.create_all()

# الصفحة الرئيسية
@app.route("/")
def home():
    return render_template("index.html", services=SERVICES)

# إنشاء طلب
@app.route("/order/<service_id>", methods=["GET", "POST"])
def order(service_id):
    service = next((s for s in SERVICES if s["id"] == service_id), None)
    if not service:
        return "Service not found", 404

    if request.method == "POST":
        new_order = Order(
            customer_name=request.form["customer_name"],
            email=request.form["email"],
            service_id=service["id"],
            service_name=service["name"],
            price=service["price"],
            note=request.form.get("note", "")
        )
        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for("pay", order_id=new_order.id))

    return render_template("order.html", service=service)

# صفحة الدفع (مهم ✅)
@app.route("/pay/<int:order_id>", methods=["GET", "POST"])
def pay(order_id):
    order = Order.query.get_or_404(order_id)

    if request.method == "POST":
        order.txid = request.form.get("txid", "")
        order.status = "payment_submitted"
        db.session.commit()
        flash("تم إرسال رقم التحويل. سيتم التحقق من الدفع قريباً.")
        return redirect(url_for("thanks", order_id=order.id))

    return render_template("pay.html", order=order, wallet=USDT_TRC20_WALLET)

# صفحة الشكر
@app.route("/thanks/<int:order_id>")
def thanks(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("thanks.html", order=order)
@app.route("/send-whatsapp/<int:order_id>")
def send_whatsapp(order_id):
    order = Order.query.get_or_404(order_id)

    phone = "964XXXXXXXXXX"  # غيرها إلى رقمك بدون +
    message = f"""
طلب جديد من Smart Project IQ

رقم الطلب: {order.id}
الاسم: {order.customer_name}
الإيميل: {order.email}
الخدمة: {order.service_name}
السعر: {order.price} USDT
TxID: {order.txid or "-"}
الحالة: {order.status}
"""

    url = "https://wa.me/" + phone + "?text=" + urllib.parse.quote(message)
    return redirect(url)

# لوحة الادمن
@app.route("/admin")
def admin():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin.html", orders=orders)

# تأكيد الدفع
@app.route("/admin/mark-paid/<int:order_id>")
def mark_paid(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = "paid"
    db.session.commit()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)