# github code
# Run: pip install flask requests pyyaml
from flask import Flask, request, Response
import sqlite3
import os
import requests
import hashlib
import random
import pickle
import yaml

app = Flask(__name__)

API_KEY = "sk_live_very_secret_value"

def get_db():
    conn = sqlite3.connect("test.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users(name TEXT, bio TEXT)")
    return conn

@app.route("/xss")
def xss():
    user = request.args.get("q", "")
    html = f"<html><body>Search: {user}</body></html>"
    return Response(html, mimetype="text/html")

@app.route("/sql")
def sql_injection():
    name = request.args.get("name", "")
    conn = get_db()
    cur = conn.cursor()
    q = f"SELECT name, bio FROM users WHERE name = '{name}'"
    cur.execute(q)
    rows = cur.fetchall()
    return {"rows": rows, "query": q}

@app.route("/cmd")
def cmd_injection():
    c = request.args.get("c", "echo hello")
    os.system(c)
    return {"status": "executed", "cmd": c}

@app.route("/file")
def path_traversal():
    p = request.args.get("path", "/etc/hostname")
    try:
        with open(p, "r") as f:
            return {"path": p, "data": f.read(200)}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/ssrf")
def ssrf():
    url = request.args.get("url", "http://127.0.0.1:80")
    r = requests.get(url, timeout=2)
    return {"status": r.status_code, "len": len(r.content)}

@app.route("/token")
def weak_crypto_random():
    user = request.args.get("user", "guest")
    token = random.random()
    md5 = hashlib.md5(user.encode()).hexdigest()
    return {"token": token, "md5": md5, "note": "weak"}

@app.route("/pickle", methods=["POST"])
def insecure_pickle():
    data = request.data
    obj = pickle.loads(data)
    return {"type": str(type(obj))}

@app.route("/yaml", methods=["POST"])
def insecure_yaml():
    content = request.data.decode("utf-8")
    obj = yaml.load(content, Loader=yaml.Loader)
    return {"loaded": str(obj)}

@app.route("/leak")
def leak():
    return {"debug_key": API_KEY}

@app.route("/")
def index():
    return {
        "endpoints": [
            "/xss?q=<script>alert(1)</script>",
            "/sql?name=admin' OR '1'='1",
            "/cmd?c=cat%20/etc/passwd",
            "/file?path=../../etc/hosts",
            "/ssrf?url=http://127.0.0.1:80",
            "/token?user=alice",
            "/pickle (POST raw pickle)",
            "/yaml (POST YAML)",
            "/leak"
        ]
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
