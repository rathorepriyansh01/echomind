import streamlit as st
import time

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question



# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EchoMind – Meeting Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&family=Playfair+Display:wght@700;800&display=swap');

/* ══════════════════════════════════════════
   ROOT VARIABLES  — Teal × Amber × Midnight
   ══════════════════════════════════════════ */
:root {
    --bg:           #060b14;
    --bg2:          #0b1220;
    --surface:      #0f1929;
    --surface-2:    #162235;
    --surface-3:    #1c2d45;
    --border:       rgba(255,255,255,0.07);
    --border-glow:  rgba(0,212,180,0.25);

    /* Primary palette */
    --teal:         #00d4b4;
    --teal-dark:    #009e87;
    --teal-glow:    rgba(0,212,180,0.15);
    --amber:        #ffb347;
    --amber-dark:   #e0892a;
    --amber-glow:   rgba(255,179,71,0.15);
    --coral:        #ff6b6b;
    --violet:       #a78bfa;

    --text:         #e2eaf4;
    --text-muted:   #5a7a9a;
    --text-dim:     #2d4a6a;

    --success:      #34d399;
    --warning:      #fbbf24;
    --danger:       #f87171;

    --radius:       14px;
    --radius-sm:    8px;
}

/* ══════════════════════════════════════════
   GLOBAL RESET
   ══════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }

/* Layered starfield + mesh background */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 10% 10%, rgba(0,212,180,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 80%, rgba(255,179,71,0.05) 0%, transparent 60%),
        radial-gradient(ellipse 40% 60% at 50% 50%, rgba(167,139,250,0.03) 0%, transparent 70%),
        linear-gradient(rgba(0,212,180,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,180,0.015) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 100% 100%, 36px 36px, 36px 36px;
    pointer-events: none;
    z-index: 0;
}

/* Moving orbs */
.stApp::after {
    content: '';
    position: fixed;
    width: 500px; height: 500px;
    top: -200px; right: -100px;
    background: radial-gradient(circle, rgba(0,212,180,0.04) 0%, transparent 70%);
    border-radius: 50%;
    animation: drift 18s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes drift {
    from { transform: translate(0,0) scale(1); }
    to   { transform: translate(-80px, 120px) scale(1.2); }
}

/* ══════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 4px 0 40px rgba(0,0,0,0.4) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] label { color: var(--text-muted) !important; }

/* ══════════════════════════════════════════
   ECHOMIND ANIMATED LOGO
   ══════════════════════════════════════════ */
.echomind-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.5rem 0 1rem;
}

.logo-icon {
    position: relative;
    width: 44px; height: 44px;
    flex-shrink: 0;
}

.logo-icon svg {
    width: 44px; height: 44px;
    filter: drop-shadow(0 0 10px rgba(0,212,180,0.6));
    animation: logo-pulse 3s ease-in-out infinite;
}

@keyframes logo-pulse {
    0%, 100% { filter: drop-shadow(0 0 8px rgba(0,212,180,0.5)); }
    50%       { filter: drop-shadow(0 0 18px rgba(0,212,180,0.9)); }
}

.logo-ring {
    position: absolute;
    inset: -6px;
    border-radius: 50%;
    border: 1.5px solid rgba(0,212,180,0.3);
    animation: ring-spin 8s linear infinite;
}

.logo-ring::after {
    content: '';
    position: absolute;
    top: -2px; left: 50%;
    width: 5px; height: 5px;
    background: var(--teal);
    border-radius: 50%;
    transform: translateX(-50%);
    box-shadow: 0 0 6px var(--teal);
}

@keyframes ring-spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

.logo-text-wrap { line-height: 1.1; }

.logo-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.45rem;
    font-weight: 800;
    letter-spacing: 0.02em;
    background: linear-gradient(120deg, var(--teal) 0%, #a0f0e8 40%, var(--amber) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    background-size: 200% 200%;
    animation: shimmer 4s ease-in-out infinite;
}

@keyframes shimmer {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.logo-tagline {
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    font-family: 'Space Mono', monospace;
    margin-top: 2px;
}

/* ══════════════════════════════════════════
   HERO SECTION
   ══════════════════════════════════════════ */
.hero-wrap {
    position: relative;
    padding: 2.5rem 0 1.5rem;
    overflow: hidden;
}

.hero-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--teal);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
    animation: fadeSlideDown 0.6s ease both;
}

