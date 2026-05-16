#!/usr/bin/env python3
"""
================================================================================
CRYPTO BACKTESTER PRO v5.1 - SEQUENTIAL CONDITIONS + UNIVERSAL DATA + LIVE
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

st.set_page_config(page_title="Crypto Backtester Pro v5.3", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);}
#MainMenu,footer,header{visibility:hidden;}
.glass-card{background:rgba(255,255,255,0.08);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:1.2rem;margin:0.5rem 0;color:white;}
.glass-card-green{background:rgba(0,200,83,0.15);border:1px solid rgba(0,200,83,0.3);}
.glass-card-red{background:rgba(255,23,68,0.15);border:1px solid rgba(255,23,68,0.3);}
.glass-card-blue{background:rgba(0,212,255,0.15);border:1px solid rgba(0,212,255,0.3);}
.glass-card-orange{background:rgba(255,152,0,0.15);border:1px solid rgba(255,152,0,0.3);}
.glass-card-purple{background:rgba(123,44,191,0.15);border:1px solid rgba(123,44,191,0.3);}
.main-title{font-size:2.5rem;font-weight:800;background:linear-gradient(90deg,#00d4ff,#7b2cbf);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;}
.subtitle{text-align:center;color:#8892b0;font-size:1rem;margin-bottom:2rem;}
.metric-box{text-align:center;padding:1rem;}
.metric-value{font-size:1.8rem;font-weight:700;color:#00d4ff;}
.metric-label{font-size:0.75rem;color:#8892b0;text-transform:uppercase;letter-spacing:1px;}
.metric-positive{color:#00c853!important;}
.metric-negative{color:#ff1744!important;}
.section-header{font-size:1.3rem;font-weight:600;color:#ccd6f6;margin:1.5rem 0 0.8rem;padding-left:0.5rem;border-left:3px solid #00d4ff;}
.condition-row{background:rgba(255,255,255,0.05);border-radius:12px;padding:0.8rem;margin:0.4rem 0;border:1px solid rgba(255,255,255,0.08);}
.stButton>button{background:linear-gradient(90deg,#00d4ff,#7b2cbf)!important;color:white!important;border:none!important;border-radius:12px!important;height:3.2rem!important;font-size:1.1rem!important;font-weight:600!important;width:100%!important;}
.stTabs [data-baseweb="tab-list"]{gap:8px;background:rgba(255,255,255,0.05);border-radius:12px;padding:0.3rem;}
.stTabs [data-baseweb="tab"]{color:#8892b0!important;border-radius:8px!important;padding:0.6rem 1.2rem!important;}
.stTabs [aria-selected="true"]{background:rgba(0,212,255,0.2)!important;color:#00d4ff!important;}
.stSelectbox>div>div,.stNumberInput>div>div{background:rgba(255,255,255,0.08)!important;border:1px solid rgba(255,255,255,0.15)!important;border-radius:10px!important;color:white!important;}
.stSlider>div>div>div{color:#00d4ff!important;}
.stToggle>div>div{background:rgba(255,255,255,0.1)!important;}
.dataframe{background:rgba(255,255,255,0.05)!important;border-radius:12px!important;}
.streamlit-expanderHeader{background:rgba(255,255,255,0.08)!important;border-radius:12px!important;color:#ccd6f6!important;font-weight:600!important;}
.footer{text-align:center;color:#8892b0;font-size:0.75rem;margin-top:2rem;padding:1rem;border-top:1px solid rgba(255,255,255,0.1);}
.live-indicator{display:inline-block;width:10px;height:10px;background:#00c853;border-radius:50%;animation:pulse 2s infinite;margin-right:8px;}
@keyframes pulse{0%{opacity:1;transform:scale(1);}50%{opacity:0.5;transform:scale(1.2);}100%{opacity:1;transform:scale(1);}}
@media(max-width:768px){.main-title{font-size:1.8rem;}.metric-value{font-size:1.4rem;}.glass-card{padding:0.8rem;}}
.seq-badge{background:linear-gradient(90deg,#7b2cbf,#00d4ff);color:white;padding:2px 8px;border-radius:6px;font-size:0.75rem;font-weight:600;margin-left:8px;}
</style>
""", unsafe_allow_html=True)

CRYPTO_PAIRS = {
    'BTC/USDT': {'binance':'BTCUSDT','coingecko':'bitcoin','cryptocompare':'BTC','base_price':65000,'vol':0.008},
    'ETH/USDT': {'binance':'ETHUSDT','coingecko':'ethereum','cryptocompare':'ETH','base_price':3500,'vol':0.012},
    'SOL/USDT': {'binance':'SOLUSDT','coingecko':'solana','cryptocompare':'SOL','base_price':145,'vol':0.018},
    'BNB/USDT': {'binance':'BNBUSDT','coingecko':'binancecoin','cryptocompare':'BNB','base_price':590,'vol':0.010},
    'XRP/USDT': {'binance':'XRPUSDT','coingecko':'ripple','cryptocompare':'XRP','base_price':0.55,'vol':0.015},
    'ADA/USDT': {'binance':'ADAUSDT','coingecko':'cardano','cryptocompare':'ADA','base_price':0.45,'vol':0.016},
    'DOGE/USDT': {'binance':'DOGEUSDT','coingecko':'dogecoin','cryptocompare':'DOGE','base_price':0.16,'vol':0.020},
    'AVAX/USDT': {'binance':'AVAXUSDT','coingecko':'avalanche-2','cryptocompare':'AVAX','base_price':35,'vol':0.019},
    'LINK/USDT': {'binance':'LINKUSDT','coingecko':'chainlink','cryptocompare':'LINK','base_price':14,'vol':0.014},
    'MATIC/USDT': {'binance':'MATICUSDT','coingecko':'matic-network','cryptocompare':'MATIC','base_price':0.65,'vol':0.017},
    'DOT/USDT': {'binance':'DOTUSDT','coingecko':'polkadot','cryptocompare':'DOT','base_price':7,'vol':0.016},
    'LTC/USDT': {'binance':'LTCUSDT','coingecko':'litecoin','cryptocompare':'LTC','base_price':85,'vol':0.013},
    'UNI/USDT': {'binance':'UNIUSDT','coingecko':'uniswap','cryptocompare':'UNI','base_price':8,'vol':0.017},
    'ATOM/USDT': {'binance':'ATOMUSDT','coingecko':'cosmos','cryptocompare':'ATOM','base_price':8,'vol':0.016},
    'ETC/USDT': {'binance':'ETCUSDT','coingecko':'ethereum-classic','cryptocompare':'ETC','base_price':25,'vol':0.015},
    'SHIB/USDT': {'binance':'SHIBUSDT','coingecko':'shiba-inu','cryptocompare':'SHIB','base_price':0.00002,'vol':0.025},
    'TRX/USDT': {'binance':'TRXUSDT','coingecko':'tron','cryptocompare':'TRX','base_price':0.12,'vol':0.014},
    'BCH/USDT': {'binance':'BCHUSDT','coingecko':'bitcoin-cash','cryptocompare':'BCH','base_price':450,'vol':0.012},
    'FIL/USDT': {'binance':'FILUSDT','coingecko':'filecoin','cryptocompare':'FIL','base_price':5.5,'vol':0.018},
    'ARB/USDT': {'binance':'ARBUSDT','coingecko':'arbitrum','cryptocompare':'ARB','base_price':1.2,'vol':0.020},
}

SOURCE_MAP = {'Auto (Best Available)':'auto','Binance':'binance','CoinGecko':'coingecko','CryptoCompare':'cryptocompare','Synthetic (Demo)':'synthetic'}

def fetch_with_retry(url, params=None, max_retries=3, timeout=15):
    for attempt in range(max_retries):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            if r.status_code == 200: return r
            if r.status_code == 429: time.sleep(2**attempt); continue
            return r
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < max_retries-1: time.sleep(1)
    return None

@st.cache_data(ttl=300)
def fetch_binance(symbol, interval='1h', limit=500):
    """Fetch up to `limit` candles. Uses pagination for large requests (max 1000 per call)."""
    url = "https://api.binance.com/api/v3/klines"
    all_data = []

    # Binance max per request = 1000
    chunk_size = 1000
    remaining = limit

    # For historical pagination, we fetch backwards from now
    # First request: get the most recent `chunk_size` candles
    # Subsequent requests: use the open_time of the earliest candle as endTime
    end_time = None

    while remaining > 0:
        params = {"symbol": symbol, "interval": interval, "limit": min(chunk_size, remaining)}
        if end_time:
            params["endTime"] = end_time

        r = fetch_with_retry(url, params)
        if not r or r.status_code != 200:
            break

        data = r.json()
        if not data or len(data) == 0:
            break

        all_data.extend(data)

        # Use open time of first candle in this batch as endTime for next batch
        # (we want older candles, so endTime = first candle's open time - 1ms)
        end_time = int(data[0][0]) - 1
        remaining -= len(data)

        # Safety: if we got less than requested, we've hit the start of available data
        if len(data) < chunk_size:
            break

        # Small delay to respect rate limits
        time.sleep(0.15)

    if not all_data:
        return None

    df = pd.DataFrame(all_data, columns=['open_time','open','high','low','close','volume','close_time','quote_volume','trades','taker_buy_base','taker_buy_quote','ignore'])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    for c in ['open','high','low','close','volume']: df[c] = df[c].astype(float)
    df = df.set_index('open_time')[['open','high','low','close','volume']]
    df = df.sort_index()  # Ensure chronological order
    return df

