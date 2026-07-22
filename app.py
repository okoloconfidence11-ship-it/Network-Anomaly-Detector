import streamlit as st
import pandas as pd
import numpy as np
import pytesseract
from PIL import Image
import base64
import time
from datetime import datetime
import random
import socket
import requests  # Bypasses local Google libraries completely
from dotenv import load_dotenv
import os


from pypdf import PdfReader  # Stable PDF extraction engine
from bs4 import BeautifulSoup

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="SOC Platform", layout="wide", page_icon="🛡️")

load_dotenv()  
api_key = os.getenv("api_key")

# =========================
# SESSION STATE INIT
# =========================
if 'sniff_buffer' not in st.session_state:
    st.session_state.sniff_buffer = []

if 'simulated_incidents' not in st.session_state:
    st.session_state.simulated_incidents = []

if 'current_ip' not in st.session_state:
    st.session_state.current_ip = "10.12.1.107"

# =========================
# FILE EXTRACTION ENGINE
# =========================
def clean_vision_extract(uploaded_file):
    fn = uploaded_file.name.lower()

    try:
        # IMAGE
        if fn.endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(uploaded_file)
            text = pytesseract.image_to_string(img)
            return text, img

        # PDF
        elif fn.endswith('.pdf'):
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text, None

        # CSV
        elif fn.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            return df.to_string(), None

        # HTML
        elif fn.endswith('.html'):
            html = uploaded_file.read().decode("utf-8")
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text("\n"), None

    except Exception as e:
        return f"Extraction error: {str(e)}", None

    return "", None

# =========================
# SIDEBAR NAVIGATION
# =========================
with st.sidebar:
    st.title("🛡️ Defender Core")

    nav_selection = st.radio(
        "Navigation",
        ["Executive Dashboard", "Purview DPI Sniffer", "AI Vision Core"]
    )

# =========================
# HEADER
# =========================
st.title(nav_selection)

# =========================
# DASHBOARD
# =========================
if nav_selection == "Executive Dashboard":

    st.metric("Gateway IP", st.session_state.current_ip)
    st.metric("Active Threats", len(st.session_state.simulated_incidents))

    st.line_chart(np.random.randn(20, 2))

    st.dataframe(pd.DataFrame(st.session_state.simulated_incidents))


# =========================
# DPI SNIFFER (SAFE VERSION)
# =========================
elif nav_selection == "Purview DPI Sniffer":

    st.warning("Live sniffing disabled for stability in this build.")

    if st.button("Inject Simulated Threat"):
        st.session_state.simulated_incidents.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "threat": random.choice([
                "RDP Brute Force",
                "DNS Exfiltration",
                "Port Scan"
            ]),
            "target": f"192.168.1.{random.randint(2,254)}"
        })

    st.dataframe(st.session_state.simulated_incidents)


# =========================
# AI VISION CORE (FIXED + STABLE)
# =========================
elif nav_selection == "AI Vision Core":

    file = st.file_uploader(
        "Upload File (Image, PDF, CSV, HTML)",
        type=["png", "jpg", "jpeg", "pdf", "csv", "html"]
    )

    if file:

        raw_text, preview_img = clean_vision_extract(file)

        if preview_img:
            st.image(preview_img, use_container_width=True)
            st.info("Image text extracted locally.")
        else:
            st.info("File loaded successfully.")

        if st.button("RUN NEURAL ANALYSIS"):

            prompt = """
You are a Lead ISO 27001 Auditor.
Identify security anomalies, suggest remediation actions, and provide RTO/RPO recommendations based on the log snippet below.
"""

            try:
                with st.spinner("Streaming lightweight audit data..."):
                    
                    headers = {"Content-Type": "application/json"}
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

                    # COMPACT DATA FIX: We aggressively trim the text down to the first 4,000 characters.
                    # This ensures the packet size is ultra-small, preventing port 443 network routing drops entirely.
                    trimmed_data = raw_text[:4000] if raw_text else "No log text extracted."

                    payload = {
                        "contents": [{
                            "parts": [{"text": f"{prompt}\n\nDATA TO AUDIT (Optimized Snippet):\n{trimmed_data}"}]
                        }]
                    }

                    # Execute the stream
                    response = requests.post(url, headers=headers, json=payload, timeout=45)
                    response_json = response.json()

                    if "candidates" in response_json:
                        ai_report_text = response_json['candidates'][0]['content']['parts'][0]['text']
                        st.success("Analysis Complete")
                        st.markdown("### AI Report")
                        st.write(ai_report_text)
                    elif "error" in response_json:
                        # Clear explanation if the free tier is just temporarily busy
                        error_msg = response_json['error']['message']
                        if "RESOURCE_EXHAUSTED" in str(response_json) or "503" in str(response_json):
                            st.error("Google's free-tier servers are currently experiencing a brief spike in global demand. Please wait 30 seconds and click analyze again to reset your slot.")
                        else:
                            st.error(f"API Connection Error: {error_msg}")
                    else:
                        st.error(f"Unexpected Layout Error: {str(response_json)}")

            except requests.exceptions.Timeout:
                st.error("The network connection dropped mid-stream. Please try using a smaller test file or try clicking the button once more.")
            except Exception as e:
                st.error(f"AI Processing Error: {str(e)}")

    st.caption("Powered by Gemini API")