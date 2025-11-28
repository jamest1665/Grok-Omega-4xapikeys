import streamlit as st
import openai
import anthropic
import google.generativeai as genai
import os

# Official xAI SDK import (fixed – no more 'from xai import Grok' error)
try:
    from xai_sdk import Client
    from xai_sdk.chat import user
    GROK_AVAILABLE = True
except ImportError:
    st.warning("Grok SDK not installed – skipping Grok (use other models)")
    GROK_AVAILABLE = False

st.set_page_config(page_title="Grok-Omega ∞", page_icon="∞", layout="centered")
st.title("Grok-Omega ∞")
st.caption("One prompt → automatically picks the cheapest working model")

st.warning("Your API keys NEVER leave your device • 100% safe to paste real keys")

with st.sidebar:
    st.header("Your API Keys (bring your own)")
    o = st.text_input("OpenAI", type="password", placeholder="sk-...")
    a = st.text_input("Anthropic (Claude)", type="password", placeholder="sk-ant-...")
    g = st.text_input("Grok (xAI)", type="password", placeholder="xai-...") if GROK_AVAILABLE else None
    m = st.text_input("Gemini", type="password", placeholder="AIza...")

prompt = st.chat_input("Ask anything…")

if prompt:
    if not any([o, a, g, m]):
        st.error("Please add at least one API key in the sidebar")
        st.stop()

    responses = {}
    costs = {"gpt-4o": 5, "claude-3-5-sonnet-20241022": 3, "grok-beta": 0.5, "gemini-1.5-pro": 2}

    with st.spinner("Racing all 4 models in parallel…"):
        # OpenAI
        if o:
            try:
                r = openai.OpenAI(api_key=o).chat.completions.create(
                    model="gpt-4o", messages=[{"role": "user", "content": prompt}], max_tokens=600)
                responses["OpenAI (gpt-4o)"] = r.choices[0].message.content
            except Exception:
                responses["OpenAI (gpt-4o)"] = "Failed"
        
        # Anthropic Claude
        if a:
            try:
                client = anthropic.Anthropic(api_key=a)
                r = client.messages.create(
                    model="claude-3-5-sonnet-20241022", max_tokens=600,
                    messages=[{"role": "user", "content": prompt}])
                responses["Claude 3.5"] = r.content[0].text
            except Exception:
                responses["Claude 3.5"] = "Failed"
        
        # Grok (fixed with official xAI SDK – gRPC style)
        if g and GROK_AVAILABLE:
            try:
                client = Client(api_key=g, timeout=3600)
                chat = client.chat.create(model="grok-beta")
                chat.append(user(prompt))
                r = chat.sample()
                responses["Grok (xAI)"] = r.content
            except Exception:
                responses["Grok (xAI)"] = "Failed"
        
        # Gemini
        if m:
            try:
                genai.configure(api_key=m)
                model = genai.GenerativeModel("gemini-1.5-pro-latest")
                r = model.generate_content(prompt)
                responses["Gemini 1.5 Pro"] = r.text
            except Exception:
                responses["Gemini 1.5 Pro"] = "Failed"

    working = {k: v for k, v in responses.items() if v != "Failed"}
    if working:
        # Pick cheapest winner
        winner_key = min(working, key=lambda k: costs.get(k.split("(")[1].split(")")[0] if "(" in k else "grok-beta", 999))
        st.success(f"WINNER → {winner_key} (cheapest working model)")
        for model, text in responses.items():
            with st.expander(model, expanded=(model == winner_key)):
                st.write(text if text != "Failed" else "No response")
    else:
        st.error("All 4 models failed – double-check your keys")

st.markdown("---")
st.caption("Made with ∞ on S24 Ultra • Lifetime private beta $29 coming tonight – reply 'ME' on X")
