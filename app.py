from flask import Flask, render_template, request
import psycopg2
import os
import time
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

auction_timer = {}


@app.route("/")
def home():

    cur.execute("SELECT * FROM players")
    players = cur.fetchall()

    return render_template("index.html",players=players)


@app.route("/player/<id>")
def player(id):

    cur.execute("SELECT * FROM players WHERE id=%s",[id])
    player = cur.fetchone()

    cur.execute("""
    SELECT MAX(bid_amount)
    FROM bids
    WHERE player_id=%s
    """,[id])

    highest = cur.fetchone()[0]

    if highest is None:
        highest = player[4]

    return render_template("player.html",
                           player=player,
                           highest=highest)


@app.route("/admin")
def admin():

    cur.execute("SELECT * FROM players")
    players = cur.fetchall()

    return render_template("admin.html",players=players)


@app.route("/start_auction/<player_id>")
def start_auction(player_id):

    auction_timer[player_id] = time.time() + 30

    socketio.emit("auction_started",{
        "player_id":player_id,
        "time":30
    })

    return "Auction Started"


@socketio.on("place_bid")
def place_bid(data):

    player_id = data["player_id"]
    bid = int(data["bid"])
    bidder = data["bidder"]

    cur.execute("""
    SELECT MAX(bid_amount)
    FROM bids
    WHERE player_id=%s
    """,[player_id])

    highest = cur.fetchone()[0]

    if highest and bid <= highest:

        emit("bid_error",{"msg":"Bid must be higher"})
        return

    cur.execute("""
    INSERT INTO bids(player_id,bid_amount,bidder)
    VALUES(%s,%s,%s)
    """,[player_id,bid,bidder])

    conn.commit()

    socketio.emit("new_bid",{
        "player_id":player_id,
        "bid":bid,
        "bidder":bidder
    })


def auction_countdown():

    while True:

        for player_id in list(auction_timer):

            remaining = int(auction_timer[player_id] - time.time())

            if remaining <= 0:

                cur.execute("""
                SELECT bidder,bid_amount
                FROM bids
                WHERE player_id=%s
                ORDER BY bid_amount DESC
                LIMIT 1
                """,[player_id])

                winner = cur.fetchone()

                if winner:

                    bidder = winner[0]
                    price = winner[1]

                    cur.execute("""
                    UPDATE players
                    SET sold=TRUE,
                    sold_price=%s,
                    sold_to=%s
                    WHERE id=%s
                    """,[price,bidder,player_id])

                    cur.execute("""
                    UPDATE teams
                    SET purse = purse - %s
                    WHERE name=%s
                    """,[price,bidder])

                    conn.commit()

                    socketio.emit("player_sold",{
                        "player_id":player_id,
                        "team":bidder,
                        "price":price
                    })

                del auction_timer[player_id]

            else:

                socketio.emit("timer_update",{
                    "player_id":player_id,
                    "time":remaining
                })

        socketio.sleep(1)


socketio.start_background_task(auction_countdown)


if __name__ == "__main__":
    socketio.run(app)