.hero-eyebrow::before {
    content: '';
    width: 24px; height: 1px;
    background: var(--teal);
    flex-shrink: 0;
}

.hero-title-main {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.4rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.05;
    margin-bottom: 0.5rem;
    animation: fadeSlideDown 0.7s ease 0.1s both;
}

.title-echo {
    background: linear-gradient(135deg, #ffffff 0%, var(--teal) 60%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.title-mind {
    background: linear-gradient(135deg, var(--amber) 0%, var(--coral) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    position: relative;
}

/* Underline accent on "Mind" */
.title-mind::after {
    content: '';
    position: absolute;
    bottom: -4px; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, var(--amber), transparent);
    border-radius: 2px;
}

.hero-sub {
    font-size: 0.95rem;
    color: var(--text-muted);
    line-height: 1.6;
    max-width: 560px;
    animation: fadeSlideDown 0.7s ease 0.2s both;
}

.hero-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 1.25rem;
    animation: fadeSlideDown 0.7s ease 0.3s both;
}

@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-16px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Decorative waveform illustration */
.hero-wave {
    position: absolute;
    right: 0; top: 50%;
    transform: translateY(-50%);
    opacity: 0.12;
    pointer-events: none;
}

/* ══════════════════════════════════════════
   FEATURE CARDS (landing / empty state)
   ══════════════════════════════════════════ */
.features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 2.5rem;
}

.feature-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem 1.25rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
    animation: cardRise 0.5s ease both;
    cursor: default;
}

.feature-card:nth-child(1) { animation-delay: 0.1s; }
.feature-card:nth-child(2) { animation-delay: 0.2s; }
.feature-card:nth-child(3) { animation-delay: 0.3s; }

.feature-card:hover {
    transform: translateY(-4px);
    border-color: var(--border-glow);
    box-shadow: 0 16px 40px rgba(0,0,0,0.4), 0 0 20px rgba(0,212,180,0.08);
}

@keyframes cardRise {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Glow accent line at top */
.feature-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: var(--radius) var(--radius) 0 0;
}

.feature-card.teal::before  { background: linear-gradient(90deg, var(--teal), transparent); }
.feature-card.amber::before { background: linear-gradient(90deg, var(--amber), transparent); }
.feature-card.violet::before{ background: linear-gradient(90deg, var(--violet), transparent); }

.feature-icon {
    font-size: 1.8rem;
    margin-bottom: 0.75rem;
    display: block;
}

.feature-name {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: var(--text);
    margin-bottom: 0.4rem;
}

.feature-desc {
    font-size: 0.8rem;
    color: var(--text-muted);
    line-height: 1.6;
}

/* ══════════════════════════════════════════
   BADGES
   ══════════════════════════════════════════ */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-family: 'Space Mono', monospace;
}

.badge-teal   { background: rgba(0,212,180,0.12); color: var(--teal);   border: 1px solid rgba(0,212,180,0.25); }
.badge-amber  { background: rgba(255,179,71,0.12); color: var(--amber);  border: 1px solid rgba(255,179,71,0.25); }
.badge-violet { background: rgba(167,139,250,0.12); color: var(--violet); border: 1px solid rgba(167,139,250,0.25); }
.badge-green  { background: rgba(52,211,153,0.12); color: var(--success); border: 1px solid rgba(52,211,153,0.25); }
.badge-coral  { background: rgba(255,107,107,0.12); color: var(--coral);  border: 1px solid rgba(255,107,107,0.25); }

/* ══════════════════════════════════════════
   CARDS (result panels)
   ══════════════════════════════════════════ */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s;
    animation: cardRise 0.4s ease both;
}

.card:hover {
    border-color: var(--border-glow);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 0 12px rgba(0,212,180,0.05);
}

/* Left glow bar */
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 2px; height: 100%;
}

.card.teal::before   { background: linear-gradient(180deg, var(--teal), transparent); }
.card.amber::before  { background: linear-gradient(180deg, var(--amber), transparent); }
.card.coral::before  { background: linear-gradient(180deg, var(--coral), transparent); }
.card.violet::before { background: linear-gradient(180deg, var(--violet), transparent); }
.card.success::before{ background: linear-gradient(180deg, var(--success), transparent); }

/* Corner accent */
.card::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 60px; height: 60px;
    background: radial-gradient(circle at top right, rgba(0,212,180,0.04), transparent 70%);
    pointer-events: none;
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.card-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 6px;
}

