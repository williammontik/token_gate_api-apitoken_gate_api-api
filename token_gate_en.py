# === token_gate_en.py (English Version, Standalone with Universal Coupon) ===
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, os

app = Flask(__name__)
CORS(app)

DB_FILE = "coupon.db"
UNIVERSAL_COUPONS = {
    "MASTER123": 100,
    "VIP888": 100
}

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS coupons (
        code TEXT PRIMARY KEY,
        max_uses INTEGER,
        used INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route("/token_gate_api", methods=["POST"])
def validate_coupon():
    data = request.get_json()
    code = data.get("coupon", "").strip().upper()

    # Multilingual English responses
    MESSAGES = {
        "invalid": "❌ Invalid code.",
        "used": "❌ This code has been fully used.",
        "error": "⚠️ Server error. Please try again."
    }

    try:
        # Handle universal/master codes
        if code in UNIVERSAL_COUPONS:
            return jsonify({
                "success": True,
                "remaining": UNIVERSAL_COUPONS[code],
                "max_uses": UNIVERSAL_COUPONS[code]
            })

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT max_uses, used FROM coupons WHERE code = ?", (code,))
        row = c.fetchone()

        if not row:
            return jsonify({"success": False, "message": MESSAGES["invalid"]})

        max_uses, used = row
        if used >= max_uses:
            return jsonify({"success": False, "message": MESSAGES["used"]})

        c.execute("UPDATE coupons SET used = used + 1 WHERE code = ?", (code,))
        conn.commit()
        remaining = max_uses - (used + 1)

        return jsonify({
            "success": True,
            "remaining": remaining,
            "max_uses": max_uses
        })

    except Exception:
        return jsonify({"success": False, "message": MESSAGES["error"]})

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # ← Use a unique port for English
