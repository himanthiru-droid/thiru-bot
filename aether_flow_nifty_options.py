# =============================================================================
# AETHER FLOW SYSTEM — NIFTY OPTIONS (STREAMLIT READY VERSION)
# =============================================================================

import os
import pyotp, time, requests, warnings
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from SmartApi import SmartConnect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

warnings.filterwarnings("ignore")

# =============================================================================
# CONFIG (SECURE)
# =============================================================================
CONFIG = {
    "api_key": os.getenv("API_KEY"),
    "client_code": os.getenv("CLIENT_CODE"),
    "password": os.getenv("PASSWORD"),
    "totp_secret": os.getenv("TOTP_SECRET"),

    "index_symbol": "Nifty 50",
    "index_token": "99926000",
    "index_exchange": "NSE",

    "option_exchange": "NFO",
    "underlying": "NIFTY",
    "lot_size": 25,
    "strike_step": 50,

    "interval": "ONE_MINUTE",
    "lookback_days": 3,

    "min_score": 3,
    "min_oi": 500000,
    "max_iv": 60.0,
    "min_delta": 0.25,
    "max_delta": 0.75,
}

_session = {
    "obj": None,
    "atm_strike": None,
}

# =============================================================================
# LOGIN
# =============================================================================
def login():
    obj = SmartConnect(api_key=CONFIG["api_key"])
    totp = pyotp.TOTP(CONFIG["totp_secret"]).now()

    data = obj.generateSession(
        CONFIG["client_code"],
        CONFIG["password"],
        totp
    )

    _session["obj"] = obj
    return obj, data

# =============================================================================
# FETCH DATA
# =============================================================================
def fetch_nifty_candles(obj):
    to_dt = datetime.now()
    from_dt = to_dt - timedelta(days=CONFIG["lookback_days"])

    params = {
        "exchange": CONFIG["index_exchange"],
        "symboltoken": CONFIG["index_token"],
        "interval": CONFIG["interval"],
        "fromdate": from_dt.strftime("%Y-%m-%d %H:%M"),
        "todate": to_dt.strftime("%Y-%m-%d %H:%M"),
    }

    resp = obj.getCandleData(params)

    if resp and resp.get("data"):
        df = pd.DataFrame(resp["data"],
            columns=["datetime","open","high","low","close","volume"]
        )
        df["datetime"] = pd.to_datetime(df["datetime"])
        return df

    return pd.DataFrame()

# =============================================================================
# SIMPLE SIGNAL (for Streamlit stability)
# =============================================================================
def compute_signal(df):
    df["ema"] = df["close"].ewm(span=20).mean()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    if prev["close"] < prev["ema"] and last["close"] > last["ema"]:
        return "BUY_CE"
    elif prev["close"] > prev["ema"] and last["close"] < last["ema"]:
        return "BUY_PE"
    else:
        return "WAIT"

# =============================================================================
# MAIN FUNCTION (STREAMLIT SAFE)
# =============================================================================
def run_once(obj=None):

    if obj is None:
        obj = _session["obj"]

    df = fetch_nifty_candles(obj)

    if df.empty or len(df) < 20:
        return None

    signal = compute_signal(df)

    last = df.iloc[-1]
    spot = float(last["close"])

    atm = round(spot / CONFIG["strike_step"]) * CONFIG["strike_step"]

    return {
        "spot": spot,
        "atm": atm,
        "signal": signal,
        "time": str(last["datetime"]),
        "ce": {"info": "CE data placeholder"},
        "pe": {"info": "PE data placeholder"},
        "bull_score": 0,
        "bear_score": 0
    }