.card-content {
    font-size: 0.88rem;
    line-height: 1.8;
    color: var(--text);
}

/* Session title card special */
.title-card {
    background: linear-gradient(135deg, var(--surface) 0%, rgba(0,212,180,0.04) 100%);
    border: 1px solid rgba(0,212,180,0.2);
    border-radius: var(--radius);
    padding: 1.75rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    animation: cardRise 0.4s ease both;
}

.title-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, var(--teal), var(--amber), transparent);
}

.session-title-text {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1.3;
}

/* ══════════════════════════════════════════
   PIPELINE / STATUS BARS
   ══════════════════════════════════════════ */
.status-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.65rem 0.9rem;
    background: var(--surface-2);
    border-radius: var(--radius-sm);
    margin: 0.35rem 0;
    border: 1px solid var(--border);
    font-size: 0.78rem;
    transition: border-color 0.3s;
}

.status-bar.active  { border-color: rgba(0,212,180,0.3); background: rgba(0,212,180,0.05); }
.status-bar.done    { border-color: rgba(52,211,153,0.2); }

.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-active  { background: var(--teal);    box-shadow: 0 0 8px var(--teal);    animation: pulse 1.2s infinite; }
.dot-done    { background: var(--success); box-shadow: 0 0 6px var(--success); }
.dot-pending { background: var(--border);  border: 1px solid var(--text-dim); }

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(0.8); }
}

/* ══════════════════════════════════════════
   LOADING FRAME (full-screen overlay feel)
   ══════════════════════════════════════════ */
.loading-frame {
    background: linear-gradient(135deg, var(--surface) 0%, var(--bg2) 100%);
    border: 1px solid rgba(0,212,180,0.2);
    border-radius: var(--radius);
    padding: 2.5rem 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin: 1rem 0;
}

/* Scanning line */
.loading-frame::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--teal), var(--amber), transparent);
    animation: scan 2s ease-in-out infinite;
}

@keyframes scan {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.loading-brain {
    font-size: 3.5rem;
    display: block;
    animation: breathe 2s ease-in-out infinite;
    margin-bottom: 1rem;
}

@keyframes breathe {
    0%, 100% { transform: scale(1);    filter: drop-shadow(0 0 8px rgba(0,212,180,0.3)); }
    50%       { transform: scale(1.08); filter: drop-shadow(0 0 20px rgba(0,212,180,0.7)); }
}

.loading-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--teal), var(--amber));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.35rem;
}

.loading-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    animation: blink 1.5s ease infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* Waveform bars animation */
.waveform {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 4px;
    height: 36px;
    margin: 1rem auto 0;
}

.wave-bar {
    width: 4px;
    border-radius: 2px;
    background: linear-gradient(180deg, var(--teal), var(--teal-dark));
    animation: wavebar 1.2s ease-in-out infinite;
}

.wave-bar:nth-child(1)  { animation-delay: 0s;    }
.wave-bar:nth-child(2)  { animation-delay: 0.1s;  }
.wave-bar:nth-child(3)  { animation-delay: 0.2s;  }
.wave-bar:nth-child(4)  { animation-delay: 0.3s;  }
.wave-bar:nth-child(5)  { animation-delay: 0.4s;  }
.wave-bar:nth-child(6)  { animation-delay: 0.3s;  }
.wave-bar:nth-child(7)  { animation-delay: 0.2s;  }
.wave-bar:nth-child(8)  { animation-delay: 0.1s;  }
.wave-bar:nth-child(9)  { animation-delay: 0s;    }
.wave-bar:nth-child(10) { animation-delay: 0.15s; }
.wave-bar:nth-child(11) { animation-delay: 0.25s; }
.wave-bar:nth-child(12) { animation-delay: 0.35s; }

@keyframes wavebar {
    0%, 100% { height: 6px;  opacity: 0.4; }
    50%       { height: 32px; opacity: 1;   }
}

/* ══════════════════════════════════════════
   CHAT
   ══════════════════════════════════════════ */
.chat-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    margin-bottom: 1rem;
}

.chat-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1.25rem;
    background: var(--surface-2);
    border-bottom: 1px solid var(--border);
}

.chat-topbar-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 6px;
}

.live-dot {
    width: 7px; height: 7px;
    background: var(--teal);
    border-radius: 50%;
    box-shadow: 0 0 6px var(--teal);
    animation: pulse 1.5s infinite;
}

