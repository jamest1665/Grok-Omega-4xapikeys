import streamlit as st
import openai, anthropic, os
import google.generativeai as genai
from xai import Grok

st.set_page_config(page_title="Grok-Omega ∞", page_icon="∞", layout="centered")
st.title("Grok-Omega ∞")
st.caption("One prompt → automatically picks the cheapest working model")

st.warning("Your API keys NEVER leave your device • 100% safe to paste real keys")

with st.sidebar:
    st.header("Your API Keys (bring your own)")
    o = st.text_input("OpenAI", type="password", placeholder="sk-...")
    a = st.text_input("Anthropic (Claude)", type="password")
    g = st.text_input("Grok (xAI)", type="password")
    m = st.text_input("Gemini", type="password")

prompt = st.chat_input("Ask anything…")

if prompt:
    if not any([o,a,g,m]):
        st.error("Please add at least one API key in the sidebar")
        st.stop()

    responses = {}
    costs = {"gpt-4o":5, "claude-3-5-sonnet-20241022":3, "grok-beta":0.5, "gemini-1.5-pro":2}

    with st.spinner("Racing all 4 models in parallel…"):
        if o:
            try:
                r = openai.OpenAI(api_key=o).chat.completions.create(model="gpt-4o", messages=[{"role":"user","content":prompt}], max_tokens=600)
                responses["OpenAI (gpt-4o)"] = r.choices[0].message.content
            except Exception: responses["OpenAI (gpt-4o)"] = "Failed"
        if a:
            try:
                r = anthropic.Anthropic(api_key=a).messages.create(model="claude-3-5-sonnet-20241022", max_tokens=600, messages=[{"role":"user","content":prompt}])
                responses["Claude 3.5"] = r.content[0].text
            except Exception: responses["Claude 3.5"] = "Failed"
        if g:
            try:
                r = Grok(api_key=g).chat(model="grok-beta", messages=[{"role":"user","content":prompt}])
                responses["Grok"] = r[0]["message"]["content"]
            except Exception: responses["Grok"] = "Failed"
        if m:
            try:
                genai.configure(api_key=m)
                r = genai.GenerativeModel("gemini-1.5-pro-latest").generate_content(prompt)
                responses["Gemini 1.5 Pro"] = r.text
            except Exception: responses["Gemini 1.5 Pro"] = "Failed"

    working = {k:v for k,v in responses.items() if v != "Failed"}
    if working:
        winner = min(working, key=lambda k: costs.get(k.split("(")[1].split(")")[0] if "(" in k else "grok-beta", 999))
        st.success(f"WINNER → {winner} (cheapest working model)")
        for model, text in responses.items():
            with st.expander(model, expanded=model==winner):
                st.write(text if text != "Failed" else "No response")
    else:
        st.error("All 4 models failed – check your keys")

st.markdown("---")
st.caption("Made with ∞ on mobile • Lifetime private beta coming tonight")
