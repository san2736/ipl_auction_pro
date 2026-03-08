import os
from flask import Flask, render_template, jsonify
import psycopg2
from psycopg2 import pool
from datetime import datetime, timedelta

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

connection_pool = psycopg2.pool.SimpleConnectionPool(
    1,
    10,
    DATABASE_URL
)

def get_conn():
    return connection_pool.getconn()

def release_conn(conn):
    connection_pool.putconn(conn)


@app.route("/")
def players():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT id,name,role,base_price,image
    FROM players
    ORDER BY name
    """)

    players = cur.fetchall()

    release_conn(conn)

    return render_template("players.html", players=players)


@app.route("/start_auction/<int:player_id>")
def start_auction(player_id):

    conn = get_conn()
    cur = conn.cursor()

    end_time = datetime.utcnow() + timedelta(seconds=30)

    cur.execute("""
    UPDATE players
    SET auction_end=%s
    WHERE id=%s
    """,(end_time,player_id))

    conn.commit()

    release_conn(conn)

    return "Auction Started"


@app.route("/bid_history/<int:player_id>")
def bid_history(player_id):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT team,bid_amount
    FROM bids
    WHERE player_id=%s
    ORDER BY bid_amount DESC
    LIMIT 10
    """,(player_id,))

    bids = cur.fetchall()

    release_conn(conn)

    return jsonify({"bids":bids})


@app.route("/teams")
def teams():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT name,purse
    FROM teams
    ORDER BY purse DESC
    """)

    teams = cur.fetchall()

    release_conn(conn)

    return jsonify({"teams":teams})


if __name__ == "__main__":
    app.run(debug=True)
