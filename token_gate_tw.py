# === token_gate_tw.py (Traditional Chinese + Universal Coupon) ===
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, os

app = Flask(__name__)
CORS(app)

DB_FILE = "coupon.db"
MASTER_CODES = ["MASTER123", "VIP888"]
MASTER_LIMIT = 100

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS coupons (
        code TEXT PRIMARY KEY,
        max_uses INTEGER,
        used INTEGER DEFAULT 0
    )''')
    for master in MASTER_CODES:
        c.execute("INSERT OR IGNORE INTO coupons (code, max_uses, used) VALUES (?, ?, 0)", (master, MASTER_LIMIT))
    conn.commit()
    conn.close()

init_db()

@app.route("/token_gate_api", methods=["POST"])
def validate_coupon():
    data = request.get_json()
    code = data.get("coupon", "").strip().upper()
    lang = "tw"

    messages = {
        "invalid": "❌ 無效的通行碼。",
        "used": "❌ 此通行碼已被用完。",
        "error": "⚠️ 伺服器錯誤，請稍後再試。"
    }

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT max_uses, used FROM coupons WHERE code = ?", (code,))
        row = c.fetchone()

        if not row:
            return jsonify({"success": False, "message": messages["invalid"]})

        max_uses, used = row
        if used >= max_uses:
            return jsonify({"success": False, "message": messages["used"]})

        c.execute("UPDATE coupons SET used = used + 1 WHERE code = ?", (code,))
        conn.commit()
        remaining = max_uses - (used + 1)

        return jsonify({
            "success": True,
            "remaining": remaining,
            "max_uses": max_uses
        })

    except:
        return jsonify({"success": False, "message": messages["error"]})

if __name__ == "__main__":
    app.run(debug=True, port=5002)
