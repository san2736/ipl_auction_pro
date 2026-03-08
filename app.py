from flask import Flask, render_template, request, redirect, jsonify
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


@app.route("/")
def index():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT p.id,p.name,p.role,p.country,p.base_price,
    COALESCE(MAX(b.bid_amount),0)
    FROM players p
    LEFT JOIN bids b ON p.id=b.player_id
    GROUP BY p.id
    """)

    players = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", players=players)


@app.route("/player/<id>")
def player(id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM players WHERE id=%s",(id,))
    player = cur.fetchone()

    cur.execute("SELECT MAX(bid_amount) FROM bids WHERE player_id=%s",(id,))
    highest = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template("player.html",player=player,highest=highest)


@app.route("/bid",methods=["POST"])
def bid():

    player_id = request.form["player_id"]
    amount = int(request.form["amount"])
    bidder = request.form["bidder"]

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT MAX(bid_amount) FROM bids WHERE player_id=%s",(player_id,))
    highest = cur.fetchone()[0] or 0

    if amount <= highest:
        return "Bid must be higher"

    cur.execute(
    "INSERT INTO bids(player_id,bid_amount,bidder) VALUES(%s,%s,%s)",
    (player_id,amount,bidder)
    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect(f"/player/{player_id}")


@app.route("/highest/<id>")
def highest(id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT MAX(bid_amount) FROM bids WHERE player_id=%s",(id,))
    bid = cur.fetchone()[0] or 0

    cur.close()
    conn.close()

    return jsonify({"bid":bid})


if __name__ == "__main__":
    app.run(debug=True)