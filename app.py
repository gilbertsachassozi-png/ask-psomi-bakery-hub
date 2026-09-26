from flask import Flask, render_template, request, redirect, url_for
from bakery_engine import process_combined_order, ORDER_DATABASE
from datetime import datetime
import urllib.parse

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    invoice_data = process_combined_order(request.form)
    
    if invoice_data['grand_total'] == 0:
        return "<h3>Error: Please enter a quantity for at least one item before checkout.</h3><a href='/'>Go Back</a>", 400

    phone = request.form.get('phone')
    payment_method = request.form.get('payment_method')
    purchase_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_delivery = invoice_data['needed_by'].replace("T", " ")

    # Generate visual itemized receipt rows
    items_html = ""
    whatsapp_items_text = ""
    for entry in invoice_data['items']:
        items_html += f"<tr><td style='padding:10px 0; border-bottom:1px solid #eee;'>{entry['name']}</td><td style='padding:10px 0; border-bottom:1px solid #eee; text-align:right;'>{entry['cost']:,} UGX</td></tr>"
        whatsapp_items_text += f"- {entry['name']}: {entry['cost']:,} UGX\n"

    # Save order into the live array database for the Admin Panel Tracker
    ORDER_DATABASE.append({
        "timestamp": purchase_timestamp,
        "phone": phone,
        "method": payment_method,
        "items": ", ".join([e['name'] for e in invoice_data['items']]),
        "total": f"{invoice_data['grand_total']:,} UGX",
        "deadline": formatted_delivery
    })

    # Encode WhatsApp metadata string securely
    raw_whatsapp_msg = f"*New Order: Ask Psomi Keik Bakery*\n📍 Lutaba Branch\n⏰ Needed By: {formatted_delivery}\n\n*Summary:*\n{whatsapp_items_text}\n*TOTAL:* {invoice_data['grand_total']:,} UGX\n\n*Client Account:* {phone} ({payment_method})"
    whatsapp_url = f"https://wa.me{urllib.parse.quote(raw_whatsapp_msg)}"

    return f"""
    <div style="font-family:sans-serif; max-width:480px; margin:40px auto; border:1px solid #ebd8c5; padding:30px; background:#fff; border-radius:12px;">
        <center><h2 style="color:#724c2a; margin:0;">ASK PSOMI KEIK BAKERY</h2><p style="color:#8a7665; margin:5px 0 20px 0;">Lutaba Branch</p></center>
        <p style="font-size:14px; color:#5c4632;"><strong>Placed:</strong> {purchase_timestamp}<br><strong>Fulfillment Date:</strong> {formatted_delivery}<br><strong>Account:</strong> {phone} ({payment_method})</p>
        <table style="width:100%; font-size:14px; border-collapse:collapse; margin:20px 0;">
            <tr style="border-bottom:2px solid #ebd8c5; color:#724c2a;"><th style="text-align:left; padding-bottom:5px;">Item Summary</th><th style="text-align:right; padding-bottom:5px;">Subtotal</th></tr>
            {items_html}
        </table>
        <h3 style="text-align:right; color:#724c2a; font-size:18px;">GRAND TOTAL: {invoice_data['grand_total']:,} UGX</h3>
        <div style="background:#eafaf1; padding:12px; border-radius:8px; text-align:center; color:#2e7d32; font-size:13px; margin-bottom:20px;"><strong>Payment Gateway Online:</strong> Mobile Wallet Push Dispatched.</div>
        <center>
            <a href="{whatsapp_url}" target="_blank" style="display:block; padding:12px; background:#25D366; color:white; text-decoration:none; font-weight:bold; border-radius:8px; margin-bottom:12px;">💬 Send Receipt to Bakery Line</a>
            <a href="/" style="color:#8a7665; text-decoration:none; font-size:13px;">← Create New Order Instance</a>
        </center>
    </div>
    """

# --- ADMIN PROFILE LOGISTIC ENDPOINTS ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Setup secure hardcoded admin gate keys matching template credentials
        if username == "admin" and password == "lutaba256":
            return redirect(url_for('admin_dashboard'))
        else:
            return "<h3>Security Authentication Refused: Invalid Credentials.</h3><a href='/admin/login'>Retry Login</a>", 401
    return """
    <div style="font-family:sans-serif; max-width:360px; margin:100px auto; border:1px solid #ebd8c5; padding:30px; background:#fff; border-radius:12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <center><h2 style="color:#724c2a; margin-top:0;">Bakery Administration</h2></center>
        <form method="POST">
            <label style="display:block; margin-bottom:5px; font-weight:bold; font-size:14px;">Username</label>
            <input type="text" name="username" style="width:100%; padding:10px; margin-bottom:15px; border:1px solid #ebd8c5; border-radius:6px; box-sizing:border-box;" required>
            <label style="display:block; margin-bottom:5px; font-weight:bold; font-size:14px;">Password</label>
            <input type="password" name="password" style="width:100%; padding:10px; margin-bottom:20px; border:1px solid #ebd8c5; border-radius:6px; box-sizing:border-box;" required>
            <button type="submit" style="width:100%; background:#724c2a; color:white; border:none; padding:12px; font-weight:bold; border-radius:6px; cursor:pointer;">Secure Dashboard Login</button>
        </form>
    </div>
    """

@app.route('/admin/dashboard')
def admin_dashboard():
    # Build clean metric data rows reading direct from our backend session array
    rows_html = ""
    for idx, order in enumerate(ORDER_DATABASE, 1):
        rows_html += f"""
        <tr style='background: { '#fff' if idx % 2 == 0 else '#faf7f2' };'>
            <td style='padding:12px; border-bottom:1px solid #eee;'>{order['timestamp']}</td>
            <td style='padding:12px; border-bottom:1px solid #eee;'>{order['phone']} ({order['method']})</td>
            <td style='padding:12px; border-bottom:1px solid #eee; color:#555;'>{order['items']}</td>
            <td style='padding:12px; border-bottom:1px solid #eee; font-weight:bold; color:#724c2a;'>{order['total']}</td>
            <td style='padding:12px; border-bottom:1px solid #eee; color:#c0392b;'>{order['deadline']}</td>
        </tr>
        """
    
    if not rows_html:
        rows_html = "<tr><td colspan='5' style='padding:20px; text-align:center; color:#999;'>No production orders logged in active tracking database yet.</td></tr>"

    return f"""
    <div style="font-family:sans-serif; max-width:960px; margin:40px auto; padding:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #724c2a; padding-bottom:15px; margin-bottom:30px;">
            <h2 style="color:#724c2a; margin:0;">📈 Ask Psomi Keik Bakery - Admin Panel</h2>
            <a href="/" style="text-decoration:none; color:#fff; background:#724c2a; padding:8px 16px; border-radius:6px; font-size:14px; font-weight:bold;">View Client Ordering Page</a>
        </div>
        
        <h3>Active Production & Order Dispatch Pipeline (Lutaba Facility)</h3>
        <table style="width:100%; border-collapse:collapse; margin-top:15px; font-size:14px; border:1px solid #ebd8c5; box-shadow: 0 4px 10px rgba(0,0,0,0.02);">
            <thead>
                <tr style="background:#724c2a; color:#fff; text-align:left;">
                    <th style="padding:12px;">Transaction Date</th>
                    <th style="padding:12px;">Client Details</th>
                    <th style="padding:12px;">Products Ordered</th>
                    <th style="padding:12px;">Total Billing</th>
                    <th style="padding:12px;">Required Deadline</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """

if __name__ == '__main__':
    app.run(debug=True)
