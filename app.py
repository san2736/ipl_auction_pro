from flask import Flask, render_template, request, redirect, session, jsonify
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()


@app.route("/")
def home():

    search = request.args.get("search","")
    role = request.args.get("role","")

    query = "SELECT * FROM players WHERE name ILIKE %s"
    params = [f"%{search}%"]

    if role:
        query += " AND role=%s"
        params.append(role)

    cur.execute(query, params)
    players = cur.fetchall()

    return render_template("index.html", players=players)


@app.route("/player/<id>")
def player(id):

    cur.execute("SELECT * FROM players WHERE id=%s",[id])
    player = cur.fetchone()

    cur.execute("""
    SELECT MAX(bid_amount) FROM bids
    WHERE player_id=%s
    """,[id])

    highest = cur.fetchone()[0]

    if highest is None:
        highest = player[4]

    return render_template("player.html",
                           player=player,
                           highest=highest)


@app.route("/bid/<id>", methods=["POST"])
def bid(id):

    amount = int(request.form["bid"])
    bidder = session.get("user","guest")

    cur.execute("""
    SELECT MAX(bid_amount)
    FROM bids
    WHERE player_id=%s
    """,[id])

    highest = cur.fetchone()[0]

    if highest and amount <= highest:
        return "Bid must be higher"

    cur.execute("""
    INSERT INTO bids(player_id,bid_amount,bidder)
    VALUES(%s,%s,%s)
    """,[id,amount,bidder])

    conn.commit()

    return redirect(f"/player/{id}")


@app.route("/highest_bid/<id>")
def highest_bid(id):

    cur.execute("""
    SELECT MAX(bid_amount)
    FROM bids
    WHERE player_id=%s
    """,[id])

    bid = cur.fetchone()[0]

    return jsonify({"bid":bid})


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        cur.execute("""
        SELECT * FROM users
        WHERE username=%s AND password=%s
        """,[username,password])

        user = cur.fetchone()

        if user:
            session["user"]=username
            return redirect("/")

    return render_template("login.html")


@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        cur.execute("""
        INSERT INTO users(username,password)
        VALUES(%s,%s)
        """,[username,password])

        conn.commit()

        return redirect("/login")

    return render_template("signup.html")


if __name__ == "__main__":
    app.run(debug=True)
