from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ضع هنا عنوان محفظتك USDT TRC20 من Binance
import os

USDT_TRC20_WALLET = os.environ.get("WALLET")

SERVICES = [
    {"id": "data-analysis", "name": "Data Analysis Report", "price": 50, "desc": "تحليل بيانات + رسوم بيانية + تقرير PDF"},
    {"id": "dashboard", "name": "Excel / Power BI Dashboard", "price": 80, "desc": "داشبورد احترافي للمبيعات أو المخزون"},
    {"id": "ai-model", "name": "AI / ML Model", "price": 150, "desc": "موديل تنبؤ أو تصنيف باستخدام Python"},
]

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

@app.before_request
def create_tables():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html", services=SERVICES)

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

@app.route("/thanks/<int:order_id>")
def thanks(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("thanks.html", order=order)

@app.route("/admin")
def admin():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin.html", orders=orders)

@app.route("/admin/mark-paid/<int:order_id>")
def mark_paid(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = "paid"
    db.session.commit()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
