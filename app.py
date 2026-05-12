import os
import random
import string
from flask import Flask, request, redirect, jsonify, render_template, abort
from models import db, Link
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///links.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["BASE_URL"] = os.getenv("BASE_URL", "http://localhost:5000")

db.init_app(app)

with app.app_context():
    db.create_all()


# ── Helpers ────────────────────────────────────────────────────────────────────

def generate_code(length: int = 6) -> str:
    """Generate a random alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if not Link.query.filter_by(short_code=code).first():
            return code


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", base_url=app.config["BASE_URL"])


@app.route("/api/shorten", methods=["POST"])
def shorten():
    data = request.get_json(silent=True) or {}
    original = data.get("url", "").strip()

    if not original:
        return jsonify({"error": "URL is required."}), 400

    # Prepend scheme if missing so the redirect works
    if not original.startswith(("http://", "https://")):
        original = "https://" + original

    # Check if URL already shortened
    existing = Link.query.filter_by(original=original).first()
    if existing:
        return jsonify({
            "short_url": f"{app.config['BASE_URL']}/{existing.short_code}",
            "short_code": existing.short_code,
            "clicks": existing.clicks,
        })

    code = generate_code()
    link = Link(original=original, short_code=code)
    db.session.add(link)
    db.session.commit()

    return jsonify({
        "short_url":  f"{app.config['BASE_URL']}/{code}",
        "short_code": code,
        "clicks":     0,
    }), 201


@app.route("/api/links", methods=["GET"])
def list_links():
    links = Link.query.order_by(Link.created_at.desc()).limit(20).all()
    return jsonify([l.to_dict() for l in links])


@app.route("/api/links/<code>", methods=["DELETE"])
def delete_link(code):
    link = Link.query.filter_by(short_code=code).first_or_404()
    db.session.delete(link)
    db.session.commit()
    return jsonify({"message": "Deleted."})


@app.route("/<code>")
def redirect_link(code):
    link = Link.query.filter_by(short_code=code).first_or_404()
    link.clicks += 1
    db.session.commit()
    return redirect(link.original)


# ── Entry ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
