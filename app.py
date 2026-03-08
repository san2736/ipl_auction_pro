import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import psycopg2
from datetime import datetime, timedelta

app = Flask(__name__)
socketio = SocketIO(app)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)


@app.route("/")
def index():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT id,name,role,base_price,image
    FROM players
    ORDER BY name
    """)

    players = cur.fetchall()

    cur.execute("SELECT name,purse FROM teams")
    teams = cur.fetchall()

    conn.close()

    return render_template("auction.html",players=players,teams=teams)



@socketio.on("place_bid")
def place_bid(data):

    player_id = data["player_id"]
    team = data["team"]
    bid = data["bid"]

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO bids(player_id,team,bid_amount)
    VALUES(%s,%s,%s)
    """,(player_id,team,bid))

    conn.commit()

    cur.execute("""
    SELECT team,bid_amount
    FROM bids
    WHERE player_id=%s
    ORDER BY bid_amount DESC
    LIMIT 10
    """,(player_id,))

    bids = cur.fetchall()

    conn.close()

    emit("bid_update",{"bids":bids,"bid":bid,"team":team},broadcast=True)



@socketio.on("start_timer")
def start_timer(data):

    duration = data["seconds"]

    end_time = datetime.utcnow() + timedelta(seconds=duration)

    emit("timer_started",{"end":end_time.timestamp()},broadcast=True)



if __name__ == "__main__":
    socketio.run(app,host="0.0.0.0",port=5000)