@st.cache_data(ttl=300)
def fetch_coingecko(coin_id, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    r = fetch_with_retry(url, {"vs_currency":"usd","days":str(days)})
    if not r or r.status_code != 200: return None
    data = r.json()
    if not data: return None
    df = pd.DataFrame(data, columns=['timestamp','open','high','low','close'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['volume'] = 0
    return df.set_index('timestamp')[['open','high','low','close','volume']]

@st.cache_data(ttl=300)
def fetch_cryptocompare(symbol, limit=500, aggregate=1):
    """Fetch up to `limit` hourly candles. Uses pagination (max ~2000 per call)."""
    url = "https://min-api.cryptocompare.com/data/v2/histohour"
    all_data = []

    chunk_size = 2000
    remaining = limit
    to_ts = None  # timestamp to fetch before

    while remaining > 0:
        params = {"fsym": symbol, "tsym": "USDT", "limit": min(chunk_size, remaining), "aggregate": aggregate}
        if to_ts:
            params["toTs"] = int(to_ts)

        r = fetch_with_retry(url, params)
        if not r or r.status_code != 200:
            break

        data = r.json().get('Data',{}).get('Data',[])
        if not data or len(data) == 0:
            break

        all_data.extend(data)

        # Next batch: fetch before the earliest timestamp in this batch
        to_ts = min(d['time'] for d in data) - 1
        remaining -= len(data)

        if len(data) < chunk_size:
            break

        time.sleep(0.2)  # Respect rate limits

    if not all_data:
        return None

    df = pd.DataFrame(all_data)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = df.set_index('time')[['open','high','low','close','volumefrom']].rename(columns={'volumefrom':'volume'})
    df = df.sort_index()
    return df

def generate_synthetic(config, n_hours=90*24, interval='1h'):
    np.random.seed(42)
    end = datetime.now()
    if interval=='1m': dates=[end-timedelta(minutes=i) for i in range(n_hours*60)]
    elif interval=='5m': dates=[end-timedelta(minutes=i*5) for i in range(n_hours*12)]
    elif interval=='15m': dates=[end-timedelta(minutes=i*15) for i in range(n_hours*4)]
    elif interval=='30m': dates=[end-timedelta(minutes=i*30) for i in range(n_hours*2)]
    elif interval=='4h': dates=[end-timedelta(hours=i*4) for i in range(n_hours//4)]
    elif interval=='1d': dates=[end-timedelta(days=i) for i in range(n_hours//24)]
    elif interval=='1w': dates=[end-timedelta(weeks=i) for i in range(n_hours//(24*7))]
    else: dates=[end-timedelta(hours=i) for i in range(n_hours)]
    dates.reverse()
    n=len(dates)
    ret=np.random.normal(0.0001,config['vol'],n)
    var=config['vol']**2
    for i in range(1,n):
        var=0.000001+0.85*var+0.1*ret[i-1]**2
        ret[i]=np.random.normal(0.0001,np.sqrt(var))
    cl=config['base_price']*np.exp(np.cumsum(ret))
    hl=cl*np.abs(np.random.normal(0,config['vol']/2,n))
    hi=cl+hl*np.random.uniform(0.3,1.0,n)
    lo=cl-hl*np.random.uniform(0.3,1.0,n)
    op=np.roll(cl,1); op[0]=config['base_price']; op=op*(1+np.random.normal(0,0.001,n))
    vol=1000*(1+5*np.abs(ret)/np.std(ret))*np.random.lognormal(0,0.5,n)
    return pd.DataFrame({'open':op,'high':hi,'low':lo,'close':cl,'volume':vol}, index=pd.DatetimeIndex(dates))

def fetch_pair_data(pair_name, interval='1h', limit=500, source='auto'):
    config = CRYPTO_PAIRS[pair_name]
    df, src = None, None
    if source in ['auto','binance']:
        df = fetch_binance(config['binance'], interval, limit)
        if df is not None and not df.empty: src='Binance'
    if df is None and source in ['auto','coingecko']:
        df = fetch_coingecko(config['coingecko'], min(limit//24+1,365))
        if df is not None and not df.empty: src='CoinGecko'
    if df is None and source in ['auto','cryptocompare']:
        agg={'1h':1,'4h':4,'1d':24}.get(interval,1)
        df = fetch_cryptocompare(config['cryptocompare'], limit, agg)
        if df is not None and not df.empty: src='CryptoCompare'
    if df is None:
        nh=limit if interval=='1h' else limit*4 if interval=='4h' else limit*24
        df = generate_synthetic(config, nh, interval)
        src='Synthetic (Demo)'
    if df is None or df.empty: return None,None,None,None
    df4h=df.resample('4h').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna()
    df1d=df.resample('1d').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna()
    return df,df4h,df1d,src

def get_live_price(pair_name):
    config = CRYPTO_PAIRS[pair_name]
    r = fetch_with_retry("https://api.binance.com/api/v3/ticker/price", {"symbol":config['binance']}, timeout=5)
    if r and r.status_code==200: return float(r.json().get('price',0))
    r = fetch_with_retry("https://api.coingecko.com/api/v3/simple/price", {"ids":config['coingecko'],"vs_currencies":"usd"}, timeout=5)
    if r and r.status_code==200: return r.json().get(config['coingecko'],{}).get('usd',0)
    return None

class IndicatorLibrary:
    @staticmethod
    def sma(s,p): return s.rolling(window=p).mean()
    @staticmethod
    def ema(s,p): return s.ewm(span=p,adjust=False).mean()
    @staticmethod
    def rsi(s,p=14):
        d=s.diff(); g=d.where(d>0,0).rolling(p).mean(); l=(-d.where(d<0,0)).rolling(p).mean()
        return 100-(100/(1+g/l))
    @staticmethod
    def macd(s,f=12,sl=26,sig=9):
        ef=s.ewm(span=f,adjust=False).mean(); es=s.ewm(span=sl,adjust=False).mean(); ml=ef-es
        return ml,ml.ewm(span=sig,adjust=False).mean(),ml-ml.ewm(span=sig,adjust=False).mean()
    @staticmethod
    def bb(s,p=20,sd=2):
        m=s.rolling(p).mean(); st=s.rolling(p).std(); return m+st*sd,m,m-st*sd
    @staticmethod
    def atr(df,p=14):
        tr=pd.concat([df['high']-df['low'],(df['high']-df['close'].shift()).abs(),(df['low']-df['close'].shift()).abs()],axis=1).max(axis=1)
        return tr.rolling(p).mean()
    @staticmethod
    def vwap(df,p=24):
        tp=(df['high']+df['low']+df['close'])/3; return (tp*df['volume']).rolling(p).sum()/df['volume'].rolling(p).sum()
    @staticmethod
    def stoch(df,k=14,d=3):
        ll=df['low'].rolling(k).min(); hh=df['high'].rolling(k).max(); kline=100*(df['close']-ll)/(hh-ll)
        return kline,kline.rolling(d).mean()
    @staticmethod
    def adx(df,p=14):
        pdm=df['high'].diff().clip(lower=0); mdm=(-df['low'].diff()).clip(lower=0); atr=IndicatorLibrary.atr(df,p)
        pdi=100*(pdm.rolling(p).mean()/atr); mdi=100*(mdm.rolling(p).mean()/atr); dx=100*(pdi-mdi).abs()/(pdi+mdi)
        return dx.rolling(p).mean(),pdi,mdi
    @staticmethod
    def supertrend(df,p=10,m=3):
        atr=IndicatorLibrary.atr(df,p); hl2=(df['high']+df['low'])/2; ub=hl2+m*atr; lb=hl2-m*atr
        st=pd.Series(index=df.index,dtype=float); dir=pd.Series(index=df.index,dtype=int)
        for i in range(len(df)):
            if i==0: st.iloc[i]=ub.iloc[i]; dir.iloc[i]=1
            elif df['close'].iloc[i]>st.iloc[i-1]: st.iloc[i]=max(lb.iloc[i],st.iloc[i-1]); dir.iloc[i]=1
            else: st.iloc[i]=min(ub.iloc[i],st.iloc[i-1]); dir.iloc[i]=-1
        return st,dir

class MultiTimeframeManager:
    def __init__(self): self.timeframes={}; self.indicators={}
    def add_timeframe(self,name,df): self.timeframes[name]=df.copy(); self.indicators[name]={}; self._compute(name)
    def _compute(self,tf):
        df=self.timeframes[tf]; lib=IndicatorLibrary(); ind=self.indicators[tf]
        for p in [20,50,200]: ind[f'sma_{p}']=lib.sma(df['close'],p)
        for p in [9,21,50]: ind[f'ema_{p}']=lib.ema(df['close'],p)
        ind['rsi_14']=lib.rsi(df['close'],14); ind['rsi_7']=lib.rsi(df['close'],7)
        ind['macd'],ind['macd_signal'],ind['macd_hist']=lib.macd(df['close'])
        ind['stoch_k'],ind['stoch_d']=lib.stoch(df)
        ind['bb_upper'],ind['bb_mid'],ind['bb_lower']=lib.bb(df['close'])
        ind['atr_14']=lib.atr(df,14); ind['atr_7']=lib.atr(df,7); ind['vwap']=lib.vwap(df,24)
        ind['adx'],ind['plus_di'],ind['minus_di']=lib.adx(df)
        ind['supertrend'],ind['supertrend_dir']=lib.supertrend(df)
    def get(self,tf,ind,ts):
        if tf not in self.indicators: return None
        if ind not in self.indicators[tf]:
            if ind in ['open','high','low','close','volume']:
                df=self.timeframes[tf]; vi=df.index[df.index<=ts]
                return df.loc[vi[-1],ind] if len(vi)>0 else None
            return None
        s=self.indicators[tf][ind]; vi=s.index[s.index<=ts]
        return s.loc[vi[-1]] if len(vi)>0 else None

class RuleEngine:
    def __init__(self,mtf): self.mtf=mtf
    def eval_cond(self,c,ts):
        tf=c.get('timeframe','1h'); ind=c['indicator']; op=c['operator']; val=c['value']
        cv=self.mtf.get(tf,ind,ts)
        if cv is None or pd.isna(cv): return False
        if isinstance(val,dict): cmp=self.mtf.get(val.get('timeframe',tf),val['indicator'],ts)
        else: cmp=float(val)
        if cmp is None or pd.isna(cmp): return False
        if op=='>': return cv>cmp
        if op=='<': return cv<cmp
        if op=='>=': return cv>=cmp
        if op=='<=': return cv<=cmp
        if op=='==': return abs(cv-cmp)<1e-10
        if op=='!=': return abs(cv-cmp)>=1e-10
        if op in ['crosses_above','crosses_below']:
            df=self.mtf.timeframes[tf]; pi=df.index[df.index<ts]
            if len(pi)==0: return False
            pt=pi[-1]; pv=self.mtf.get(tf,ind,pt)
            pc=cmp if not isinstance(val,dict) else self.mtf.get(val.get('timeframe',tf),val['indicator'],pt)
            if pv is None or pc is None: return False
            if op=='crosses_above': return pv<=pc and cv>cmp
            return pv>=pc and cv<cmp
        return False
    def eval_rule(self,rule,ts):
        if 'logic' not in rule: return self.eval_cond(rule,ts)
        conds=rule['conditions']
        if rule['logic']=='AND': return all(self.eval_rule(c,ts) if 'logic' in c else self.eval_cond(c,ts) for c in conds)
        if rule['logic']=='OR': return any(self.eval_rule(c,ts) if 'logic' in c else self.eval_cond(c,ts) for c in conds)
        if rule['logic']=='NOT': return not self.eval_rule(conds[0],ts) if conds else True
        return False

# ============================================================
# NEW: SEQUENTIAL RULE ENGINE
# ============================================================

class SequentialRuleEngine:
    """
    Sequential condition logic:
    - Conditions are checked in order (1st, 2nd, 3rd...)
    - Once condition N is met, we wait for condition N+1
    - All conditions must be satisfied in sequence (not necessarily same candle)
    - State resets after entry or after max_wait_bars timeout
    """
    def __init__(self, mtf, max_wait_bars=20):
        self.mtf = mtf
        self.max_wait_bars = max_wait_bars
        self.reset()

    def reset(self):
        self.state = 0  # Which condition we're waiting for (0 = first condition)
        self.state_bars = 0  # How many bars we've been waiting for current condition
        self.satisfied_at = None  # Timestamp when last condition was satisfied

    def eval_cond(self, c, ts):
        """Evaluate a single condition at timestamp"""
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
        if op == '==': return abs(cv - cmp) < 1e-10
        if op == '!=': return abs(cv - cmp) >= 1e-10
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

    def check_sequential(self, conditions, ts):
        """
        Check sequential conditions.
        Returns True if ALL conditions have been satisfied in order.
        """
        if not conditions:
            return True

        # Check if current condition is satisfied
        if self.state < len(conditions):
            current_cond = conditions[self.state]
            if self.eval_cond(current_cond, ts):
                self.state += 1
                self.state_bars = 0
                self.satisfied_at = ts

                # If all conditions satisfied, trigger entry and reset
                if self.state >= len(conditions):
                    self.reset()
                    return True
            else:
                self.state_bars += 1
                # Timeout: reset if waiting too long
                if self.state_bars > self.max_wait_bars:
                    self.reset()

        return False

    def check_simultaneous(self, conditions, ts, logic='AND'):
        """Fallback to standard simultaneous logic"""
        if logic == 'AND':
            return all(self.eval_cond(c, ts) for c in conditions)
        elif logic == 'OR':
            return any(self.eval_cond(c, ts) for c in conditions)
        return False

class BacktestEngine:
    def __init__(self,mtf,capital=10000,comm=0.001,slip=0.0005,spread=0.0002):
        self.mtf=mtf; self.initial=capital; self.comm=comm; self.slip=slip; self.spread=spread; self.reset()
    def reset(self):
        self.capital=self.initial; self.alloc=0; self.equity=[]; self.trades=[]; self.pos=None; self.size=0
        self.entry_p=0; self.entry_t=None; self.sl=None; self.tp=None; self.trail=None; self.hi=None; self.lo=None
        self.n_trades=0; self.n_win=0; self.n_loss=0; self.peak=self.initial; self.max_dd=0
        self.use_sl=True; self.use_tp=True; self.use_trail_flag=False
        # NEW: Sequential rule engine per backtest instance
        self.seq_engine = SequentialRuleEngine(self.mtf)
    def exec_price(self,p,d):
        if d=='buy': ep=p*(1+self.spread/2)
        else: ep=p*(1-self.spread/2)
        sl=ep*self.slip*np.random.uniform(0.5,1.5)
        return ep+sl if d=='buy' else ep-sl
    def pos_size(self,p,atr,risk=0.02,mult=2):
        if atr==0 or pd.isna(atr): return 0
        sd=atr*mult; ra=self.capital*risk; pv=ra/(sd/p)
        return min(pv/p,self.capital/p)
    def enter(self,ts,p,dir,sl_atr=2,tp_atr=3,use_sl=True,use_tp=True,use_trail=False,trail_atr=2):
        if self.pos: return False
        atr=self.mtf.get('1h','atr_14',ts)
        if atr is None or pd.isna(atr): return False
        ep=self.exec_price(p,'buy' if dir=='long' else 'sell')
        sz=self.pos_size(ep,atr)
        if sz<=0: return False
        pv=sz*ep; comm=pv*self.comm
        if pv+comm>self.capital:
            pv=self.capital/(1+self.comm); sz=pv/ep; comm=pv*self.comm
        if pv<=0: return False
        self.capital-=(pv+comm); self.alloc=pv
        self.use_sl=use_sl; self.use_tp=use_tp; self.use_trail_flag=use_trail
        if dir=='long':
            self.sl=ep-atr*sl_atr if use_sl else None
            self.tp=ep+atr*tp_atr if use_tp else None
            self.trail=ep-atr*trail_atr if use_trail else None
            self.hi=ep
        else:
            self.sl=ep+atr*sl_atr if use_sl else None
            self.tp=ep-atr*tp_atr if use_tp else None
            self.trail=ep+atr*trail_atr if use_trail else None
            self.lo=ep
        self.pos=dir; self.size=sz; self.entry_p=ep; self.entry_t=ts
        return True
    def exit(self,ts,p,reason):
        if not self.pos: return False
        ep=self.exec_price(p,'sell' if self.pos=='long' else 'buy')
        pnl=(ep-self.entry_p)*self.size if self.pos=='long' else (self.entry_p-ep)*self.size
        comm=self.size*ep*self.comm; net=pnl-comm
        self.capital+=self.alloc+net; self.alloc=0
        self.trades.append({
            'entry_time':self.entry_t,'exit_time':ts,'direction':self.pos,
            'entry_price':self.entry_p,'exit_price':ep,'position_size':self.size,
            'pnl':net,'pnl_pct':net/(self.size*self.entry_p)*100,
            'reason':reason,'duration_hours':(ts-self.entry_t).total_seconds()/3600
        })
        self.n_trades+=1
        if net>0: self.n_win+=1
        else: self.n_loss+=1
        self.pos=None; self.size=0; self.entry_p=0; self.sl=self.tp=self.trail=self.hi=self.lo=None
        return True
    def check_stops(self,ts,hi,lo,cl):
        if not self.pos: return False
        if self.pos=='long':
            if self.use_sl and self.sl is not None and lo<=self.sl: self.exit(ts,self.sl,'stop_loss'); return True
            if self.use_tp and self.tp is not None and hi>=self.tp: self.exit(ts,self.tp,'take_profit'); return True
            if self.use_trail_flag and self.trail is not None:
                if cl>self.hi: self.hi=cl; self.trail=max(self.trail,cl-(self.hi-self.entry_p)*0.5)
                if lo<=self.trail: self.exit(ts,self.trail,'trailing_stop'); return True
        else:
            if self.use_sl and self.sl is not None and hi>=self.sl: self.exit(ts,self.sl,'stop_loss'); return True
            if self.use_tp and self.tp is not None and lo<=self.tp: self.exit(ts,self.tp,'take_profit'); return True
            if self.use_trail_flag and self.trail is not None:
                if cl<self.lo: self.lo=cl; self.trail=min(self.trail,cl+(self.entry_p-self.lo)*0.5)
                if hi>=self.trail: self.exit(ts,self.trail,'trailing_stop'); return True
        return False
    def update_eq(self,ts,cl):
        un=0
        if self.pos=='long': un=(cl-self.entry_p)*self.size
        elif self.pos=='short': un=(self.entry_p-cl)*self.size
        eq=self.capital+self.alloc+un
        self.equity.append({'timestamp':ts,'equity':eq,'capital':self.capital,'allocated':self.alloc,'unrealized':un,'position':self.pos})
        if eq>self.peak: self.peak=eq
        dd=(self.peak-eq)/self.peak
        if dd>self.max_dd: self.max_dd=dd
    def run(self,tf='1h',entry=None,exit=None,sl_atr=2,tp_atr=3,use_sl=True,use_tp=True,use_trail=False,trail_atr=2,start=None,end=None):
        self.reset()
        df=self.mtf.timeframes[tf]
        if start: df=df[df.index>=pd.to_datetime(start)]
        if end: df=df[df.index<=pd.to_datetime(end)]
        eng=RuleEngine(self.mtf)

        # NEW: Parse entry rule for sequential vs simultaneous
        entry_mode = 'simultaneous'
        entry_conditions = []
        entry_logic = 'AND'

        if entry and 'mode' in entry:
            entry_mode = entry['mode']
        if entry and 'conditions' in entry:
            entry_conditions = entry['conditions']
        if entry and 'logic' in entry:
            entry_logic = entry['logic']
        elif entry and 'conditions' in entry and len(entry['conditions']) > 0 and 'logic' in entry['conditions'][0]:
            entry_logic = entry['conditions'][0]['logic']

        for i,(ts,row) in enumerate(df.iterrows()):
            if i<200: self.update_eq(ts,row['close']); continue
            if self.pos and self.check_stops(ts,row['high'],row['low'],row['close']): self.update_eq(ts,row['close']); continue
            if self.pos and exit and eng.eval_rule(exit,ts): 
                self.exit(ts,row['close'],'signal_exit'); 
                self.update_eq(ts,row['close']); 
                continue
            if not self.pos:
                should_enter = False
                if entry_mode == 'sequential' and entry_conditions:
                    should_enter = self.seq_engine.check_sequential(entry_conditions, ts)
                elif entry:
                    should_enter = eng.eval_rule(entry, ts)

                if should_enter:
                    self.enter(ts,row['close'],'long',sl_atr,tp_atr,use_sl,use_tp,use_trail,trail_atr)
                    # Reset sequential engine after entry
                    if entry_mode == 'sequential':
                        self.seq_engine.reset()
            self.update_eq(ts,row['close'])
        if self.pos: self.exit(df.index[-1],df.iloc[-1]['close'],'end_of_data')
        return self.results()
    def results(self):
        if not self.equity: return {}
        eq_df=pd.DataFrame(self.equity)
        ret=eq_df['equity'].pct_change().dropna()
        tr=(self.capital-self.initial)/self.initial*100
        sharpe=(ret.mean()/ret.std()*np.sqrt(365*24)) if len(ret)>1 and ret.std()>0 else 0
        dr=ret[ret<0]
        sortino=(ret.mean()/dr.std()*np.sqrt(365*24)) if len(dr)>0 and dr.std()>0 else 0
        wr=(self.n_win/self.n_trades*100) if self.n_trades>0 else 0
        gp=sum(t['pnl'] for t in self.trades if t['pnl']>0)
        gl=abs(sum(t['pnl'] for t in self.trades if t['pnl']<0))
        pf=gp/gl if gl>0 else float('inf')
        at=sum(t['pnl'] for t in self.trades)/len(self.trades) if self.trades else 0
        aw=sum(t['pnl'] for t in self.trades if t['pnl']>0)/self.n_win if self.n_win>0 else 0
        al=sum(t['pnl'] for t in self.trades if t['pnl']<0)/self.n_loss if self.n_loss>0 else 0
        exp=(wr/100*aw)+((1-wr/100)*al) if self.n_trades>0 else 0
        return {
            'total_return_pct':tr,'initial_capital':self.initial,'final_capital':self.capital,
            'total_trades':self.n_trades,'winning_trades':self.n_win,'losing_trades':self.n_loss,
            'win_rate':wr,'profit_factor':pf,'sharpe_ratio':sharpe,'sortino_ratio':sortino,
            'max_drawdown_pct':self.max_dd*100,'avg_trade':at,'avg_win':aw,'avg_loss':al,
            'expectancy':exp,'equity_curve':eq_df,'trades':pd.DataFrame(self.trades) if self.trades else pd.DataFrame()
        }

def aggregate_results(all_results):
    if not all_results: return None
    total_trades=sum(r['total_trades'] for r in all_results)
    winning_trades=sum(r['winning_trades'] for r in all_results)
    losing_trades=sum(r['losing_trades'] for r in all_results)
    total_initial=sum(r['initial_capital'] for r in all_results)
    total_final=sum(r['final_capital'] for r in all_results)
    total_return_pct=(total_final-total_initial)/total_initial*100
    win_rate=(winning_trades/total_trades*100) if total_trades>0 else 0
    all_equity=[]
    for r in all_results:
        eq=r['equity_curve'].copy(); all_equity.append(eq)
    if all_equity:
        combined_eq=pd.concat(all_equity).sort_values('timestamp')
        combined_eq=combined_eq.groupby('timestamp').agg({'equity':'sum','capital':'sum','allocated':'sum','unrealized':'sum'}).reset_index()
    else: combined_eq=pd.DataFrame()
    all_trades=pd.concat([r['trades'] for r in all_results if not r['trades'].empty],ignore_index=True) if any(not r['trades'].empty for r in all_results) else pd.DataFrame()
    if len(combined_eq)>1:
        ret=combined_eq['equity'].pct_change().dropna()
        sharpe=(ret.mean()/ret.std()*np.sqrt(365*24)) if ret.std()>0 else 0
        dr=ret[ret<0]
        sortino=(ret.mean()/dr.std()*np.sqrt(365*24)) if len(dr)>0 and dr.std()>0 else 0
        peak=combined_eq['equity'].cummax(); dd=(peak-combined_eq['equity'])/peak; max_dd=dd.max()*100
    else: sharpe=sortino=max_dd=0
    gp=sum(t['pnl'] for _,t in all_trades.iterrows() if t['pnl']>0) if not all_trades.empty else 0
    gl=abs(sum(t['pnl'] for _,t in all_trades.iterrows() if t['pnl']<0)) if not all_trades.empty else 0
    pf=gp/gl if gl>0 else float('inf')
    at=all_trades['pnl'].mean() if not all_trades.empty else 0
    aw=all_trades[all_trades['pnl']>0]['pnl'].mean() if not all_trades.empty and winning_trades>0 else 0
    al=all_trades[all_trades['pnl']<0]['pnl'].mean() if not all_trades.empty and losing_trades>0 else 0
    exp=(win_rate/100*aw)+((1-win_rate/100)*al) if total_trades>0 else 0
    return {
        'total_return_pct':total_return_pct,'initial_capital':total_initial,'final_capital':total_final,
        'total_trades':total_trades,'winning_trades':winning_trades,'losing_trades':losing_trades,
        'win_rate':win_rate,'profit_factor':pf,'sharpe_ratio':sharpe,'sortino_ratio':sortino,
        'max_drawdown_pct':max_dd,'avg_trade':at,'avg_win':aw,'avg_loss':al,
        'expectancy':exp,'equity_curve':combined_eq,'trades':all_trades,'per_pair':all_results
    }

def render_header():
    st.markdown('<div class="main-title">📊 Crypto Backtester Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">1 Year History | Sequential Logic | Real Data | Multi-Timeframe | Multi-Pair | Custom Costs</div>', unsafe_allow_html=True)

def build_condition_card(prefix,key_prefix,index,default=None):
    """Build a condition card. If default dict provided, pre-populate values."""
    indicators=['close','open','high','low','volume','rsi_14','rsi_7','macd_hist','ema_9','ema_21','ema_50','sma_20','sma_50','sma_200','bb_upper','bb_mid','bb_lower','atr_14','atr_7','adx','vwap','supertrend_dir','stoch_k','stoch_d']
    ops=['>','<','>=','<=','==','!=','crosses_above','crosses_below']

    # Extract defaults if provided
    d_tf = default.get('timeframe', '1h') if default else '1h'
    d_ind = default.get('indicator', 'close') if default else 'close'
    d_op = default.get('operator', '>') if default else '>'
    d_val = default.get('value', 50.0) if default else 50.0
    d_is_ind = isinstance(d_val, dict) if default else False
    d_vtf = d_val.get('timeframe', '1h') if d_is_ind else '1h'
    d_vind = d_val.get('indicator', 'close') if d_is_ind else 'close'

    with st.container():
        st.markdown(f'<div class="condition-row">',unsafe_allow_html=True)
        c1,c2,c3,c4,c5=st.columns([2,2,1,2,2])
        with c1: tf=st.selectbox(f"Timeframe",['1h','4h','1d'],index=['1h','4h','1d'].index(d_tf),key=f"{key_prefix}_tf_{index}",label_visibility="collapsed")
        with c2: ind=st.selectbox(f"Indicator",indicators,index=indicators.index(d_ind) if d_ind in indicators else 0,key=f"{key_prefix}_ind_{index}",label_visibility="collapsed")
        with c3: op=st.selectbox(f"Op",ops,index=ops.index(d_op) if d_op in ops else 0,key=f"{key_prefix}_op_{index}",label_visibility="collapsed")
        with c4: val_type=st.selectbox(f"Type",['Number','Indicator'],index=1 if d_is_ind else 0,key=f"{key_prefix}_vt_{index}",label_visibility="collapsed")
        with c5:
            if val_type=='Number':
                val=st.number_input(f"Value",value=float(d_val) if not d_is_ind else 50.0,key=f"{key_prefix}_val_{index}",label_visibility="collapsed")
                result={'timeframe':tf,'indicator':ind,'operator':op,'value':val}
            else:
                val_tf=st.selectbox(f"V-TF",['1h','4h','1d'],index=['1h','4h','1d'].index(d_vtf),key=f"{key_prefix}_vtf_{index}",label_visibility="collapsed")
                val_ind=st.selectbox(f"V-Ind",indicators,index=indicators.index(d_vind) if d_vind in indicators else 0,key=f"{key_prefix}_vind_{index}",label_visibility="collapsed")
                result={'timeframe':tf,'indicator':ind,'operator':op,'value':{'timeframe':val_tf,'indicator':val_ind}}
        st.markdown('</div>',unsafe_allow_html=True)
    return result

def main():
    render_header()
    if 'run_backtest' not in st.session_state: st.session_state.run_backtest=False
    if 'results' not in st.session_state: st.session_state.results=None
    if 'all_results' not in st.session_state: st.session_state.all_results=[]
    if 'entry_rule' not in st.session_state: st.session_state.entry_rule=None
    if 'exit_rule' not in st.session_state: st.session_state.exit_rule=None
    if 'applied_strategy' not in st.session_state: st.session_state.applied_strategy=None
    if 'strategy_config' not in st.session_state: st.session_state.strategy_config=None

    # Apply strategy defaults to session_state BEFORE widgets render
    # This ensures sliders/toggles pick up strategy values on first load
    strat_cfg = st.session_state.get('strategy_config')
    if strat_cfg and st.session_state.get('applied_strategy') != "Custom (Manual)":
        # Risk management defaults
        if 'sl' not in st.session_state: st.session_state.sl = strat_cfg.get('sl_atr', 2.0)
        if 'tp' not in st.session_state: st.session_state.tp = strat_cfg.get('tp_atr', 3.0)
        if 'trail' not in st.session_state: st.session_state.trail = strat_cfg.get('trail_atr', 2.0)
        if 'sl_en' not in st.session_state: st.session_state.sl_en = strat_cfg.get('use_sl', True)
        if 'tp_en' not in st.session_state: st.session_state.tp_en = strat_cfg.get('use_tp', True)
        if 'trail_en' not in st.session_state: st.session_state.trail_en = strat_cfg.get('use_trail', False)
        # Entry mode
        target_mode = "Sequential (One-by-One)" if strat_cfg.get('entry_mode') == 'sequential' else "Simultaneous (AND)"
        if 'entry_mode' not in st.session_state: st.session_state.entry_mode = target_mode

    tab1,tab2,tab3,tab4,tab5=st.tabs(["🎯 Strategy","⚙️ Settings","📈 Results","📋 Trades","🔴 Live"])

    # TAB 1: STRATEGY
    with tab1:
        st.markdown('<div class="section-header">💱 Select Crypto Pairs</div>',unsafe_allow_html=True)
        selected_pairs=st.multiselect("Choose pairs (20 available)",options=list(CRYPTO_PAIRS.keys()),default=['BTC/USDT'],key="selected_pairs")
        if not selected_pairs: st.warning("⚠️ Select at least one pair."); st.stop()
        pair_chips=" ".join([f"<span style='background:rgba(0,212,255,0.2);color:#00d4ff;padding:4px 12px;border-radius:12px;margin:2px;display:inline-block;font-size:0.85rem;'>{p}</span>" for p in selected_pairs])
        st.markdown(f"<div style='margin:0.5rem 0 1rem 0;'>Selected: {pair_chips}</div>",unsafe_allow_html=True)

        st.markdown('<div class="section-header">⏱️ Data Settings</div>',unsafe_allow_html=True)
        col_ds1,col_ds2=st.columns(2)
        with col_ds1: data_source=st.selectbox("Data Source",['Auto (Best Available)','Binance','CoinGecko','CryptoCompare','Synthetic (Demo)'],key="data_source")
        with col_ds2:
            # Use a separate key for preset target to avoid widget state conflict
            if 'data_limit_preset' not in st.session_state:
                st.session_state.data_limit_preset = 500
            data_limit = st.slider("Candles to Fetch", 100, 10000, 
                                    value=st.session_state.data_limit_preset, 
                                    step=100, key="data_limit")
            # Sync back so presets can read current value
            st.session_state.data_limit_preset = data_limit

        # Quick presets
        preset_cols = st.columns(4)
        with preset_cols[0]:
            if st.button("1 Month (~720)", key="preset_1m", use_container_width=True):
                st.session_state.data_limit_preset = 720
                st.rerun()
        with preset_cols[1]:
            if st.button("3 Months (~2160)", key="preset_3m", use_container_width=True):
                st.session_state.data_limit_preset = 2160
                st.rerun()
        with preset_cols[2]:
            if st.button("6 Months (~4320)", key="preset_6m", use_container_width=True):
                st.session_state.data_limit_preset = 4320
                st.rerun()
        with preset_cols[3]:
            if st.button("1 Year (~8760)", key="preset_1y", use_container_width=True):
                st.session_state.data_limit_preset = 8760
                st.rerun()
        st.caption(f"Fetching ~{data_limit} candles per pair | Auto-fallback enabled | Max: 1 year of 1h data (~8,760 candles)")

        st.markdown("---")
        st.markdown('<div class="section-header">📚 Strategy Library</div>',unsafe_allow_html=True)

        # Strategy definitions - pre-built profitable strategies
        STRATEGIES = {
            "Custom (Manual)": {
                "desc": "Build your own strategy from scratch",
                "entry_mode": "simultaneous",
                "entry_conds": [],
                "exit_conds": [],
                "sl_atr": 2.0,
                "tp_atr": 3.0,
                "use_sl": True,
                "use_tp": True,
                "use_trail": False,
            },
            "RSI Oversold Bounce": {
                "desc": "Buy when RSI is oversold and starts recovering. Classic mean-reversion.",
                "entry_mode": "sequential",
                "entry_conds": [
                    {"timeframe": "1h", "indicator": "rsi_14", "operator": "<", "value": 30},
                    {"timeframe": "1h", "indicator": "rsi_14", "operator": ">", "value": 35},
                ],
                "exit_conds": [
                    {"timeframe": "1h", "indicator": "rsi_14", "operator": ">", "value": 65},
                ],
                "sl_atr": 2.0,
                "tp_atr": 4.0,
                "use_sl": True,
                "use_tp": True,
                "use_trail": False,
            },
            "EMA Golden Cross": {
                "desc": "Trend following - buy on EMA9 crossing above EMA21 with volume confirmation.",
                "entry_mode": "simultaneous",
                "entry_conds": [
                    {"timeframe": "1h", "indicator": "ema_9", "operator": "crosses_above", "value": {"timeframe": "1h", "indicator": "ema_21"}},
                    {"timeframe": "1h", "indicator": "volume", "operator": ">", "value": {"timeframe": "1h", "indicator": "sma_20"}},
                ],
                "exit_conds": [
                    {"timeframe": "1h", "indicator": "ema_9", "operator": "crosses_below", "value": {"timeframe": "1h", "indicator": "ema_21"}},
                ],
                "sl_atr": 2.5,
                "tp_atr": 5.0,
                "use_sl": True,
                "use_tp": True,
                "use_trail": True,
                "trail_atr": 2.0,
            },
            "MACD Momentum": {
                "desc": "Enter on MACD histogram turning positive with RSI confirmation.",
                "entry_mode": "sequential",
                "entry_conds": [
                    {"timeframe": "1h", "indicator": "macd_hist", "operator": ">", "value": 0},
                    {"timeframe": "1h", "indicator": "rsi_14", "operator": ">", "value": 50},
                ],
                "exit_conds": [
                    {"timeframe": "1h", "indicator": "macd_hist", "operator": "<", "value": 0},
                ],
                "sl_atr": 2.0,
                "tp_atr": 4.0,
                "use_sl": True,
                "use_tp": True,
                "use_trail": False,
            },
            "Bollinger Squeeze": {
                "desc": "Mean reversion - buy when price touches lower Bollinger Band with RSI oversold.",
                "entry_mode": "simultaneous",
                "entry_conds": [
                    {"timeframe": "1h", "indicator": "close", "operator": "<", "value": {"timeframe": "1h", "indicator": "bb_lower"}},
                    {"timeframe": "1h", "indicator": "rsi_14", "operator": "<", "value": 35},
                ],
                "exit_conds": [
                    {"timeframe": "1h", "indicator": "close", "operator": ">", "value": {"timeframe": "1h", "indicator": "bb_mid"}},
                ],
                "sl_atr": 1.5,
                "tp_atr": 3.0,
                "use_sl": True,
                "use_tp": True,
                "use_trail": False,
            },
            "SuperTrend Follower": {
                "desc": "Pure trend following using SuperTrend indicator. Simple and effective.",
                "entry_mode": "simultaneous",
                "entry_conds": [
                    {"timeframe": "1h", "indicator": "supertrend_dir", "operator": "==", "value": 1},
                    {"timeframe": "1h", "indicator": "adx", "operator": ">", "value": 25},
                ],
                "exit_conds": [
                    {"timeframe": "1h", "indicator": "supertrend_dir", "operator": "==", "value": -1},
                ],
                "sl_atr": 3.0,
                "tp_atr": 6.0,
                "use_sl": True,
                "use_tp": False,
                "use_trail": True,
                "trail_atr": 2.5,
            },
            "VWAP Deviation": {
                "desc": "Institutional style - buy when price falls below VWAP with volume spike.",
                "entry_mode": "sequential",
                "entry_conds": [
                    {"timeframe": "1h", "indicator": "close", "operator": "<", "value": {"timeframe": "1h", "indicator": "vwap"}},
                    {"timeframe": "1h", "indicator": "volume", "operator": ">", "value": {"timeframe": "1h", "indicator": "sma_20"}},
                ],
                "exit_conds": [
                    {"timeframe": "1h", "indicator": "close", "operator": ">", "value": {"timeframe": "1h", "indicator": "vwap"}},
                ],
                "sl_atr": 2.0,
                "tp_atr": 3.5,
                "use_sl": True,
                "use_tp": True,
                "use_trail": False,
            },
            "Stochastic Reversal": {
                "desc": "Counter-trend strategy using Stochastic oscillator extreme readings.",
                "entry_mode": "sequential",
                "entry_conds": [
                    {"timeframe": "1h", "indicator": "stoch_k", "operator": "<", "value": 20},
                    {"timeframe": "1h", "indicator": "stoch_k", "operator": "crosses_above", "value": {"timeframe": "1h", "indicator": "stoch_d"}},
                ],
                "exit_conds": [
                    {"timeframe": "1h", "indicator": "stoch_k", "operator": ">", "value": 80},
                ],
                "sl_atr": 1.5,
                "tp_atr": 3.0,
                "use_sl": True,
                "use_tp": True,
                "use_trail": False,
            },
            "Multi-Timeframe Breakout": {
                "desc": "Higher timeframe trend + lower timeframe entry. 1d trend, 1h entry.",
                "entry_mode": "simultaneous",
                "entry_conds": [
                    {"timeframe": "1d", "indicator": "close", "operator": ">", "value": {"timeframe": "1d", "indicator": "ema_50"}},
                    {"timeframe": "1h", "indicator": "close", "operator": "crosses_above", "value": {"timeframe": "1h", "indicator": "ema_9"}},
                ],
                "exit_conds": [
                    {"timeframe": "1h", "indicator": "close", "operator": "crosses_below", "value": {"timeframe": "1h", "indicator": "ema_21"}},
                ],
                "sl_atr": 2.5,
                "tp_atr": 5.0,
                "use_sl": True,
                "use_tp": True,
                "use_trail": True,
                "trail_atr": 2.0,
            },
            "ATR Volatility Squeeze": {
                "desc": "Enter after volatility contraction (low ATR) with directional breakout.",
                "entry_mode": "sequential",
                "entry_conds": [
                    {"timeframe": "1h", "indicator": "atr_14", "operator": "<", "value": {"timeframe": "1h", "indicator": "sma_20"}},
                    {"timeframe": "1h", "indicator": "close", "operator": ">", "value": {"timeframe": "1h", "indicator": "sma_20"}},
                ],
                "exit_conds": [
                    {"timeframe": "1h", "indicator": "close", "operator": "<", "value": {"timeframe": "1h", "indicator": "ema_9"}},
                ],
                "sl_atr": 1.5,
                "tp_atr": 4.0,
                "use_sl": True,
                "use_tp": True,
                "use_trail": False,
            },
        }

        # Strategy selector
        strat_names = list(STRATEGIES.keys())
        selected_strategy = st.selectbox(
            "Choose a Strategy",
            strat_names,
            key="selected_strategy",
            help="Select a pre-built strategy or 'Custom' to build your own"
        )

        strat = STRATEGIES[selected_strategy]

        # Show strategy card
        st.markdown(f"""
        <div style="background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.2);border-radius:12px;padding:12px;margin:8px 0;">
            <div style="color:#00d4ff;font-weight:600;font-size:0.95rem;">{selected_strategy}</div>
            <div style="color:#8892b0;font-size:0.85rem;margin-top:4px;">{strat['desc']}</div>
            <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;">
                <span style="background:rgba(0,200,83,0.15);color:#00c853;padding:2px 8px;border-radius:6px;font-size:0.75rem;">SL: {strat['sl_atr']}x ATR</span>
                <span style="background:rgba(0,200,83,0.15);color:#00c853;padding:2px 8px;border-radius:6px;font-size:0.75rem;">TP: {strat['tp_atr']}x ATR</span>
                <span style="background:rgba(0,212,255,0.15);color:#00d4ff;padding:2px 8px;border-radius:6px;font-size:0.75rem;">{'Trailing' if strat.get('use_trail') else 'Fixed'} Stop</span>
                <span style="background:rgba(123,44,191,0.15);color:#b794f6;padding:2px 8px;border-radius:6px;font-size:0.75rem;">{'Sequential' if strat['entry_mode'] == 'sequential' else 'Simultaneous'} Entry</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Apply strategy button
        if selected_strategy != "Custom (Manual)" and st.button("🎯 Apply This Strategy", type="primary", use_container_width=True, key="apply_strategy"):
            st.session_state.applied_strategy = selected_strategy
            st.session_state.strategy_config = strat
            st.rerun()

        # If strategy applied, show indicator
        if st.session_state.get('applied_strategy') == selected_strategy and selected_strategy != "Custom (Manual)":
            st.success(f"✅ {selected_strategy} applied! Configure below or go to Settings to adjust risk.")

        st.markdown("---")
        st.markdown('<div class="section-header">🟢 Entry Rules</div>',unsafe_allow_html=True)

        # NEW: Entry Mode Selection
        entry_mode = st.segmented_control(
            "How conditions trigger entry",
            ["Simultaneous (AND)", "Sequential (One-by-One)"],
            default=st.session_state.get('entry_mode', "Simultaneous (AND)"),
            key="entry_mode"
        )

        is_sequential = entry_mode == "Sequential (One-by-One)"

        if is_sequential:
            st.markdown("""
            <div style="background:rgba(123,44,191,0.1);border:1px solid rgba(123,44,191,0.3);border-radius:8px;padding:10px;margin:8px 0;">
            <span style="color:#b794f6;font-size:0.9rem;">📋 <b>Sequential Mode:</b> Conditions are checked in order. 
            Once condition 1 is met, the system waits for condition 2, then condition 3, etc. 
            All conditions must be satisfied in sequence (not necessarily on the same candle). 
            State resets after entry or after timeout.</span>
            </div>
            """, unsafe_allow_html=True)
            seq_timeout = st.slider("Max Wait Bars (timeout reset)", 5, 100, 20, 5, key="seq_timeout",
                                  help="If waiting for next condition exceeds this many bars, reset sequence")
        else:
            seq_timeout = 20
            st.markdown("""
            <div style="background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.3);border-radius:8px;padding:10px;margin:8px 0;">
            <span style="color:#00d4ff;font-size:0.9rem;">⚡ <b>Simultaneous Mode:</b> All conditions must be met at the SAME candle. 
            Use AND for all conditions together, OR for any condition.</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("**Primary Entry Group**")
        if not is_sequential:
            entry_g1_logic=st.segmented_control("Group 1 Logic",["AND","OR"],default="AND",key="ent_g1_logic")
        else:
            entry_g1_logic = "AND"  # Sequential always uses AND internally
            st.markdown("<span class='seq-badge'>SEQUENTIAL</span> Conditions checked in order below:", unsafe_allow_html=True)

        # Check if a strategy is applied and we need to set defaults
        strat_config = st.session_state.get('strategy_config', None)
        is_applied = st.session_state.get('applied_strategy') and st.session_state.get('applied_strategy') != "Custom (Manual)"

        # Set entry mode from strategy if applied
        if is_applied and strat_config:
            target_mode = "Sequential (One-by-One)" if strat_config.get('entry_mode') == 'sequential' else "Simultaneous (AND)"
            if st.session_state.get('entry_mode') != target_mode:
                st.session_state.entry_mode = target_mode

        # Determine number of entry conditions from strategy
        default_n_ent = 2
        if is_applied and strat_config and strat_config.get('entry_conds'):
            default_n_ent = len(strat_config['entry_conds'])

        n_ent_g1=st.slider("Conditions",1,4,default_n_ent,key="n_ent_g1")

        # Build entry conditions with strategy defaults
        entry_g1_conds = []
        for i in range(n_ent_g1):
            default_cond = None
            if is_applied and strat_config and i < len(strat_config.get('entry_conds', [])):
                default_cond = strat_config['entry_conds'][i]
            entry_g1_conds.append(build_condition_card("Entry","ent_g1",i,default=default_cond))

        if is_sequential:
            # For sequential, we show order numbers
            for i, cond in enumerate(entry_g1_conds):
                cond['_order'] = i + 1

        entry_conditions=[{'logic':entry_g1_logic,'conditions':entry_g1_conds}]
        use_ent_g2=st.toggle("➕ Add Second Entry Group",value=False,key="use_ent_g2")
        if use_ent_g2:
            st.markdown("**Secondary Entry Group**")
            if not is_sequential:
                entry_g2_logic=st.segmented_control("Group 2 Logic",["AND","OR"],default="OR",key="ent_g2_logic")
            else:
                entry_g2_logic = "AND"
                st.markdown("<span class='seq-badge'>SEQUENTIAL</span>", unsafe_allow_html=True)
            n_ent_g2=st.slider("Conditions",1,4,1,key="n_ent_g2")
            entry_g2_conds=[build_condition_card("Entry","ent_g2",i) for i in range(n_ent_g2)]
            if is_sequential:
                for i, cond in enumerate(entry_g2_conds):
                    cond['_order'] = i + 1
            entry_conditions.append({'logic':entry_g2_logic,'conditions':entry_g2_conds})
            if not is_sequential:
                entry_group_logic=st.segmented_control("How groups combine",["AND","OR"],default="OR",key="ent_groups")
            else:
                entry_group_logic = "OR"
                st.info("In Sequential mode, groups combine with OR (either sequence triggers entry)")
            entry_rule={'mode':'sequential' if is_sequential else 'simultaneous','logic':entry_group_logic,'conditions':entry_conditions,'seq_timeout':seq_timeout}
        else: 
            entry_rule={'mode':'sequential' if is_sequential else 'simultaneous','logic':entry_g1_logic,'conditions':entry_conditions[0]['conditions'],'seq_timeout':seq_timeout}

        st.markdown("---")
        st.markdown('<div class="section-header">🔴 Exit Rules</div>',unsafe_allow_html=True)
        st.markdown("**Primary Exit Group**")
        exit_g1_logic=st.segmented_control("Group 1 Logic",["OR","AND"],default="OR",key="ext_g1_logic")
        # Determine number of exit conditions from strategy
        default_n_ext = 2
        if is_applied and strat_config and strat_config.get('exit_conds'):
            default_n_ext = len(strat_config['exit_conds'])

        n_ext_g1=st.slider("Conditions",1,4,default_n_ext,key="n_ext_g1")

        # Build exit conditions with strategy defaults
        exit_g1_conds = []
        for i in range(n_ext_g1):
            default_cond = None
            if is_applied and strat_config and i < len(strat_config.get('exit_conds', [])):
                default_cond = strat_config['exit_conds'][i]
            exit_g1_conds.append(build_condition_card("Exit","ext_g1",i,default=default_cond))
        exit_conditions=[{'logic':exit_g1_logic,'conditions':exit_g1_conds}]
        use_ext_g2=st.toggle("➕ Add Second Exit Group",value=False,key="use_ext_g2")
        if use_ext_g2:
            st.markdown("**Secondary Exit Group**")
            exit_g2_logic=st.segmented_control("Group 2 Logic",["OR","AND"],default="OR",key="ext_g2_logic")
            n_ext_g2=st.slider("Conditions",1,4,1,key="n_ext_g2")
            exit_g2_conds=[build_condition_card("Exit","ext_g2",i) for i in range(n_ext_g2)]
            exit_conditions.append({'logic':exit_g2_logic,'conditions':exit_g2_conds})
            exit_group_logic=st.segmented_control("How groups combine",["OR","AND"],default="OR",key="ext_groups")
            exit_rule={'logic':exit_group_logic,'conditions':exit_conditions}
        else: exit_rule=exit_conditions[0]
        st.session_state.entry_rule=entry_rule
        st.session_state.exit_rule=exit_rule

    # TAB 2: SETTINGS
    with tab2:
        st.markdown('<div class="section-header">Risk Management</div>',unsafe_allow_html=True)
        col1,col2=st.columns(2)
        with col1:
            st.markdown("<div class='glass-card'>",unsafe_allow_html=True)
            st.markdown("**Stop Loss**")
            use_sl=st.toggle("Enable Stop Loss",value=st.session_state.get('sl_en',True),key="sl_en")
            sl_atr=st.slider("ATR Multiplier",0.5,5.0,value=st.session_state.get('sl',2.0),step=0.5,key="sl",disabled=not use_sl)
            st.markdown("</div>",unsafe_allow_html=True)
            st.markdown("<div class='glass-card'>",unsafe_allow_html=True)
            st.markdown("**Take Profit**")
            use_tp=st.toggle("Enable Take Profit",value=st.session_state.get('tp_en',True),key="tp_en")
            tp_atr=st.slider("ATR Multiplier",1.0,10.0,value=st.session_state.get('tp',3.0),step=0.5,key="tp",disabled=not use_tp)
            st.markdown("</div>",unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='glass-card'>",unsafe_allow_html=True)
            st.markdown("**Trailing Stop**")
            use_trail=st.toggle("Enable",value=st.session_state.get('trail_en',False),key="trail_en")
            trail_atr=st.slider("ATR Multiplier",0.5,5.0,value=st.session_state.get('trail',2.0),step=0.5,key="trail",disabled=not use_trail)
            st.markdown("</div>",unsafe_allow_html=True)
            st.markdown("<div class='glass-card'>",unsafe_allow_html=True)
            st.markdown("**Capital**")
            capital=st.number_input("Initial ($)",1000,100000,10000,1000,key="cap")
            st.markdown("</div>",unsafe_allow_html=True)

        # NEW: Commission & Slippage controls
        st.markdown('<div class="section-header">Execution Costs</div>',unsafe_allow_html=True)
        cost_col1, cost_col2, cost_col3 = st.columns(3)
        with cost_col1:
            st.markdown("<div class='glass-card'>",unsafe_allow_html=True)
            st.markdown("**Commission**")
            commission_pct = st.slider("Per trade (%)", 0.0, 1.0, 0.1, 0.01, key="comm_pct",
                                      help="Trading fee per side as percentage (e.g., 0.1% = typical exchange fee)")
            commission = commission_pct / 100.0
            st.caption(f"Equivalent: {commission:.4f} fraction")
            st.markdown("</div>",unsafe_allow_html=True)
        with cost_col2:
            st.markdown("<div class='glass-card'>",unsafe_allow_html=True)
            st.markdown("**Slippage**")
            slippage_pct = st.slider("Per trade (%)", 0.0, 1.0, 0.05, 0.01, key="slip_pct",
                                    help="Price slippage on entry/exit as percentage")
            slippage = slippage_pct / 100.0
            st.caption(f"Equivalent: {slippage:.4f} fraction")
            st.markdown("</div>",unsafe_allow_html=True)
        with cost_col3:
            st.markdown("<div class='glass-card'>",unsafe_allow_html=True)
            st.markdown("**Spread**")
            spread_pct = st.slider("Bid-Ask (%)", 0.0, 0.5, 0.02, 0.005, key="spread_pct",
                                  help="Bid-ask spread as percentage (already factored into execution price)")
            spread = spread_pct / 100.0
            st.caption(f"Equivalent: {spread:.4f} fraction")
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown('<div class="section-header">Backtest Period</div>',unsafe_allow_html=True)
        col3,col4=st.columns(2)
        with col3: start_date=st.date_input("Start Date",datetime(2026,3,1),key="start")
        with col4: end_date=st.date_input("End Date",datetime(2026,5,15),key="end")
        st.markdown("---")
        if st.button("🚀 RUN BACKTEST",type="primary",use_container_width=True,key="run_btn"):
            st.session_state.run_backtest=True
            st.rerun()

    # TAB 3: RESULTS
    with tab3:
        if not st.session_state.run_backtest:
            st.info("👆 Configure strategy and tap **RUN BACKTEST** in Settings tab")
            cols=st.columns(4)
            for col in cols:
                with col: st.markdown("""<div class="glass-card"><div class="metric-box"><div class="metric-value">--</div><div class="metric-label">Waiting...</div></div></div>""",unsafe_allow_html=True)
        else:
            selected_pairs=st.session_state.selected_pairs
            data_limit=st.session_state.data_limit
            data_source_key=SOURCE_MAP.get(st.session_state.data_source,'auto')
            progress_bar=st.progress(0); status_text=st.empty()
            all_results=[]; sources_used={}
            for idx,pair in enumerate(selected_pairs):
                progress_bar.progress(idx/len(selected_pairs))
                status_text.text(f"Fetching data for {pair}... ({idx+1}/{len(selected_pairs)})")
                df_1h,df_4h,df_1d,source=fetch_pair_data(pair,interval='1h',limit=data_limit,source=data_source_key)
                sources_used[pair]=source
                if df_1h is None or df_1h.empty: st.warning(f"Could not fetch data for {pair}. Skipping..."); continue
                mtf=MultiTimeframeManager(); mtf.add_timeframe('1h',df_1h); mtf.add_timeframe('4h',df_4h); mtf.add_timeframe('1d',df_1d)
                status_text.text(f"Backtesting {pair}... ({idx+1}/{len(selected_pairs)})")
                bt=BacktestEngine(mtf,capital=st.session_state.cap,
                                  comm=st.session_state.comm_pct/100.0,
                                  slip=st.session_state.slip_pct/100.0,
                                  spread=st.session_state.spread_pct/100.0)
                res=bt.run(tf='1h',entry=st.session_state.entry_rule,exit=st.session_state.exit_rule,
                          sl_atr=st.session_state.sl,tp_atr=st.session_state.tp,use_sl=st.session_state.sl_en,
                          use_tp=st.session_state.tp_en,use_trail=st.session_state.trail_en,trail_atr=st.session_state.trail,
                          start=st.session_state.start,end=st.session_state.end)
                if res: res['pair']=pair; res['source']=source; all_results.append(res)
                if idx<len(selected_pairs)-1: time.sleep(0.3)
            progress_bar.progress(1.0); status_text.empty(); progress_bar.empty()
            results=aggregate_results(all_results)
            if not results or results['total_trades']==0:
                st.error("No results generated. Check your conditions, selected pairs, and date range.")
                st.session_state.run_backtest=False
            else:
                st.session_state.results=results; st.session_state.all_results=all_results
                st.markdown('<div class="section-header">📡 Data Sources Used</div>',unsafe_allow_html=True)
                source_chips=" ".join([f"<span style='background:rgba(0,212,255,0.15);color:#00d4ff;padding:3px 10px;border-radius:10px;margin:2px;display:inline-block;font-size:0.8rem;'>{p}: {s}</span>" for p,s in sources_used.items()])
                st.markdown(f"<div>{source_chips}</div>",unsafe_allow_html=True)
                if any('Synthetic' in s for s in sources_used.values()): st.info("ℹ️ Some pairs used synthetic demo data. Select 'Synthetic (Demo)' in Strategy tab for all demo data.")

                # NEW: Show entry mode badge
                entry_mode_display = "Sequential" if st.session_state.entry_rule.get('mode') == 'sequential' else "Simultaneous"
                st.markdown(f"""
                <div style="margin:10px 0;">
                    <span style="background:rgba(123,44,191,0.2);color:#b794f6;padding:4px 12px;border-radius:8px;font-size:0.85rem;font-weight:600;">
                        Entry Mode: {entry_mode_display}
                    </span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="section-header">Per-Pair Performance</div>',unsafe_allow_html=True)
                pair_cols=st.columns(min(len(all_results),5))
                for i,pair_res in enumerate(all_results):
                    with pair_cols[i%len(pair_cols)]:
                        ret_color="metric-positive" if pair_res['total_return_pct']>0 else "metric-negative"
                        source_badge="🟢" if 'Synthetic' not in pair_res.get('source','') else "🟡"
                        st.markdown(f"""<div class="glass-card-blue"><div class="metric-box"><div class="metric-value" style="font-size:0.9rem;">{source_badge} {pair_res.get('pair','Unknown')}</div><div class="metric-value {ret_color}" style="font-size:1.2rem;">{pair_res['total_return_pct']:+.2f}%</div><div class="metric-label">{pair_res['total_trades']} trades | WR {pair_res['win_rate']:.0f}%</div></div></div>""",unsafe_allow_html=True)
                st.markdown('<div class="section-header">Combined Performance Metrics</div>',unsafe_allow_html=True)
                c1,c2,c3,c4=st.columns(4)
                with c1:
                    is_pos=results['total_return_pct']>0; card_class="glass-card-green" if is_pos else "glass-card-red"
                    st.markdown(f"""<div class="{card_class}"><div class="metric-box"><div class="metric-value {'metric-positive' if is_pos else 'metric-negative'}">{results['total_return_pct']:+.2f}%</div><div class="metric-label">Total Return</div></div></div>""",unsafe_allow_html=True)
                with c2: st.markdown(f"""<div class="glass-card"><div class="metric-box"><div class="metric-value">{results['total_trades']}</div><div class="metric-label">Total Trades</div></div></div>""",unsafe_allow_html=True)
                with c3: st.markdown(f"""<div class="glass-card"><div class="metric-box"><div class="metric-value">{results['win_rate']:.1f}%</div><div class="metric-label">Win Rate</div></div></div>""",unsafe_allow_html=True)
                with c4: st.markdown(f"""<div class="glass-card"><div class="metric-box"><div class="metric-value">{results['sharpe_ratio']:.2f}</div><div class="metric-label">Sharpe Ratio</div></div></div>""",unsafe_allow_html=True)
                c5,c6,c7,c8=st.columns(4)
                with c5: st.markdown(f"""<div class="glass-card"><div class="metric-box"><div class="metric-value metric-negative">{results['max_drawdown_pct']:.2f}%</div><div class="metric-label">Max Drawdown</div></div></div>""",unsafe_allow_html=True)
                with c6: st.markdown(f"""<div class="glass-card"><div class="metric-box"><div class="metric-value">{results['profit_factor']:.2f}</div><div class="metric-label">Profit Factor</div></div></div>""",unsafe_allow_html=True)
                with c7: st.markdown(f"""<div class="glass-card"><div class="metric-box"><div class="metric-value">${results['expectancy']:.2f}</div><div class="metric-label">Expectancy</div></div></div>""",unsafe_allow_html=True)
                with c8: st.markdown(f"""<div class="glass-card"><div class="metric-box"><div class="metric-value">${results['final_capital']:,.0f}</div><div class="metric-label">Final Capital</div></div></div>""",unsafe_allow_html=True)
                st.markdown('<div class="section-header">Charts</div>',unsafe_allow_html=True)
                eq_df=results['equity_curve']
                tab_chart1,tab_chart2=st.tabs(["Equity Curve","Drawdown"])
                with tab_chart1:
                    if not eq_df.empty:
                        chart_data=pd.DataFrame({'Equity':eq_df.set_index('timestamp')['equity'],'Peak':eq_df.set_index('timestamp')['equity'].cummax()})
                        st.line_chart(chart_data,use_container_width=True)
                    else: st.info("No equity data available.")
                with tab_chart2:
                    if not eq_df.empty:
                        peak=eq_df['equity'].cummax(); dd=(peak-eq_df['equity'])/peak*100
                        st.area_chart(pd.DataFrame({'Drawdown %':dd.values},index=eq_df['timestamp']),use_container_width=True,color=['#ff1744'])
                    else: st.info("No drawdown data available.")
                st.markdown("---")
                if st.button("🔄 Run Another Backtest",use_container_width=True,key="reset_btn"):
                    st.session_state.run_backtest=False; st.session_state.results=None; st.session_state.all_results=[]; st.rerun()

    # TAB 4: TRADES
    with tab4:
        if st.session_state.results is None: st.info("👆 Run a backtest first in the **Results** tab")
        else:
            results=st.session_state.results; trades_df=results['trades']; all_results=st.session_state.all_results
            if not trades_df.empty:
                st.markdown('<div class="section-header">Trade History</div>',unsafe_allow_html=True)
                if len(all_results)>1:
                    st.markdown('<div class="section-header">Per-Pair Summary</div>',unsafe_allow_html=True)
                    pair_summary=[{'Pair':r.get('pair','Unknown'),'Source':r.get('source','Unknown'),'Trades':r['total_trades'],'Win Rate':f"{r['win_rate']:.1f}%",'Return':f"{r['total_return_pct']:+.2f}%",'Profit Factor':f"{r['profit_factor']:.2f}",'Sharpe':f"{r['sharpe_ratio']:.2f}"} for r in all_results]
                    st.dataframe(pd.DataFrame(pair_summary),use_container_width=True,hide_index=True)
                wins=trades_df[trades_df['pnl']>0]; losses=trades_df[trades_df['pnl']<=0]
                c1,c2,c3=st.columns(3)
                with c1: st.markdown(f"""<div class="glass-card-green"><div class="metric-box"><div class="metric-value metric-positive">{len(wins)}</div><div class="metric-label">Winning Trades</div></div></div>""",unsafe_allow_html=True)
                with c2: st.markdown(f"""<div class="glass-card-red"><div class="metric-box"><div class="metric-value metric-negative">{len(losses)}</div><div class="metric-label">Losing Trades</div></div></div>""",unsafe_allow_html=True)
                with c3:
                    avg_dur=trades_df['duration_hours'].mean()
                    st.markdown(f"""<div class="glass-card"><div class="metric-box"><div class="metric-value">{avg_dur:.1f}h</div><div class="metric-label">Avg Duration</div></div></div>""",unsafe_allow_html=True)
                if 'pair' not in trades_df.columns and len(all_results)>1:
                    trades_with_pair=[]
                    for r in all_results: tdf=r['trades'].copy(); tdf['pair']=r.get('pair','Unknown'); trades_with_pair.append(tdf)
                    trades_df=pd.concat(trades_with_pair,ignore_index=True)
                if 'pair' in trades_df.columns:
                    display_df=trades_df[['pair','entry_time','exit_time','pnl','pnl_pct','reason','duration_hours']].copy()
                    display_df.columns=['Pair','Entry','Exit','P&L ($)','P&L (%)','Reason','Hours']
                else:
                    display_df=trades_df[['entry_time','exit_time','pnl','pnl_pct','reason','duration_hours']].copy()
                    display_df.columns=['Entry','Exit','P&L ($)','P&L (%)','Reason','Hours']
                def color_pnl(val):
                    if isinstance(val,(int,float)): return 'background-color: rgba(0,200,83,0.3)' if val>0 else 'background-color: rgba(255,23,68,0.3)'
                    return ''
                st.dataframe(display_df.style.map(color_pnl,subset=['P&L ($)','P&L (%)']),use_container_width=True,height=400)
                csv=trades_df.to_csv(index=False)
                st.download_button("📥 Download CSV",csv,"trades.csv","text/csv",use_container_width=True)
            else: st.warning("No trades were generated. Try adjusting your strategy conditions or date range.")

    # TAB 5: LIVE
    with tab5:
        st.markdown('<div class="section-header">🔴 Live Price Monitor</div>',unsafe_allow_html=True)
        st.caption("Real-time price updates via API polling")
        live_pairs=st.multiselect("Select pairs to monitor",options=list(CRYPTO_PAIRS.keys()),default=['BTC/USDT','ETH/USDT'],key="live_pairs")
        auto_refresh=st.toggle("Auto-refresh every 10s",value=True,key="auto_refresh")
        if auto_refresh: st.markdown("<span class='live-indicator'></span><span style='color:#00c853;font-size:0.9rem;'>Live monitoring active</span>",unsafe_allow_html=True)
        if st.button("🔄 Refresh Now",key="refresh_now") or auto_refresh:
            live_data=[]
            for pair in live_pairs:
                price=get_live_price(pair); config=CRYPTO_PAIRS[pair]
                if price and price>0:
                    change_pct=((price-config['base_price'])/config['base_price'])*100
                    live_data.append({'Pair':pair,'Price':f"${price:,.4f}" if price<1 else f"${price:,.2f}",'24h Change':f"{change_pct:+.2f}%",'Source':'Live API'})
                else:
                    np.random.seed(hash(pair)%10000)
                    synthetic=config['base_price']*(1+np.random.normal(0,0.02))
                    change_pct=((synthetic-config['base_price'])/config['base_price'])*100
                    live_data.append({'Pair':pair,'Price':f"${synthetic:,.4f}" if synthetic<1 else f"${synthetic:,.2f}",'24h Change':f"{change_pct:+.2f}%",'Source':'Simulated'})
            if live_data:
                st.dataframe(pd.DataFrame(live_data),use_container_width=True,hide_index=True)
                st.markdown('<div class="section-header">Price Visualization</div>',unsafe_allow_html=True)
                price_cols=st.columns(min(len(live_data),4))
                for i,row in enumerate(live_data):
                    with price_cols[i%len(price_cols)]:
                        is_up='+' in row['24h Change']; card="glass-card-green" if is_up else "glass-card-red"
                        st.markdown(f"""<div class="{card}"><div class="metric-box"><div class="metric-value" style="font-size:1.0rem;">{row['Pair']}</div><div class="metric-value" style="font-size:1.4rem;">{row['Price']}</div><div class="metric-label">{row['24h Change']} | {row['Source']}</div></div></div>""",unsafe_allow_html=True)
            else: st.info("No live data available.")
        if auto_refresh: st.caption("Note: True WebSocket streaming requires external infrastructure. This uses API polling.")

    st.markdown("""<div class="footer">Crypto Backtester Pro v5.3 | 1 Year History | Sequential Conditions | Custom Costs | Universal Data Sources | Live Streaming | Built with Streamlit</div>""",unsafe_allow_html=True)

if __name__=="__main__": main()