.chat-messages {
    padding: 1.25rem;
    max-height: 400px;
    overflow-y: auto;
}

.chat-msg {
    margin-bottom: 1.1rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    animation: msgAppear 0.3s ease both;
}

@keyframes msgAppear {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

.chat-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.chat-bubble {
    display: inline-block;
    padding: 0.65rem 1rem;
    border-radius: 12px;
    font-size: 0.85rem;
    line-height: 1.65;
    max-width: 88%;
}

.user-label  { color: var(--amber); }
.bot-label   { color: var(--teal); }

.user-bubble {
    background: rgba(255,179,71,0.1);
    border: 1px solid rgba(255,179,71,0.2);
    align-self: flex-end;
    border-bottom-right-radius: 4px;
}

.bot-bubble {
    background: rgba(0,212,180,0.07);
    border: 1px solid rgba(0,212,180,0.15);
    align-self: flex-start;
    border-bottom-left-radius: 4px;
}

/* ══════════════════════════════════════════
   TRANSCRIPT BOX
   ══════════════════════════════════════════ */
.transcript-box {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 1.25rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.85;
    max-height: 300px;
    overflow-y: auto;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
}

/* ══════════════════════════════════════════
   INPUTS & BUTTONS
   ══════════════════════════════════════════ */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.88rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}

.stTextInput > div > div > input:focus {
    border-color: rgba(0,212,180,0.5) !important;
    box-shadow: 0 0 0 3px rgba(0,212,180,0.08) !important;
}

/* Primary CTA button */
.stButton > button {
    background: linear-gradient(135deg, var(--teal-dark), var(--teal)) !important;
    color: var(--bg) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.22s !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton > button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, transparent 0%, rgba(255,255,255,0.15) 50%, transparent 100%);
    transform: translateX(-100%);
    transition: transform 0.4s;
}

.stButton > button:hover::before { transform: translateX(100%); }

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(0,212,180,0.35) !important;
}

.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
}

/* ══════════════════════════════════════════
   DIVIDERS & MISC
   ══════════════════════════════════════════ */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.75rem 0 !important;
}

.stProgress > div > div > div    { background: linear-gradient(90deg, var(--teal), var(--amber)) !important; }
.stSpinner > div                  { border-top-color: var(--teal) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
label { color: var(--text-muted) !important; font-size: 0.82rem !important; }

/* ── Section divider with label ── */
.section-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2rem 0 1.25rem;
}

.section-divider-line {
    flex: 1;
    height: 1px;
    background: var(--border);
}

.section-divider-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-dim);
}

/* scrollbar */
::-webkit-scrollbar       { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,180,0.4); }

/* stAlert override */
.stAlert { border-radius: var(--radius-sm) !important; }

