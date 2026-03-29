from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
from sklearn.ensemble import IsolationForest

app = Flask(__name__)

failed_attempts = {}

# ---- AI MODEL ----
data = [[9],[10],[11],[12],[13],[14],[15],[16]]
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(data)

# ---- USER SYSTEM ----
def load_users():
    users = {}
    try:
        with open("users.txt", "r") as f:
            for line in f:
                u, p = line.strip().split(",")
                users[u] = p
    except:
        pass
    return users

def save_user(username, password):
    with open("users.txt", "a") as f:
        f.write(f"{username},{password}\n")

# ---- LOG SYSTEM ----
def log_event(user, event):
    with open("security_log.txt", "a") as f:
        f.write(f"{datetime.now()} - {user} - {event}\n")

def get_logs():
    try:
        with open("security_log.txt", "r") as f:
            return f.readlines()[-15:]
    except:
        return ["No logs yet"]

def get_stats():
    try:
        with open("security_log.txt", "r") as f:
            lines = f.readlines()
        return [1 if "ANOMALY" in l else 0 for l in lines[-10:]]
    except:
        return [0]

def detect(time):
    return model.predict([[time]])[0] == -1

# ---- UI ----
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Pulse Security</title>
<style>
body {
    background:black;
    color:white;
    font-family:Consolas;
    text-align:center;
}
h1 { color:red; margin-top:60px; }

input {
    display:block;
    margin:10px auto;
    padding:10px;
    width:240px;
    background:#0d0d0d;
    border:1px solid #222;
    color:white;
}

button {
    padding:10px 20px;
    border:1px solid red;
    background:transparent;
    color:red;
    cursor:pointer;
}

button:hover { background:red; color:black; }

.message { margin-top:10px; }

.blink { animation: blink 1s infinite; }
@keyframes blink { 50% {opacity:0;} }

.terminal {
    margin:20px auto;
    width:80%;
    height:180px;
    background:#050505;
    border:1px solid red;
    overflow:auto;
    text-align:left;
    padding:10px;
    font-size:12px;
    color:#00ff9c;
}

.bar {
    height:20px;
    background:red;
    margin:5px;
}
</style>
</head>

<body>

<h1>PULSE SECURITY DASHBOARD</h1>

<form method="POST" onsubmit="setTimeout(clearForm,100);">
<input id="username" name="username" placeholder="Username" required>
<input id="password" name="password" type="password" placeholder="Password" required>
<input id="time" name="time" type="number" placeholder="Login Hour (0-23)" required>
<button type="submit">Login</button>
</form>

<div class="message">{{message|safe}}</div>

<div class="terminal" id="logs">Loading logs...</div>
<div id="graph"></div>

<script>
function clearForm(){
    document.getElementById("username").value="";
    document.getElementById("password").value="";
    document.getElementById("time").value="";
}

function fetchLogs(){
    fetch('/logs')
    .then(res=>res.json())
    .then(data=>{
        document.getElementById("logs").innerHTML=data.logs.join("<br>");
    });
}

function fetchGraph(){
    fetch('/stats')
    .then(res=>res.json())
    .then(data=>{
        let html="";
        data.values.forEach(v=>{
            html += "<div class='bar' style='width:"+ (v*20) +"px'></div>";
        });
        document.getElementById("graph").innerHTML=html;
    });
}

setInterval(fetchLogs,2000);
setInterval(fetchGraph,3000);

fetchLogs();
fetchGraph();
</script>

</body>
</html>
"""

# ---- MAIN ROUTE ----
@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "GET":
        return render_template_string(HTML, message="")

    u = request.form.get("username")
    p = request.form.get("password")
    t = int(request.form.get("time"))

    users = load_users()

    if u not in failed_attempts:
        failed_attempts[u] = 0

    # ---- AUTO REGISTER ----
    if u not in users:
        save_user(u, p)
        log_event(u, "AUTO REGISTERED")
        return render_template_string(
            HTML,
            message="<span style='color:#00ff9c'>✔ New user created & logged in</span>"
        )

    # ---- LOGIN ----
    elif users[u] == p:
        failed_attempts[u] = 0

        if detect(t):
            log_event(u, "ANOMALY LOGIN")
            return render_template_string(
                HTML,
                message="<span class='blink' style='color:yellow'>⚠ Suspicious Login</span>"
            )

        log_event(u, "SUCCESS LOGIN")
        return render_template_string(
            HTML,
            message="<span style='color:#00ff9c'>✔ Login Successful</span>"
        )

    # ---- WRONG PASSWORD ----
    else:
        failed_attempts[u] += 1
        log_event(u, "FAILED LOGIN")

        if failed_attempts[u] >= 3:
            log_event(u, "ATTACK DETECTED")
            return render_template_string(
                HTML,
                message="<span class='blink' style='color:red'>🚨 Fraud Detected</span>"
            )

        return render_template_string(
            HTML,
            message="<span style='color:red'>✖ Wrong Password</span>"
        )

# ---- API ----
@app.route("/logs")
def logs():
    return jsonify({"logs": get_logs()})

@app.route("/stats")
def stats():
    return jsonify({"values": get_stats()})

# ---- RUN ----
if __name__ == "__main__":
    app.run(debug=True)
