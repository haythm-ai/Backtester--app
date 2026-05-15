#!/usr/bin/env python3
"""
================================================================================
CRYPTO BACKTESTER PRO - STREAMLIT WEB APP
Mobile-Optimized UI for Android/iPhone
================================================================================

Run with: streamlit run crypto_backtester_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page config - mobile optimized
st.set_page_config(
    page_title="Crypto Backtester Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile
st.markdown("""
<style>
    .main { padding: 0.5rem; }
    .stButton>button { width: 100%; height: 3rem; font-size: 1.1rem; }
    .stSelectbox>div>div { font-size: 1rem; }
    .metric-card { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem; 
        border-radius: 10px; 
        color: white;
        margin: 0.3rem 0;
    }
    .positive { color: #00c853; font-weight: bold; }
    .negative { color: #ff1744; font-weight: bold; }
    @media (max-width: 768px) {
        .main { padding: 0.2rem; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA & INDICATORS
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
    def enter(self, ts, p, dir, sl_atr=2, tp_atr=3, use_trail=False, trail_atr=2):
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
        if dir == 'long':
            self.sl = ep - atr * sl_atr
            self.tp = ep + atr * tp_atr
            self.trail = ep - atr * trail_atr if use_trail else None
            self.hi = ep
        else:
            self.sl = ep + atr * sl_atr
            self.tp = ep - atr * tp_atr
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
            if lo <= self.sl: self.exit(ts, self.sl, 'stop_loss'); return True
            if hi >= self.tp: self.exit(ts, self.tp, 'take_profit'); return True
            if self.trail:
                if cl > self.hi: self.hi = cl; self.trail = max(self.trail, cl - (self.hi-self.entry_p)*0.5)
                if lo <= self.trail: self.exit(ts, self.trail, 'trailing_stop'); return True
        else:
            if hi >= self.sl: self.exit(ts, self.sl, 'stop_loss'); return True
            if lo <= self.tp: self.exit(ts, self.tp, 'take_profit'); return True
            if self.trail:
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
    def run(self, tf='1h', entry=None, exit=None, sl_atr=2, tp_atr=3, use_trail=False, trail_atr=2, start=None, end=None):
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
                self.enter(ts, row['close'], 'long', sl_atr, tp_atr, use_trail, trail_atr)
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
# DATA GENERATION (No caching - works on Streamlit Cloud)
# ============================================================

def generate_data():
    """Generate synthetic crypto data"""
    np.random.seed(42)
    end = datetime(2026, 5, 15, 22, 0)

    dates_1h = pd.date_range(end-timedelta(days=90), periods=90*24, freq='1H')
    ret = np.random.normal(0.0001, 0.008, len(dates_1h))
    var = 0.008**2
    for i in range(1, len(ret)):
        var = 0.000001 + 0.85*var + 0.1*ret[i-1]**2
        ret[i] = np.random.normal(0.0001, np.sqrt(var))
    cl = 65000 * np.exp(np.cumsum(ret))
    hl = cl * np.abs(np.random.normal(0, 0.004, len(cl)))
    hi = cl + hl * np.random.uniform(0.3, 1.0, len(cl))
    lo = cl - hl * np.random.uniform(0.3, 1.0, len(cl))
    op = np.roll(cl, 1); op[0] = 65000; op = op * (1 + np.random.normal(0, 0.001, len(cl)))
    vol = 1000 * (1 + 5*np.abs(ret)/np.std(ret)) * np.random.lognormal(0, 0.5, len(cl))
    df_1h = pd.DataFrame({'open': op, 'high': hi, 'low': lo, 'close': cl, 'volume': vol}, index=dates_1h)

    df_4h = df_1h.resample('4H').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna()
    df_1d = df_1h.resample('1D').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna()

    return df_1h, df_4h, df_1d

# ============================================================
# UI COMPONENTS
# ============================================================

def render_header():
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 2rem; margin: 0;">📈 Crypto Backtester Pro</h1>
        <p style="color: #666; margin: 0.5rem 0;">Multi-Timeframe Strategy Backtesting</p>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, suffix="", is_pct=False):
    color = "positive" if (is_pct and float(value) > 0) or (not is_pct and float(value) > 0) else "negative" if (is_pct and float(value) < 0) else ""
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.8rem; opacity: 0.9;">{label}</div>
        <div style="font-size: 1.5rem; font-weight: bold;" class="{color}">{value}{suffix}</div>
    </div>
    """, unsafe_allow_html=True)

def build_condition_ui(prefix, key_prefix):
    """Build a single condition UI"""
    cols = st.columns([2, 2, 1, 2, 2])

    with cols[0]:
        tf = st.selectbox(f"TF", ['1h', '4h', '1d'], key=f"{key_prefix}_tf")
    with cols[1]:
        indicators = ['close', 'open', 'high', 'low', 'volume', 'rsi_14', 'rsi_7', 'macd_hist', 
                      'ema_9', 'ema_21', 'ema_50', 'sma_20', 'sma_50', 'sma_200',
                      'bb_upper', 'bb_mid', 'bb_lower', 'atr_14', 'atr_7', 'adx',
                      'vwap', 'supertrend_dir', 'stoch_k', 'stoch_d', 'williams_r']
        ind = st.selectbox(f"Indicator", indicators, key=f"{key_prefix}_ind")
    with cols[2]:
        ops = ['>', '<', '>=', '<=', '==', '!=', 'crosses_above', 'crosses_below']
        op = st.selectbox(f"Op", ops, key=f"{key_prefix}_op")
    with cols[3]:
        value_type = st.selectbox(f"Type", ['Number', 'Indicator'], key=f"{key_prefix}_vtype")
    with cols[4]:
        if value_type == 'Number':
            val = st.number_input(f"Value", value=50.0, key=f"{key_prefix}_val")
            return {'timeframe': tf, 'indicator': ind, 'operator': op, 'value': val}
        else:
            val_tf = st.selectbox(f"V-TF", ['1h', '4h', '1d'], key=f"{key_prefix}_vtf")
            val_ind = st.selectbox(f"V-Ind", indicators, key=f"{key_prefix}_vind")
            return {'timeframe': tf, 'indicator': ind, 'operator': op, 
                    'value': {'timeframe': val_tf, 'indicator': val_ind}}

# ============================================================
# MAIN APP
# ============================================================

def main():
    render_header()

    # Load data
    df_1h, df_4h, df_1d = generate_data()

    mtf = MultiTimeframeManager()
    mtf.add_timeframe('1h', df_1h)
    mtf.add_timeframe('4h', df_4h)
    mtf.add_timeframe('1d', df_1d)

    # Sidebar / Main area for mobile
    with st.expander("⚙️ Strategy Settings", expanded=True):
        st.subheader("Entry Conditions")
        n_entry = st.number_input("Number of entry conditions", 1, 5, 2, key="n_entry")
        entry_conditions = []
        for i in range(n_entry):
            with st.container():
                st.markdown(f"**Condition {i+1}**")
                entry_conditions.append(build_condition_ui("Entry", f"ent_{i}"))

        st.subheader("Exit Conditions")
        n_exit = st.number_input("Number of exit conditions", 1, 5, 2, key="n_exit")
        exit_conditions = []
        for i in range(n_exit):
            with st.container():
                st.markdown(f"**Condition {i+1}**")
                exit_conditions.append(build_condition_ui("Exit", f"ext_{i}"))

        st.subheader("Risk Management")
        col1, col2 = st.columns(2)
        with col1:
            sl_atr = st.slider("Stop Loss (ATR x)", 0.5, 5.0, 2.0, 0.5)
            tp_atr = st.slider("Take Profit (ATR x)", 1.0, 10.0, 3.0, 0.5)
        with col2:
            use_trail = st.toggle("Trailing Stop", value=False)
            trail_atr = st.slider("Trailing (ATR x)", 0.5, 5.0, 2.0, 0.5) if use_trail else 2.0

        st.subheader("Backtest Period")
        col3, col4 = st.columns(2)
        with col3:
            start_date = st.date_input("Start", datetime(2026, 3, 1))
        with col4:
            end_date = st.date_input("End", datetime(2026, 5, 15))

    # Build rules
    entry_rule = {'logic': 'AND', 'conditions': entry_conditions}
    exit_rule = {'logic': 'OR', 'conditions': exit_conditions}

    # Run button
    if st.button("🚀 RUN BACKTEST", type="primary", use_container_width=True):
        with st.spinner("Running backtest..."):
            bt = BacktestEngine(mtf, capital=10000, comm=0.001, slip=0.0005, spread=0.0002)
            results = bt.run(
                tf='1h', entry=entry_rule, exit=exit_rule,
                sl_atr=sl_atr, tp_atr=tp_atr, use_trail=use_trail, trail_atr=trail_atr,
                start=start_date, end=end_date
            )

        if not results:
            st.error("No results generated. Check your conditions.")
            return

        # Results display
        st.markdown("---")
        st.subheader("📊 Results")

        # Metrics grid
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_metric_card("Return", f"{results['total_return_pct']:+.2f}", "%", True)
        with m2:
            render_metric_card("Trades", str(results['total_trades']), "")
        with m3:
            render_metric_card("Win Rate", f"{results['win_rate']:.1f}", "%")
        with m4:
            render_metric_card("Sharpe", f"{results['sharpe_ratio']:.2f}", "")

        m5, m6, m7, m8 = st.columns(4)
        with m5:
            render_metric_card("Max DD", f"{results['max_drawdown_pct']:.2f}", "%")
        with m6:
            render_metric_card("Profit Factor", f"{results['profit_factor']:.2f}", "")
        with m7:
            render_metric_card("Expectancy", f"${results['expectancy']:.2f}", "")
        with m8:
            render_metric_card("Final Capital", f"${results['final_capital']:,.0f}", "")

        # Charts
        st.markdown("---")

        eq_df = results['equity_curve']
        trades_df = results['trades']

        # Equity curve
        st.subheader("Equity Curve")
        chart_data = pd.DataFrame({
            'Equity': eq_df.set_index('timestamp')['equity'],
            'Peak': eq_df.set_index('timestamp')['equity'].cummax()
        })
        st.line_chart(chart_data, use_container_width=True)

        # Drawdown
        st.subheader("Drawdown")
        peak = eq_df['equity'].cummax()
        dd = (peak - eq_df['equity']) / peak * 100
        st.area_chart(pd.DataFrame({'Drawdown %': dd.values}, index=eq_df['timestamp']), 
                      use_container_width=True, color=['#ff1744'])

        # Trades table
        if not trades_df.empty:
            st.subheader("Trade Log")
            display_df = trades_df[['entry_time', 'exit_time', 'pnl', 'pnl_pct', 'reason', 'duration_hours']].copy()
            display_df.columns = ['Entry', 'Exit', 'P&L ($)', 'P&L (%)', 'Reason', 'Hours']

            def highlight_pnl(val):
                if isinstance(val, (int, float)):
                    return 'color: #00c853' if val > 0 else 'color: #ff1744'
                return ''

            st.dataframe(display_df.style.applymap(highlight_pnl, subset=['P&L ($)', 'P&L (%)']),
                        use_container_width=True, height=300)

            csv = trades_df.to_csv(index=False)
            st.download_button("📥 Download Trades CSV", csv, "trades.csv", "text/csv")

    # Footer
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #999; font-size: 0.8rem;'>Crypto Backtester Pro v1.0 | Mobile Optimized</div>", 
                unsafe_allow_html=True)

if __name__ == "__main__":
    main()
