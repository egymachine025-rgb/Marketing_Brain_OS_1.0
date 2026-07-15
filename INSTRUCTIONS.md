# Marketing Brain OS — API Integration Guide
# ===========================================

## Where to place these files in your existing project

Your project structure (E:\Marketing_Brain_OS_1.0):
```
Marketing_Brain_OS_1.0/
├── marketing_brain_os/          ← Existing package
├── src/                         ← Existing source
│   ├── acquisition/
│   ├── api/                     ← [NEW] Place app.py here
│   ├── bot/                     ← [NEW] Place telegram_bot.py here
│   ├── core/
│   ├── models/
│   └── ...
├── scripts/                     ← Existing scripts
├── data/                        ← Existing data
├── templates/                   ← [NEW] Create this folder
├── static/                      ← [NEW] Create this folder
├── .env                         ← [NEW] Environment variables
└── ...
```

## File Placement

| File | Destination | Action |
|------|-------------|--------|
| `src/api/app.py` | `E:\Marketing_Brain_OS_1.0\src\api\app.py` | Create folder `src/api/` if not exists |
| `src/api/__init__.py` | `E:\Marketing_Brain_OS_1.0\src\api\__init__.py` | Create |
| `src/bot/telegram_bot.py` | `E:\Marketing_Brain_OS_1.0\src\bot\telegram_bot.py` | Create folder `src/bot/` if not exists |
| `src/bot/__init__.py` | `E:\Marketing_Brain_OS_1.0\src\bot\__init__.py` | Create |
| `templates/dashboard.html` | `E:\Marketing_Brain_OS_1.0\templates\dashboard.html` | Create folder `templates/` |
| `.env` | `E:\Marketing_Brain_OS_1.0\.env` | Create |
| `requirements.txt` | Add to existing or merge | Install: `pip install flask flask-cors python-dotenv` |

## Configure .env

Edit `.env` and update:
```env
TELEGRAM_PHONE=+966YOUR_PHONE_NUMBER
CHANNELS=@cjfhjch4764gd36e,@EgyStore005
```

## Running the System

### Step 1: Install new dependencies
```bash
pip install flask flask-cors python-dotenv
```

### Step 2: Start the Flask API
```bash
# From project root (E:\Marketing_Brain_OS_1.0)
python src/api/app.py --host 0.0.0.0 --port 5000
```

### Step 3: Open the Dashboard
Open browser to: `http://localhost:5000/`

### Step 4: Start Telegram Bot (in new terminal)
```bash
# From project root
python src/bot/telegram_bot.py --continuous
```

The bot will automatically read credentials from `.env` and scan:
- @cjfhjch4764gd36e
- @EgyStore005

## API Endpoints

Once running, the API is available at:
- Dashboard: `http://localhost:5000/`
- API Base: `http://localhost:5000/api/`
- Health: `http://localhost:5000/api/health`
- Products: `http://localhost:5000/api/products`
- Statistics: `http://localhost:5000/api/statistics`

## What was built

1. ✅ **Flask API** (`src/api/app.py`) — Serves all dashboard data via REST
2. ✅ **Widget** (`templates/dashboard.html`) — Connected to API, NOT demo data
3. ✅ **Telegram Bot** (`src/bot/telegram_bot.py`) — Receives real messages, runs pipeline
4. ✅ **Pipeline** — End-to-end: Telegram → Parser → Builder → DuplicateCheck → Save → Dashboard
