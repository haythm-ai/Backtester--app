#!/usr/bin/env python3
"""
================================================================================
CRYPTO BACKTESTER PRO v4.1 - BUG FIXES + REAL DATA
- Fixed StreamlitAPIException (no manual session_state writes for widget keys)
- Fixed pandas applymap -> map
- Fixed SL/TP enable/disable toggles
- Real Binance historical data fetching
- Multi-pair support
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import time
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Crypto Backtester Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        color: white;
    }
    .glass-card-green {
        background: rgba(0, 200, 83, 0.15);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 200, 83, 0.3);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        color: white;
    }
    .glass-card-red {
        background: rgba(255, 23, 68, 0.15);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 23, 68, 0.3);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        color: white;
    }
    .glass-card-blue {
        background: rgba(0, 212, 255, 0.15);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        color: white;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #7b2cbf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #8892b0;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .metric-box {
        text-align: center;
        padding: 1rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00d4ff;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #8892b0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-positive { color: #00c853 !important; }
    .metric-negative { color: #ff1744 !important; }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ccd6f6;
        margin: 1.5rem 0 0.8rem 0;
        padding-left: 0.5rem;
        border-left: 3px solid #00d4ff;
    }
    .condition-row {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 0.8rem;
        margin: 0.4rem 0;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stButton>button {
        background: linear-gradient(90deg, #00d4ff, #7b2cbf) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        height: 3.2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 0.3rem;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8892b0 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(0, 212, 255, 0.2) !important;
        color: #00d4ff !important;
    }
    .stSelectbox>div>div {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    .stNumberInput>div>div {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    .stSlider>div>div>div {
        color: #00d4ff !important;
    }
    .stToggle>div>div {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    .dataframe {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
    }
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #ccd6f6 !important;
        font-weight: 600 !important;
    }
    .footer {
        text-align: center;
        color: #8892b0;
        font-size: 0.75rem;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    @media (max-width: 768px) {
        .main-title { font-size: 1.8rem; }
        .metric-value { font-size: 1.4rem; }
        .glass-card { padding: 0.8rem; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# REAL DATA FETCHING FROM BINANCE
# ============================================================

BINANCE_PAIRS = {
    'BTC/USDT': 'BTCUSDT',
    'ETH/USDT': 'ETHUSDT',
    'SOL/USDT': 'SOLUSDT',
    'BNB/USDT': 'BNBUSDT',
    'XRP/USDT': 'XRPUSDT',
    'ADA/USDT': 'ADAUSDT',
    'DOGE/USDT': 'DOGEUSDT',
    'AVAX/USDT': 'AVAXUSDT',
    'LINK/USDT': 'LINKUSDT',
    'MATIC/USDT': 'MATICUSDT',
    'DOT/USDT': 'DOTUSDT',
    'LTC/USDT': 'LTCUSDT',
    'UNI/USDT': 'UNIUSDT',
    'ATOM/USDT': 'ATOMUSDT',
    'ETC/USDT': 'ETCUSDT',
}

@st.cache_data(ttl=3600)
def fetch_binance_klines(symbol, interval, limit=1000):
    """Fetch real OHLCV data from Binance public API"""
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if not data or len(data) == 0:
            return None
        df = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        df = df.set_index('open_time')
        df = df[['open', 'high', 'low', 'close', 'volume']]
        df.index.name = None
        return df
    except Exception as e:
        st.error(f"Error fetching {symbol}: {str(e)}")
        return None

def fetch_pair_data(pair_symbol, interval='1h', limit=1000):
    """Fetch all timeframes for a pair"""
    df_1h = fetch_binance_klines(pair_symbol, interval, limit=limit)
    if df_1h is None or df_1h.empty:
        return None, None, None
    df_4h = df_1h.resample('4h').agg({
        'open': 'first', 'high': 'max', 'low': 'min',
        'close': 'last', 'volume': 'sum'
    }).dropna()
    df_1d = df_1h.resample('1d').agg({
        'open': 'first', 'high': 'max', 'low': 'min',
        'close': 'last', 'volume': 'sum'
    }).dropna()
    return df_1h, df_4h, df_1d

# ============================================================
# INDICATORS & ENGINE
# ============================================================

class IndicatorLibrary:
    @staticmethod
    def sma(s, p): return s.rolling(window=p).mean()
    @staticmethod
    def ema(s, p): return s.ewm(span=p, adjust=False).mean()
    @staticmethod
    def rsi(s, p=14):
        d = s.diff()
        g = d.where(d>0,0).rolling(p).mean()
        l = (-d.where(d<0,0)).rolling(p).mean()
        return 100 - (100/(1+g/l))
    @staticmethod
    def macd(s, f=12, sl=26, sig=9):
        ef = s.ewm(span=f, adjust=False).mean()
        es = s.ewm(span=sl, adjust=False).mean()
        ml = ef-es
        return ml, ml.ewm(span=sig, adjust=False).mean(), ml - ml.ewm(span=sig, adjust=False).mean()
    @staticmethod
    def bb(s, p=20, sd=2):
        m = s.rolling(p).mean()
        st = s.rolling(p).std()
        return m+st*sd, m, m-st*sd
    @staticmethod
    def atr(df, p=14):
        tr = pd.concat([df['high']-df['low'], (df['high']-df['close'].shift()).abs(), (df['low']-df['close'].shift()).abs()], axis=1).max(axis=1)
        return tr.rolling(p).mean()
    @staticmethod
    def vwap(df, p=24):
        tp = (df['high']+df['low']+df['close'])/3
        return (tp*df['volume']).rolling(p).sum()/df['volume'].rolling(p).sum()
    @staticmethod
    def stoch(df, k=14, d=3):
        ll = df['low'].rolling(k).min()
        hh = df['high'].rolling(k).max()
        kline = 100*(df['close']-ll)/(hh-ll)
        return kline, kline.rolling(d).mean()
    @staticmethod
    def adx(df, p=14):
        pdm = df['high'].diff().clip(lower=0)
        mdm = (-df['low'].diff()).clip(lower=0)
        atr = IndicatorLibrary.atr(df, p)
        pdi = 100*(pdm.rolling(p).mean()/atr)
        mdi = 100*(mdm.rolling(p).mean()/atr)
        dx = 100*(pdi-mdi).abs()/(pdi+mdi)
        return dx.rolling(p).mean(), pdi, mdi
    @staticmethod
    def supertrend(df, p=10, m=3):
        atr = IndicatorLibrary.atr(df, p)
        hl2 = (df['high']+df['low'])/2
        ub = hl2 + m*atr
        lb = hl2 - m*atr
        st = pd.Series(index=df.index, dtype=float)
        dir = pd.Series(index=df.index, dtype=int)
        for i in range(len(df)):
            if i==0: st.iloc[i]=ub.iloc[i]; dir.iloc[i]=1
            elif df['close'].iloc[i] > st.iloc[i-1]:
                st.iloc[i] = max(lb.iloc[i], st.iloc[i-1]); dir.iloc[i]=1
            else:
                st.iloc[i] = min(ub.iloc[i], st.iloc[i-1]); dir.iloc[i]=-1
        return st, dir

class MultiTimeframeManager:
    def __init__(self):
        self.timeframes = {}
        self.indicators = {}
    def add_timeframe(self, name, df):
        self.timeframes[name] = df.copy()
        self.indicators[name] = {}
        self._compute(name)
    def _compute(self, tf):
        df = self.timeframes[tf]
        lib = IndicatorLibrary()
        ind = self.indicators[tf]
        for p in [20,50,200]: ind[f'sma_{p}'] = lib.sma(df['close'], p)
        for p in [9,21,50]: ind[f'ema_{p}'] = lib.ema(df['close'], p)
        ind['rsi_14'] = lib.rsi(df['close'], 14)
        ind['rsi_7'] = lib.rsi(df['close'], 7)
        ind['macd'], ind['macd_signal'], ind['macd_hist'] = lib.macd(df['close'])
        ind['stoch_k'], ind['stoch_d'] = lib.stoch(df)
        ind['bb_upper'], ind['bb_mid'], ind['bb_lower'] = lib.bb(df['close'])
        ind['atr_14'] = lib.atr(df, 14)
        ind['atr_7'] = lib.atr(df, 7)
        ind['vwap'] = lib.vwap(df, 24)
        ind['adx'], ind['plus_di'], ind['minus_di'] = lib.adx(df)
        ind['supertrend'], ind['supertrend_dir'] = lib.supertrend(df)
    def get(self, tf, ind, ts):
        if tf not in self.indicators: return None
        if ind not in self.indicators[tf]:
            if ind in ['open','high','low','close','volume']:
                df = self.timeframes[tf]
                vi = df.index[df.index <= ts]
                return df.loc[vi[-1], ind] if len(vi) > 0 else None
            return None
        s = self.indicators[tf][ind]
        vi = s.index[s.index <= ts]
        return s.loc[vi[-1]] if len(vi) > 0 else None

class RuleEngine:
    def __init__(self, mtf): self.mtf = mtf
    def eval_cond(self, c, ts):
        tf = c.get('timeframe', '1h')
        ind = c['indicator']
        op = c['operator']
        val = c['value']
        cv = self.mtf.get(tf, ind, ts)
        if cv is None or pd.isna(cv): return False
        if isinstance(val, dict):
            cmp = self.mtf.get(val.get('timeframe', tf), val['indicator'], ts)
        else:
            cmp = float(val)
        if cmp is None or pd.isna(cmp): return False
        if op == '>': return cv > cmp
        if op == '<': return cv < cmp
        if op == '>=': return cv >= cmp
        if op == '<=': return cv <= cmp
        if op == '==': return abs(cv-cmp) < 1e-10
        if op == '!=': return abs(cv-cmp) >= 1e-10
        if op in ['crosses_above', 'crosses_below']:
            df = self.mtf.timeframes[tf]
            pi = df.index[df.index < ts]
            if len(pi) == 0: return False
            pt = pi[-1]
            pv = self.mtf.get(tf, ind, pt)
            pc = cmp if not isinstance(val, dict) else self.mtf.get(val.get('timeframe', tf), val['indicator'], pt)
            if pv is None or pc is None: return False
            if op == 'crosses_above': return pv <= pc and cv > cmp
            return pv >= pc and cv < cmp
        return False
    def eval_rule(self, rule, ts):
        if 'logic' not in rule: return self.eval_cond(rule, ts)
        conds = rule['conditions']
        if rule['logic'] == 'AND': return all(self.eval_rule(c, ts) if 'logic' in c else self.eval_cond(c, ts) for c in conds)
        if rule['logic'] == 'OR': return any(self.eval_rule(c, ts) if 'logic' in c else self.eval_cond(c, ts) for c in conds)
        if rule['logic'] == 'NOT': return not self.eval_rule(conds[0], ts) if conds else True
        return False

class BacktestEngine:
    def __init__(self, mtf, capital=10000, comm=0.001, slip=0.0005, spread=0.0002):
        self.mtf = mtf
        self.initial = capital
        self.comm = comm
        self.slip = slip
        self.spread = spread
        self.reset()
    def reset(self):
        self.capital = self.initial
        self.alloc = 0
        self.equity = []
        self.trades = []
        self.pos = None
        self.size = 0
        self.entry_p = 0
        self.entry_t = None
        self.sl = None
        self.tp = None
        self.trail = None
        self.hi = None
        self.lo = None
        self.n_trades = 0
        self.n_win = 0
        self.n_loss = 0
        self.peak = self.initial
        self.max_dd = 0
        self.use_sl = True
        self.use_tp = True
        self.use_trail_flag = False
    def exec_price(self, p, d):
        if d == 'buy': ep = p * (1 + self.spread/2)
        else: ep = p * (1 - self.spread/2)
        sl = ep * self.slip * np.random.uniform(0.5, 1.5)
        return ep + sl if d == 'buy' else ep - sl
    def pos_size(self, p, atr, risk=0.02, mult=2):
        if atr == 0 or pd.isna(atr): return 0
        sd = atr * mult
        ra = self.capital * risk
        pv = ra / (sd / p)
        return min(pv / p, self.capital / p)
    def enter(self, ts, p, dir, sl_atr=2, tp_atr=3, use_sl=True, use_tp=True, use_trail=False, trail_atr=2):
        if self.pos: return False
        atr = self.mtf.get('1h', 'atr_14', ts)
        if atr is None or pd.isna(atr): return False
        ep = self.exec_price(p, 'buy' if dir == 'long' else 'sell')
        sz = self.pos_size(ep, atr)
        if sz <= 0: return False
        pv = sz * ep
        comm = pv * self.comm
        if pv + comm > self.capital:
            pv = self.capital / (1 + self.comm)
            sz = pv / ep
            comm = pv * self.comm
        if pv <= 0: return False
        self.capital -= (pv + comm)
        self.alloc = pv
        self.use_sl = use_sl
        self.use_tp = use_tp
        self.use_trail_flag = use_trail
        if dir == 'long':
            self.sl = ep - atr * sl_atr if use_sl else None
            self.tp = ep + atr * tp_atr if use_tp else None
            self.trail = ep - atr * trail_atr if use_trail else None
            self.hi = ep
        else:
            self.sl = ep + atr * sl_atr if use_sl else None
            self.tp = ep - atr * tp_atr if use_tp else None
            self.trail = ep + atr * trail_atr if use_trail else None
            self.lo = ep
        self.pos = dir
        self.size = sz
        self.entry_p = ep
        self.entry_t = ts
        return True
    def exit(self, ts, p, reason):
        if not self.pos: return False
        ep = self.exec_price(p, 'sell' if self.pos == 'long' else 'buy')
        pnl = (ep - self.entry_p) * self.size if self.pos == 'long' else (self.entry_p - ep) * self.size
        comm = self.size * ep * self.comm
        net = pnl - comm
        self.capital += self.alloc + net
        self.alloc = 0
        self.trades.append({
            'entry_time': self.entry_t, 'exit_time': ts, 'direction': self.pos,
            'entry_price': self.entry_p, 'exit_price': ep, 'position_size': self.size,
            'pnl': net, 'pnl_pct': net/(self.size*self.entry_p)*100,
            'reason': reason, 'duration_hours': (ts-self.entry_t).total_seconds()/3600
        })
        self.n_trades += 1
        if net > 0: self.n_win += 1
        else: self.n_loss += 1
        self.pos = None
        self.size = 0
        self.entry_p = 0
        self.sl = self.tp = self.trail = self.hi = self.lo = None
        return True
    def check_stops(self, ts, hi, lo, cl):
        if not self.pos: return False
        if self.pos == 'long':
            if self.use_sl and self.sl is not None and lo <= self.sl:
                self.exit(ts, self.sl, 'stop_loss'); return True
            if self.use_tp and self.tp is not None and hi >= self.tp:
                self.exit(ts, self.tp, 'take_profit'); return True
            if self.use_trail_flag and self.trail is not None:
                if cl > self.hi: self.hi = cl; self.trail = max(self.trail, cl - (self.hi-self.entry_p)*0.5)
                if lo <= self.trail: self.exit(ts, self.trail, 'trailing_stop'); return True
        else:
            if self.use_sl and self.sl is not None and hi >= self.sl:
                self.exit(ts, self.sl, 'stop_loss'); return True
            if self.use_tp and self.tp is not None and lo <= self.tp:
                self.exit(ts, self.tp, 'take_profit'); return True
            if self.use_trail_flag and self.trail is not None:
                if cl < self.lo: self.lo = cl; self.trail = min(self.trail, cl + (self.entry_p-self.lo)*0.5)
                if hi >= self.trail: self.exit(ts, self.trail, 'trailing_stop'); return True
        return False
    def update_eq(self, ts, cl):
        un = 0
        if self.pos == 'long': un = (cl - self.entry_p) * self.size
        elif self.pos == 'short': un = (self.entry_p - cl) * self.size
        eq = self.capital + self.alloc + un
        self.equity.append({'timestamp': ts, 'equity': eq, 'capital': self.capital, 'allocated': self.alloc, 'unrealized': un, 'position': self.pos})
        if eq > self.peak: self.peak = eq
        dd = (self.peak - eq) / self.peak
        if dd > self.max_dd: self.max_dd = dd
    def run(self, tf='1h', entry=None, exit=None, sl_atr=2, tp_atr=3, use_sl=True, use_tp=True, use_trail=False, trail_atr=2, start=None, end=None):
        self.reset()
        df = self.mtf.timeframes[tf]
        if start: df = df[df.index >= pd.to_datetime(start)]
        if end: df = df[df.index <= pd.to_datetime(end)]
        eng = RuleEngine(self.mtf)
        for i, (ts, row) in enumerate(df.iterrows()):
            if i < 200: self.update_eq(ts, row['close']); continue
            if self.pos and self.check_stops(ts, row['high'], row['low'], row['close']):
                self.update_eq(ts, row['close']); continue
            if self.pos and exit and eng.eval_rule(exit, ts):
                self.exit(ts, row['close'], 'signal_exit')
                self.update_eq(ts, row['close']); continue
            if not self.pos and entry and eng.eval_rule(entry, ts):
                self.enter(ts, row['close'], 'long', sl_atr, tp_atr, use_sl, use_tp, use_trail, trail_atr)
            self.update_eq(ts, row['close'])
        if self.pos: self.exit(df.index[-1], df.iloc[-1]['close'], 'end_of_data')
        return self.results()
    def results(self):
        if not self.equity: return {}
        eq_df = pd.DataFrame(self.equity)
        ret = eq_df['equity'].pct_change().dropna()
        tr = (self.capital - self.initial) / self.initial * 100
        sharpe = (ret.mean()/ret.std()*np.sqrt(365*24)) if len(ret)>1 and ret.std()>0 else 0
        dr = ret[ret<0]
        sortino = (ret.mean()/dr.std()*np.sqrt(365*24)) if len(dr)>0 and dr.std()>0 else 0
        wr = (self.n_win/self.n_trades*100) if self.n_trades>0 else 0
        gp = sum(t['pnl'] for t in self.trades if t['pnl']>0)
        gl = abs(sum(t['pnl'] for t in self.trades if t['pnl']<0))
        pf = gp/gl if gl>0 else float('inf')
        at = sum(t['pnl'] for t in self.trades)/len(self.trades) if self.trades else 0
        aw = sum(t['pnl'] for t in self.trades if t['pnl']>0)/self.n_win if self.n_win>0 else 0
        al = sum(t['pnl'] for t in self.trades if t['pnl']<0)/self.n_loss if self.n_loss>0 else 0
        exp = (wr/100*aw)+((1-wr/100)*al) if self.n_trades>0 else 0
        return {
            'total_return_pct': tr, 'initial_capital': self.initial, 'final_capital': self.capital,
            'total_trades': self.n_trades, 'winning_trades': self.n_win, 'losing_trades': self.n_loss,
            'win_rate': wr, 'profit_factor': pf, 'sharpe_ratio': sharpe, 'sortino_ratio': sortino,
            'max_drawdown_pct': self.max_dd*100, 'avg_trade': at, 'avg_win': aw, 'avg_loss': al,
            'expectancy': exp, 'equity_curve': eq_df, 'trades': pd.DataFrame(self.trades) if self.trades else pd.DataFrame()
        }

# ============================================================
# AGGREGATED RESULTS
# ============================================================

def aggregate_results(all_results):
    if not all_results:
        return None
    total_trades = sum(r['total_trades'] for r in all_results)
    winning_trades = sum(r['winning_trades'] for r in all_results)
    losing_trades = sum(r['losing_trades'] for r in all_results)
    total_initial = sum(r['initial_capital'] for r in all_results)
    total_final = sum(r['final_capital'] for r in all_results)
    total_return_pct = (total_final - total_initial) / total_initial * 100
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    all_equity = []
    for r in all_results:
        eq = r['equity_curve'].copy()
        all_equity.append(eq)

    if all_equity:
        combined_eq = pd.concat(all_equity).sort_values('timestamp')
        combined_eq = combined_eq.groupby('timestamp').agg({
            'equity': 'sum', 'capital': 'sum',
            'allocated': 'sum', 'unrealized': 'sum'
        }).reset_index()
    else:
        combined_eq = pd.DataFrame()

    all_trades = pd.concat([r['trades'] for r in all_results if not r['trades'].empty], ignore_index=True) if any(not r['trades'].empty for r in all_results) else pd.DataFrame()

    if len(combined_eq) > 1:
        ret = combined_eq['equity'].pct_change().dropna()
        sharpe = (ret.mean()/ret.std()*np.sqrt(365*24)) if ret.std() > 0 else 0
        dr = ret[ret<0]
        sortino = (ret.mean()/dr.std()*np.sqrt(365*24)) if len(dr)>0 and dr.std()>0 else 0
        peak = combined_eq['equity'].cummax()
        dd = (peak - combined_eq['equity']) / peak
        max_dd = dd.max() * 100
    else:
        sharpe = sortino = max_dd = 0

    gp = sum(t['pnl'] for _, t in all_trades.iterrows() if t['pnl'] > 0) if not all_trades.empty else 0
    gl = abs(sum(t['pnl'] for _, t in all_trades.iterrows() if t['pnl'] < 0)) if not all_trades.empty else 0
    pf = gp/gl if gl > 0 else float('inf')
    at = all_trades['pnl'].mean() if not all_trades.empty else 0
    aw = all_trades[all_trades['pnl'] > 0]['pnl'].mean() if not all_trades.empty and winning_trades > 0 else 0
    al = all_trades[all_trades['pnl'] < 0]['pnl'].mean() if not all_trades.empty and losing_trades > 0 else 0
    exp = (win_rate/100*aw)+((1-win_rate/100)*al) if total_trades > 0 else 0

    return {
        'total_return_pct': total_return_pct, 'initial_capital': total_initial, 'final_capital': total_final,
        'total_trades': total_trades, 'winning_trades': winning_trades, 'losing_trades': losing_trades,
        'win_rate': win_rate, 'profit_factor': pf, 'sharpe_ratio': sharpe, 'sortino_ratio': sortino,
        'max_drawdown_pct': max_dd, 'avg_trade': at, 'avg_win': aw, 'avg_loss': al,
        'expectancy': exp, 'equity_curve': combined_eq, 'trades': all_trades,
        'per_pair': all_results
    }

# ============================================================
# UI HELPERS
# ============================================================

def render_header():
    st.markdown('<div class="main-title">📊 Crypto Backtester Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Real Data | Multi-Timeframe | Multi-Pair</div>', unsafe_allow_html=True)

def build_condition_card(prefix, key_prefix, index):
    indicators = ['close', 'open', 'high', 'low', 'volume', 'rsi_14', 'rsi_7', 'macd_hist',
                  'ema_9', 'ema_21', 'ema_50', 'sma_20', 'sma_50', 'sma_200',
                  'bb_upper', 'bb_mid', 'bb_lower', 'atr_14', 'atr_7', 'adx',
                  'vwap', 'supertrend_dir', 'stoch_k', 'stoch_d']
    ops = ['>', '<', '>=', '<=', '==', '!=', 'crosses_above', 'crosses_below']

    with st.container():
        st.markdown(f'<div class="condition-row">', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 2, 2])
        with c1:
            tf = st.selectbox(f"Timeframe", ['1h', '4h', '1d'], key=f"{key_prefix}_tf_{index}", label_visibility="collapsed")
        with c2:
            ind = st.selectbox(f"Indicator", indicators, key=f"{key_prefix}_ind_{index}", label_visibility="collapsed")
        with c3:
            op = st.selectbox(f"Op", ops, key=f"{key_prefix}_op_{index}", label_visibility="collapsed")
        with c4:
            val_type = st.selectbox(f"Type", ['Number', 'Indicator'], key=f"{key_prefix}_vt_{index}", label_visibility="collapsed")
        with c5:
            if val_type == 'Number':
                val = st.number_input(f"Value", value=50.0, key=f"{key_prefix}_val_{index}", label_visibility="collapsed")
                result = {'timeframe': tf, 'indicator': ind, 'operator': op, 'value': val}
            else:
                val_tf = st.selectbox(f"V-TF", ['1h', '4h', '1d'], key=f"{key_prefix}_vtf_{index}", label_visibility="collapsed")
                val_ind = st.selectbox(f"V-Ind", indicators, key=f"{key_prefix}_vind_{index}", label_visibility="collapsed")
                result = {'timeframe': tf, 'indicator': ind, 'operator': op,
                         'value': {'timeframe': val_tf, 'indicator': val_ind}}
        st.markdown('</div>', unsafe_allow_html=True)
    return result

# ============================================================
# MAIN APP
# ============================================================

def main():
    render_header()

    # Initialize session state for non-widget values
    if 'run_backtest' not in st.session_state:
        st.session_state.run_backtest = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'all_results' not in st.session_state:
        st.session_state.all_results = []
    if 'entry_rule' not in st.session_state:
        st.session_state.entry_rule = None
    if 'exit_rule' not in st.session_state:
        st.session_state.exit_rule = None

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Strategy", "⚙️ Settings", "📈 Results", "📋 Trades"])

    # ============================================
    # TAB 1: STRATEGY
    # ============================================
    with tab1:
        st.markdown('<div class="section-header">💱 Select Crypto Pairs</div>', unsafe_allow_html=True)

        selected_pairs = st.multiselect(
            "Choose one or more pairs to backtest (real Binance data)",
            options=list(BINANCE_PAIRS.keys()),
            default=['BTC/USDT'],
            key="selected_pairs"
        )

        if not selected_pairs:
            st.warning("⚠️ Please select at least one crypto pair to continue.")
            st.stop()

        pair_chips = " ".join([f"<span style='background:rgba(0,212,255,0.2);color:#00d4ff;padding:4px 12px;border-radius:12px;margin:2px;display:inline-block;font-size:0.85rem;'>{p}</span>" for p in selected_pairs])
        st.markdown(f"<div style='margin:0.5rem 0 1rem 0;'>Selected: {pair_chips}</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-header">⏱️ Data Settings</div>', unsafe_allow_html=True)
        data_limit = st.slider("Data Points (max 1000)", 100, 1000, 500, 100, key="data_limit")
        st.caption(f"Fetching ~{data_limit} candles of real historical data per pair from Binance")

        st.markdown("---")
        st.markdown('<div class="section-header">🟢 Entry Rules</div>', unsafe_allow_html=True)

        st.markdown("**Primary Entry Group**")
        entry_g1_logic = st.segmented_control("Group 1 Logic", ["AND", "OR"], default="AND", key="ent_g1_logic")
        n_ent_g1 = st.slider("Conditions", 1, 4, 2, key="n_ent_g1")
        entry_g1_conds = []
        for i in range(n_ent_g1):
            entry_g1_conds.append(build_condition_card("Entry", "ent_g1", i))

        entry_conditions = [{'logic': entry_g1_logic, 'conditions': entry_g1_conds}]

        use_ent_g2 = st.toggle("➕ Add Second Entry Group", value=False, key="use_ent_g2")
        if use_ent_g2:
            st.markdown("**Secondary Entry Group**")
            entry_g2_logic = st.segmented_control("Group 2 Logic", ["AND", "OR"], default="OR", key="ent_g2_logic")
            n_ent_g2 = st.slider("Conditions", 1, 4, 1, key="n_ent_g2")
            entry_g2_conds = []
            for i in range(n_ent_g2):
                entry_g2_conds.append(build_condition_card("Entry", "ent_g2", i))
            entry_conditions.append({'logic': entry_g2_logic, 'conditions': entry_g2_conds})
            entry_group_logic = st.segmented_control("How groups combine", ["AND", "OR"], default="OR", key="ent_groups")
            entry_rule = {'logic': entry_group_logic, 'conditions': entry_conditions}
        else:
            entry_rule = entry_conditions[0]

        st.markdown("---")
        st.markdown('<div class="section-header">🔴 Exit Rules</div>', unsafe_allow_html=True)

        st.markdown("**Primary Exit Group**")
        exit_g1_logic = st.segmented_control("Group 1 Logic", ["OR", "AND"], default="OR", key="ext_g1_logic")
        n_ext_g1 = st.slider("Conditions", 1, 4, 2, key="n_ext_g1")
        exit_g1_conds = []
        for i in range(n_ext_g1):
            exit_g1_conds.append(build_condition_card("Exit", "ext_g1", i))

        exit_conditions = [{'logic': exit_g1_logic, 'conditions': exit_g1_conds}]

        use_ext_g2 = st.toggle("➕ Add Second Exit Group", value=False, key="use_ext_g2")
        if use_ext_g2:
            st.markdown("**Secondary Exit Group**")
            exit_g2_logic = st.segmented_control("Group 2 Logic", ["OR", "AND"], default="OR", key="ext_g2_logic")
            n_ext_g2 = st.slider("Conditions", 1, 4, 1, key="n_ext_g2")
            exit_g2_conds = []
            for i in range(n_ext_g2):
                exit_g2_conds.append(build_condition_card("Exit", "ext_g2", i))
            exit_conditions.append({'logic': exit_g2_logic, 'conditions': exit_g2_conds})
            exit_group_logic = st.segmented_control("How groups combine", ["OR", "AND"], default="OR", key="ext_groups")
            exit_rule = {'logic': exit_group_logic, 'conditions': exit_conditions}
        else:
            exit_rule = exit_conditions[0]

        # Store rules in session state (NOT widget values - widgets auto-store)
        st.session_state.entry_rule = entry_rule
        st.session_state.exit_rule = exit_rule
        # data_limit is auto-stored by the widget, no manual assignment needed

    # ============================================
    # TAB 2: SETTINGS
    # ============================================
    with tab2:
        st.markdown('<div class="section-header">Risk Management</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("**Stop Loss**")
            use_sl = st.toggle("Enable Stop Loss", value=True, key="sl_en")
            sl_atr = st.slider("ATR Multiplier", 0.5, 5.0, 2.0, 0.5, key="sl", disabled=not use_sl)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("**Take Profit**")
            use_tp = st.toggle("Enable Take Profit", value=True, key="tp_en")
            tp_atr = st.slider("ATR Multiplier", 1.0, 10.0, 3.0, 0.5, key="tp", disabled=not use_tp)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("**Trailing Stop**")
            use_trail = st.toggle("Enable", value=False, key="trail_en")
            trail_atr = st.slider("ATR Multiplier", 0.5, 5.0, 2.0, 0.5, key="trail", disabled=not use_trail)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("**Capital**")
            capital = st.number_input("Initial ($)", 1000, 100000, 10000, 1000, key="cap")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-header">Backtest Period</div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            start_date = st.date_input("Start Date", datetime(2026, 3, 1), key="start")
        with col4:
            end_date = st.date_input("End Date", datetime(2026, 5, 15), key="end")

        # NO manual session_state assignments for widget keys!
        # Widget values are automatically accessible via st.session_state.key_name

        st.markdown("---")
        if st.button("🚀 RUN BACKTEST", type="primary", use_container_width=True, key="run_btn"):
            st.session_state.run_backtest = True
            st.rerun()

    # ============================================
    # TAB 3: RESULTS
    # ============================================
    with tab3:
        if not st.session_state.run_backtest:
            st.info("👆 Go to **Strategy** or **Settings** tab and tap **RUN BACKTEST**")
            cols = st.columns(4)
            for col in cols:
                with col:
                    st.markdown("""
                    <div class="glass-card">
                        <div class="metric-box">
                            <div class="metric-value">--</div>
                            <div class="metric-label">Waiting...</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            selected_pairs = st.session_state.selected_pairs
            data_limit = st.session_state.data_limit

            progress_bar = st.progress(0)
            status_text = st.empty()

            all_results = []
            all_data = {}

            for idx, pair in enumerate(selected_pairs):
                progress = (idx) / len(selected_pairs)
                progress_bar.progress(progress)
                status_text.text(f"Fetching real data for {pair}... ({idx+1}/{len(selected_pairs)})")

                symbol = BINANCE_PAIRS[pair]
                df_1h, df_4h, df_1d = fetch_pair_data(symbol, interval='1h', limit=data_limit)

                if df_1h is None or df_1h.empty:
                    st.warning(f"Could not fetch data for {pair}. Skipping...")
                    continue

                mtf = MultiTimeframeManager()
                mtf.add_timeframe('1h', df_1h)
                mtf.add_timeframe('4h', df_4h)
                mtf.add_timeframe('1d', df_1d)
                all_data[pair] = mtf

                status_text.text(f"Backtesting {pair}... ({idx+1}/{len(selected_pairs)})")

                bt = BacktestEngine(mtf, capital=st.session_state.cap,
                                   comm=0.001, slip=0.0005, spread=0.0002)
                res = bt.run(
                    tf='1h',
                    entry=st.session_state.entry_rule,
                    exit=st.session_state.exit_rule,
                    sl_atr=st.session_state.sl,
                    tp_atr=st.session_state.tp,
                    use_sl=st.session_state.sl_en,
                    use_tp=st.session_state.tp_en,
                    use_trail=st.session_state.trail_en,
                    trail_atr=st.session_state.trail,
                    start=st.session_state.start,
                    end=st.session_state.end
                )
                if res:
                    res['pair'] = pair
                    all_results.append(res)

                if idx < len(selected_pairs) - 1:
                    time.sleep(0.5)

            progress_bar.progress(1.0)
            status_text.empty()
            progress_bar.empty()

            results = aggregate_results(all_results)

            if not results or results['total_trades'] == 0:
                st.error("No results generated. Check your conditions, selected pairs, and date range.")
                st.session_state.run_backtest = False
            else:
                st.session_state.results = results
                st.session_state.all_results = all_results

                st.markdown('<div class="section-header">📡 Real Data Source</div>', unsafe_allow_html=True)
                st.success(f"✅ Backtested {len(all_results)} pair(s) with real Binance historical data")

                st.markdown('<div class="section-header">Per-Pair Performance</div>', unsafe_allow_html=True)
                pair_cols = st.columns(min(len(all_results), 5))
                for i, pair_res in enumerate(all_results):
                    with pair_cols[i % len(pair_cols)]:
                        ret_color = "metric-positive" if pair_res['total_return_pct'] > 0 else "metric-negative"
                        st.markdown(f"""
                        <div class="glass-card-blue">
                            <div class="metric-box">
                                <div class="metric-value" style="font-size:1.0rem;">{pair_res.get('pair', 'Unknown')}</div>
                                <div class="metric-value {ret_color}" style="font-size:1.3rem;">{pair_res['total_return_pct']:+.2f}%</div>
                                <div class="metric-label">{pair_res['total_trades']} trades | WR {pair_res['win_rate']:.0f}%</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown('<div class="section-header">Combined Performance Metrics</div>', unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    is_pos = results['total_return_pct'] > 0
                    card_class = "glass-card-green" if is_pos else "glass-card-red"
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div class="metric-box">
                            <div class="metric-value {'metric-positive' if is_pos else 'metric-negative'}">{results['total_return_pct']:+.2f}%</div>
                            <div class="metric-label">Total Return</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-box">
                            <div class="metric-value">{results['total_trades']}</div>
                            <div class="metric-label">Total Trades</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-box">
                            <div class="metric-value">{results['win_rate']:.1f}%</div>
                            <div class="metric-label">Win Rate</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c4:
                    st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-box">
                            <div class="metric-value">{results['sharpe_ratio']:.2f}</div>
                            <div class="metric-label">Sharpe Ratio</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                c5, c6, c7, c8 = st.columns(4)
                with c5:
                    st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-box">
                            <div class="metric-value metric-negative">{results['max_drawdown_pct']:.2f}%</div>
                            <div class="metric-label">Max Drawdown</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c6:
                    st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-box">
                            <div class="metric-value">{results['profit_factor']:.2f}</div>
                            <div class="metric-label">Profit Factor</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c7:
                    st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-box">
                            <div class="metric-value">${results['expectancy']:.2f}</div>
                            <div class="metric-label">Expectancy</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c8:
                    st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-box">
                            <div class="metric-value">${results['final_capital']:,.0f}</div>
                            <div class="metric-label">Final Capital</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('<div class="section-header">Charts</div>', unsafe_allow_html=True)
                eq_df = results['equity_curve']

                tab_chart1, tab_chart2 = st.tabs(["Equity Curve", "Drawdown"])
                with tab_chart1:
                    if not eq_df.empty:
                        chart_data = pd.DataFrame({
                            'Equity': eq_df.set_index('timestamp')['equity'],
                            'Peak': eq_df.set_index('timestamp')['equity'].cummax()
                        })
                        st.line_chart(chart_data, use_container_width=True)
                    else:
                        st.info("No equity data available.")
                # Reset button to run again
                st.markdown("---")
                if st.button("🔄 Run Another Backtest", use_container_width=True, key="reset_btn"):
                    st.session_state.run_backtest = False
                    st.session_state.results = None
                    st.session_state.all_results = []
                    st.rerun()

                with tab_chart2:
                    if not eq_df.empty:
                        peak = eq_df['equity'].cummax()
                        dd = (peak - eq_df['equity']) / peak * 100
                        st.area_chart(pd.DataFrame({'Drawdown %': dd.values}, index=eq_df['timestamp']),
                                      use_container_width=True, color=['#ff1744'])
                    else:
                        st.info("No drawdown data available.")

    # ============================================
    # TAB 4: TRADES
    # ============================================
    with tab4:
        if st.session_state.results is None:
            st.info("👆 Run a backtest first in the **Results** tab")
        else:
            results = st.session_state.results
            trades_df = results['trades']
            all_results = st.session_state.all_results

            if not trades_df.empty:
                st.markdown('<div class="section-header">Trade History</div>', unsafe_allow_html=True)

                if len(all_results) > 1:
                    st.markdown('<div class="section-header">Per-Pair Summary</div>', unsafe_allow_html=True)
                    pair_summary = []
                    for r in all_results:
                        pair_summary.append({
                            'Pair': r.get('pair', 'Unknown'),
                            'Trades': r['total_trades'],
                            'Win Rate': f"{r['win_rate']:.1f}%",
                            'Return': f"{r['total_return_pct']:+.2f}%",
                            'Profit Factor': f"{r['profit_factor']:.2f}",
                            'Sharpe': f"{r['sharpe_ratio']:.2f}"
                        })
                    summary_df = pd.DataFrame(pair_summary)
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)

                wins = trades_df[trades_df['pnl'] > 0]
                losses = trades_df[trades_df['pnl'] <= 0]

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"""
                    <div class="glass-card-green">
                        <div class="metric-box">
                            <div class="metric-value metric-positive">{len(wins)}</div>
                            <div class="metric-label">Winning Trades</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class="glass-card-red">
                        <div class="metric-box">
                            <div class="metric-value metric-negative">{len(losses)}</div>
                            <div class="metric-label">Losing Trades</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c3:
                    avg_dur = trades_df['duration_hours'].mean()
                    st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-box">
                            <div class="metric-value">{avg_dur:.1f}h</div>
                            <div class="metric-label">Avg Duration</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Reconstruct pair column for display
                if 'pair' not in trades_df.columns and len(all_results) > 1:
                    trades_with_pair = []
                    for r in all_results:
                        tdf = r['trades'].copy()
                        tdf['pair'] = r.get('pair', 'Unknown')
                        trades_with_pair.append(tdf)
                    trades_df = pd.concat(trades_with_pair, ignore_index=True)

                if 'pair' in trades_df.columns:
                    display_df = trades_df[['pair', 'entry_time', 'exit_time', 'pnl', 'pnl_pct', 'reason', 'duration_hours']].copy()
                    display_df.columns = ['Pair', 'Entry', 'Exit', 'P&L ($)', 'P&L (%)', 'Reason', 'Hours']
                else:
                    display_df = trades_df[['entry_time', 'exit_time', 'pnl', 'pnl_pct', 'reason', 'duration_hours']].copy()
                    display_df.columns = ['Entry', 'Exit', 'P&L ($)', 'P&L (%)', 'Reason', 'Hours']

                def color_pnl(val):
                    if isinstance(val, (int, float)):
                        return 'background-color: rgba(0,200,83,0.3)' if val > 0 else 'background-color: rgba(255,23,68,0.3)'
                    return ''

                st.dataframe(
                    display_df.style.map(color_pnl, subset=['P&L ($)', 'P&L (%)']),
                    use_container_width=True,
                    height=400
                )

                csv = trades_df.to_csv(index=False)
                st.download_button("📥 Download CSV", csv, "trades.csv", "text/csv", use_container_width=True)
            else:
                st.warning("No trades were generated. Try adjusting your strategy conditions or date range.")

    st.markdown("""
    <div class="footer">
        Crypto Backtester Pro v4.1 | Real Binance Data | Built with Streamlit
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
