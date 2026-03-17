import streamlit as st
import requests
import time
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE")
ASK_URL = f"{API_BASE}/ask"
STREAM_URL = f"{API_BASE}/stream"
METRICS_URL = f"{API_BASE}/metrics"
HEALTH_URL = f"{API_BASE}/health"

st.set_page_config(
    page_title="Redis RAG AI",
    page_icon="🤖",
    layout="wide", # Uses full screen width
    initial_sidebar_state="expanded"
)

# -----------------------------
# Enhanced Styling for Screen Size
# -----------------------------
st.markdown("""
<style>
    /* 1. Reduce the main container bottom padding */
    .block-container {
        padding-bottom: 1rem !important;
    }

    /* 2. Target the specific input container to sit lower */
    [data-testid="stChatFloatingInputContainer"] {
        bottom: 10px;
    }

    /* 3. Reduce the gap between the chat container and input */
    .stVerticalBlock {
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "latency_history" not in st.session_state:
    st.session_state.latency_history = []
if "button_disabled" not in st.session_state:
    st.session_state.button_disabled = False
if "cooldown_end" not in st.session_state:
    st.session_state.cooldown_end = 0

# -----------------------------
# Sidebar & Metrics
# -----------------------------
with st.sidebar:
    st.title("🤖 Redis RAG AI")
    
    # Status Row
    try:
        health = requests.get(HEALTH_URL, timeout=2).json()
        h_col1, h_col2 = st.columns(2)
        if health["status"] == "ok": h_col1.success("API")
        if health["redis"] == "connected": h_col2.success("Redis")
    except:
        st.error("Backend Offline")

    st.divider()
    
    use_stream = st.toggle("Enable Streaming", value=False)
    
    if metrics_data := requests.get(METRICS_URL, timeout=2).json() if True else None:
        st.subheader("Cache Performance")
        m_col1, m_col2 = st.columns(2)
        hits = int(metrics_data.get("cache_hits", 0))
        misses = int(metrics_data.get("cache_misses", 0))
        total = hits + misses
        hit_rate = (hits / total * 100) if total else 0
        
        m_col1.metric("Hit Rate", f"{hit_rate:.1f}%")
        m_col2.metric("Limited", metrics_data.get("rate_limited_requests", 0))

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.latency_history = []
        st.rerun()

# -----------------------------
# Main Chat & Analytics Layout
# -----------------------------
chat_col, metrics_col = st.columns([4, 1.2], gap="medium")

with chat_col:
    st.subheader("⚡ Redis-Optimized RAG Assistant")
    
    chat_container = st.container(height=650)
    
    with chat_container:
        if not st.session_state.messages:
            st.info("System Ready. Ask a question to begin semantic retrieval.")
            
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if "source" in msg:
                    label = "🟢 Redis" if msg["source"] == "cache" else "☁️ LLM"
                    if msg["source"] == "system": label = "🛡️ System"
                    st.caption(f"{label} | Latency: {msg.get('latency', 0):.2f}s")

    # --- Cooldown Logic ---
    current_time = time.time()
    if "cooldown_end" in st.session_state and current_time < st.session_state.cooldown_end:
        st.session_state.button_disabled = True
        remaining = int(st.session_state.cooldown_end - current_time)
        st.warning(f"⏳ Rate limit cooldown: {remaining}s remaining")
        
        # This is the "magic" bit: 
        # It waits 1 second and then reruns the script to update the timer/input state
        time.sleep(1)
        st.rerun() 
    else:
        if st.session_state.button_disabled:
            st.session_state.button_disabled = False
            st.success("✅ Cooldown over! You can ask questions again.")
            # Optional: st.rerun() here to immediately clear the success message 
            # or just let the next interaction do it.

    # --- Chat Input ---
    prompt = st.chat_input("Ask about Redis...", disabled=st.session_state.button_disabled)

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                start = time.time()
                answer = ""
                source = "llm"

                try:
                    if use_stream:
                        placeholder = st.empty()
                        response = requests.get(STREAM_URL, params={"question": prompt}, stream=True, timeout=10)
                        source = "llm"
                        first_chunk = True

                        for chunk in response.iter_content(chunk_size=None):

                            if chunk:
                                token = chunk.decode("utf-8")

                                if first_chunk and token.startswith("__SOURCE__:"):
                                    source = token.replace("__SOURCE__:", "").strip()
                                    first_chunk = False
                                    continue

                                first_chunk = False
                                answer += token
                                placeholder.markdown(answer)
                        latency = time.time() - start
                    
                    else:
                        response = requests.get(ASK_URL, params={"question": prompt})
                        latency = time.time() - start
                        data = response.json()

                        if "error" in data:
                            retry_after = data.get("retry_after", 60)
                            answer = f"🚫 **{data['error']}**"
                            source = "system"
                            st.session_state.cooldown_end = time.time() + retry_after
                            st.error(f"{answer} (Try again in {retry_after}s)")
                        else:
                            source = data.get("source", "llm")
                            result = data.get("data", {})
                            answer = result.get("answer", "No answer found.")
                            st.markdown(answer)
                            
                            if "context_used" in result:
                                with st.expander("🔍 Retrieved Context"):
                                    st.write(result["context_used"])

                except Exception as e:
                    answer = f"⚠️ Connection Error: {str(e)}"
                    source = "system"
                    latency = 0.0

        # Update history
        st.session_state.latency_history.append(latency)
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer, 
            "source": source,
            "latency": latency
        })
        st.rerun()

    # Disclaimer Footer
    st.markdown(
        "<div style='text-align: center; color: grey; font-size: 0.8rem; margin-top: 10px;'>"
        "Redis RAG AI can make mistakes. Check important info."
        "</div>", 
        unsafe_allow_html=True
    )

# -----------------------------
# Analytics Panel
# -----------------------------
with metrics_col:
    st.subheader("Analytics")
    
    if st.session_state.latency_history:
        st.caption("Latency Trend (sec)")
        st.line_chart(st.session_state.latency_history, height=200)
    
    st.divider()
    
    if metrics_data:
        st.caption("Cache Hits vs Misses")
        chart_df = pd.DataFrame({
            "Type": ["Hits", "Misses"],
            "Count": [int(metrics_data.get("cache_hits", 0)), int(metrics_data.get("cache_misses", 0))]
        }).set_index("Type")
        st.bar_chart(chart_df, height=250)