/* Expander override */
details summary {
    color: var(--text-muted) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result":         None,
    "chat_history":   [],
    "processing":     False,
    "pipeline_done":  False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_status(steps: dict, key: str) -> tuple:
    s = steps.get(key, "pending")
    if s == "active":  return "dot-active", "active"
    if s == "done":    return "dot-done",   "done"
    return "dot-pending", ""

def render_step_bar(label: str, key: str, icon: str):
    dot_css, bar_css = step_status(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="status-bar {bar_css}">
        <div class="status-dot {dot_css}"></div>
        <span>{icon}&nbsp; {label}</span>
    </div>""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
BRAIN_SVG = """<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="20" cy="20" r="18" stroke="#00d4b4" stroke-width="1.2" stroke-dasharray="3 3"/>
  <circle cx="20" cy="20" r="10" fill="none" stroke="#00d4b4" stroke-width="1.5"/>
  <circle cx="20" cy="20" r="4"  fill="#00d4b4"/>
  <line x1="20" y1="10" x2="20" y2="2"  stroke="#ffb347" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="30" y1="20" x2="38" y2="20" stroke="#ffb347" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="20" y1="30" x2="20" y2="38" stroke="#00d4b4" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="10" y1="20" x2="2"  y2="20" stroke="#00d4b4" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="20" cy="2"  r="2" fill="#ffb347"/>
  <circle cx="38" cy="20" r="2" fill="#ffb347"/>
  <circle cx="20" cy="38" r="2" fill="#00d4b4"/>
  <circle cx="2"  cy="20" r="2" fill="#00d4b4"/>
</svg>"""

with st.sidebar:
    # Logo
    st.markdown(f"""
    <div class="echomind-logo">
        <div class="logo-icon">
            {BRAIN_SVG}
            <div class="logo-ring"></div>
        </div>
        <div class="logo-text-wrap">
            <div class="logo-title">EchoMind</div>
            <div class="logo-tagline">Meeting Intelligence</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<span class="badge badge-teal">⚡ Input</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    source = st.text_input(
        "YouTube URL or File Path",
        placeholder="https://youtube.com/watch?v=... or /path/to/meeting.mp4"
    )

    language = st.selectbox("Language", ["english", "hinglish"], index=0)
    st.markdown("<br>", unsafe_allow_html=True)

    run_btn = st.button("🧠  Analyse with EchoMind", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<span class="badge badge-green">✅ Pipeline Status</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        for step, icon, label in [
            ("audio",      "🔊", "Audio Processing"),
            ("transcript", "📝", "Transcription"),
            ("title",      "🏷️", "Title Generation"),
            ("summary",    "📋", "Summarisation"),
            ("extract",    "🔍", "Extraction"),
            ("rag",        "🧠", "RAG Engine"),
        ]:
            render_step_bar(label, step, icon)

    # Sidebar footer
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.68rem;color:var(--text-dim);text-align:center;font-family:'Space Mono',monospace;line-height:1.7">
        Powered by EchoMind AI<br>
        <span style="color:rgba(0,212,180,0.4)">v2.0  ·  © 2025</span>
    </div>""", unsafe_allow_html=True)

# ─── Main Area ──────────────────────────────────────────────────────────────────

# Decorative waveform SVG
WAVE_SVG = """<svg width="320" height="90" viewBox="0 0 320 90" fill="none" xmlns="http://www.w3.org/2000/svg">
  <polyline points="0,45 20,45 30,10 40,80 50,25 60,65 70,30 80,55 90,40 100,50 110,20 120,70 130,35 140,60 150,30 160,50 170,20 180,75 190,30 200,60 210,35 220,55 230,42 240,48 250,45 270,45 320,45"
    stroke="url(#wg)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  <defs>
    <linearGradient id="wg" x1="0" y1="0" x2="320" y2="0">
      <stop offset="0%"   stop-color="#00d4b4" stop-opacity="0"/>
      <stop offset="40%"  stop-color="#00d4b4" stop-opacity="1"/>
      <stop offset="70%"  stop-color="#ffb347" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#ffb347" stop-opacity="0"/>
    </linearGradient>
  </defs>
</svg>"""

st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-eyebrow">AI-Powered Meeting Analysis</div>
    <div class="hero-title-main">
        <span class="title-echo">Echo</span><span class="title-mind">Mind</span>
    </div>
    <div class="hero-sub">
        Transform meetings into intelligence — transcribe, summarise, extract insights, and chat with your recordings in seconds.
    </div>
    <div class="hero-badges">
        <span class="badge badge-teal">🎙️ Transcription</span>
        <span class="badge badge-amber">✨ Summarisation</span>
        <span class="badge badge-violet">🤖 RAG Chat</span>
        <span class="badge badge-coral">🔍 Insight Extraction</span>
    </div>
    <div class="hero-wave">{WAVE_SVG}</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr>', unsafe_allow_html=True)

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("⚠️ Please enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result        = None
        st.session_state.chat_history  = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            # ── Loading Frame ──────────────────────────────────────────────
            progress_placeholder.markdown("""
            <div class="loading-frame">
                <span class="loading-brain">🧠</span>
                <div class="loading-title">EchoMind is Processing</div>
                <div class="loading-sub">Analysing your meeting — this may take a moment…</div>
                <div class="waveform">
                    <div class="wave-bar"></div><div class="wave-bar"></div>
                    <div class="wave-bar"></div><div class="wave-bar"></div>
                    <div class="wave-bar"></div><div class="wave-bar"></div>
                    <div class="wave-bar"></div><div class="wave-bar"></div>
                    <div class="wave-bar"></div><div class="wave-bar"></div>
                    <div class="wave-bar"></div><div class="wave-bar"></div>
                </div>
            </div>""", unsafe_allow_html=True)

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items = extract_action_items(transcript)
            decisions    = extract_key_decisions(transcript)
            questions    = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title":          title,
                "transcript":     transcript,
                "summary":        summary,
                "action_items":   action_items,
                "key_decisions":  decisions,
                "open_questions": questions,
                "rag_chain":      rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("✅ EchoMind analysis complete!")
            time.sleep(0.8)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio","transcript","title","summary","extract","rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"❌ Error: {e}")

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # ── Session Title Banner ──────────────────────────────────────────────
    st.markdown(f"""
    <div class="title-card">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.5rem">
            <span class="badge badge-teal">📌 Session</span>
        </div>
        <div class="session-title-text">{r['title']}</div>
    </div>""", unsafe_allow_html=True)

    # ── Summary + Transcript ──────────────────────────────────────────────
    st.markdown("""<div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">Overview</div>
        <div class="section-divider-line"></div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown(f"""
        <div class="card teal">
            <div class="card-header">
                <div class="card-title">📋 &nbsp;Summary</div>
                <span class="badge badge-teal">AI Generated</span>
            </div>
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        with st.expander("📝  Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>',
                        unsafe_allow_html=True)

    # ── Insights Row ─────────────────────────────────────────────────────
    st.markdown("""<div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">Extracted Insights</div>
        <div class="section-divider-line"></div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="card success">
            <div class="card-header">
                <div class="card-title">✅ &nbsp;Action Items</div>
            </div>
            <div class="card-content">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card amber">
            <div class="card-header">
                <div class="card-title">🔑 &nbsp;Key Decisions</div>
            </div>
            <div class="card-content">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card coral">
            <div class="card-header">
                <div class="card-title">❓ &nbsp;Open Questions</div>
            </div>
            <div class="card-content">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    # ── RAG Chat ──────────────────────────────────────────────────────────
    st.markdown("""<div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">Chat with your Meeting</div>
        <div class="section-divider-line"></div>
    </div>""", unsafe_allow_html=True)

    # Chat window
    if st.session_state.chat_history:
        chat_html = '<div class="chat-wrap"><div class="chat-topbar">'
        chat_html += '<div class="chat-topbar-title"><div class="live-dot"></div> EchoMind Chat</div>'
        chat_html += f'<span class="badge badge-teal">{len(st.session_state.chat_history)//2} exchanges</span>'
        chat_html += '</div><div class="chat-messages">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label user-label">You</span>
                    <div class="chat-bubble user-bubble">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label bot-label">🧠 EchoMind</span>
                    <div class="chat-bubble bot-bubble">{msg['content']}</div>
                </div>"""
        chat_html += '</div></div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card violet" style="text-align:center;padding:2.5rem">
            <div style="font-size:2.5rem;margin-bottom:0.75rem">🧠</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;
                        color:var(--text);margin-bottom:0.4rem">Ready to Answer</div>
            <div style="color:var(--text-muted);font-size:0.82rem;line-height:1.7;max-width:340px;margin:0 auto">
                Ask EchoMind anything about your meeting — decisions, action items, names, or details.
            </div>
        </div>""", unsafe_allow_html=True)

    # Chat input row
    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input(
            "Ask EchoMind",
            placeholder="What were the main decisions made in this meeting?",
            label_visibility="collapsed"
        )
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("🧠 EchoMind is thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # ── Empty / Landing State ──────────────────────────────────────────────
    st.markdown("""
    <div class="features-grid">
        <div class="feature-card teal">
            <span class="feature-icon">🎙️</span>
            <div class="feature-name">Smart Transcription</div>
            <div class="feature-desc">High-accuracy transcription for English and Hinglish content from YouTube or local files.</div>
        </div>
        <div class="feature-card amber">
            <span class="feature-icon">✨</span>
            <div class="feature-name">AI Summarisation</div>
            <div class="feature-desc">Concise summaries with auto-generated titles so you never miss the big picture.</div>
        </div>
        <div class="feature-card violet">
            <span class="feature-icon">🔍</span>
            <div class="feature-name">Insight Extraction</div>
            <div class="feature-desc">Automatically pull out action items, key decisions, and open questions from any meeting.</div>
        </div>
    </div>

    <div style="text-align:center;padding:3rem 2rem 1rem">
        <div style="font-family:'Space Mono',monospace;font-size:0.7rem;
                    letter-spacing:0.2em;color:var(--text-dim);text-transform:uppercase">
            ← Paste a URL or file path in the sidebar to get started
        </div>
    </div>
    """, unsafe_allow_html=True)
