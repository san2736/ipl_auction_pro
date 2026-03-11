# IPL Mega Auction 2025 🏏

A real-time IPL auction platform with live bidding, admin controls, player stats, and Socket.IO-powered live updates.

---

## Features

- **Real-time bidding** via Socket.IO — bids appear instantly across all browsers
- **16 pre-seeded IPL players** with full stats (strike rate, batting avg, wickets, etc.)
- **Admin dashboard** — put players live, sell, mark unsold, add new players
- **User login/register** — each user gets ₹1000 Cr budget
- **Filters** — by role, nationality, status, sort by strike rate (ascending only), batting avg
- **Player detail pages** — full stats, bid history, live bidding
- **Bid validation** — bids cannot go lower than the current highest bid
- **Responsive** dark-themed UI inspired by professional auction sites

---

## Local Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create PostgreSQL database locally (pgAdmin4 or psql)
createdb ipl_auction

# 4. Set environment variable
export DATABASE_URL=postgresql://localhost/ipl_auction
export SECRET_KEY=your-secret-key

# 5. Run
python app.py
```

Visit http://localhost:5000

Admin login: **admin / admin123**

---

## Deploy to Render (with pgAdmin4 / PostgreSQL)

### Step 1: Create PostgreSQL Database on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Name: `ipl-auction-db`
4. Region: Singapore (closest to India)
5. Plan: **Free**
6. Click **Create Database**
7. Copy the **External Database URL** (starts with `postgresql://`)

### Step 2: Connect with pgAdmin4

1. Open pgAdmin4
2. Right-click **Servers** → **Register → Server**
3. **General tab:**
   - Name: `Render IPL DB`
4. **Connection tab:**
   - Host: (from Render DB → Hostname field, e.g. `dpg-xxxx.oregon-postgres.render.com`)
   - Port: `5432`
   - Database: `ipl_auction` (or whatever Render shows)
   - Username: (from Render DB → Username field)
   - Password: (from Render DB → Password field)
5. **SSL tab:** set SSL mode to **Require**
6. Click Save

You'll now see your Render DB in pgAdmin4. Tables will appear after first deploy.

### Step 3: Deploy Web Service on Render

1. Push your code to GitHub
2. Go to https://dashboard.render.com → **New + → Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Name:** `ipl-auction`
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$PORT`
5. **Environment Variables:**
   - `DATABASE_URL` = (paste the Internal Database URL from your Render PostgreSQL)
   - `SECRET_KEY` = any random string (e.g. `ipl-auction-super-secret-2025`)
6. Click **Create Web Service**

### Step 4: Initialize Database & Create Admin

After deployment, open the **Shell** tab in Render and run:

```bash
python -c "
from app import app, db, create_admin
with app.app_context():
    db.create_all()
    create_admin()
    print('Done!')
"
```

Then visit your site URL → Login as **admin / admin123** → Click **Seed Players**

---

## Using the Auction

### As Admin:
1. Login as `admin` / `admin123`
2. Go to `/admin`
3. Click **Seed Players** (first time only)
4. Click **▶ LIVE** next to any player to start their auction
5. Users can now bid in real-time
6. Click **✓ SELL** to close at highest bid, or **✗ UNSOLD** to pass

### As User:
1. Register at `/register` (get ₹1000 Cr budget)
2. Browse players at `/players` — filter by role, nationality, sort by strike rate
3. Click any player for detailed stats and bid history
4. Go to `/auction` when a player is live and place bids
5. Bid must always be higher than current highest bid

---

## File Structure

```
ipl_auction/
├── app.py              # Main Flask app (models, routes, SocketIO)
├── requirements.txt
├── Procfile            # For Render
├── render.yaml         # Render blueprint (optional)
└── templates/
    ├── base.html       # Nav, layout, flash messages
    ├── index.html      # Homepage with stats & featured players
    ├── players.html    # Player listing with filters
    ├── player_detail.html  # Individual player + bidding
    ├── auction.html    # Live auction room
    ├── admin.html      # Admin dashboard
    ├── login.html
    └── register.html
```

---

## Notes

- Socket.IO requires **1 worker** in gunicorn (eventlet mode). Do not increase workers.
- Free Render PostgreSQL databases expire after 90 days — upgrade to paid for production.
- The wallet balance is deducted when admin marks a player as sold.
- Strike rate filter sorts **highest to lowest** (best strike rate first) as requested.
