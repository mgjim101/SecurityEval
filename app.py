import streamlit as st
st.set_page_config(page_title="SecurityEval + GPT Demo", layout="wide")

from streamlit_ace import st_ace
import openai
import os
import json
from dotenv import load_dotenv
import subprocess
import tempfile
from utils.prompts import build_detection_prompt, build_fix_prompt

# Load environment and API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY", "paste_your_key")
if not openai.api_key:
    st.error("❌ OPENAI_API_KEY not found in .env file.")
    st.stop()

# Load dataset
@st.cache_data
def load_securityeval_dataset():
    with open("data/securityeval.jsonl", "r") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]

samples = load_securityeval_dataset()

# UI setup
st.title("🔐 SecurityEval Vulnerability Detection & Fixing with GPT-3.5")

# Sidebar: Settings and sample selector
with st.sidebar:
    st.header("⚙️ Configuration")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.4)
    max_tokens = st.slider("Max Tokens", 100, 2000, 800)
    sample_ids = [sample["ID"] for sample in samples]
    selected_id = st.selectbox("Select a SecurityEval Sample", sample_ids)

# Get selected sample
sample = next((s for s in samples if s["ID"] == selected_id), None)
if not sample:
    st.error("Sample not found!")
    st.stop()

# Display prompt and insecure code
st.subheader("🧪 Prompt Code (Editable)")
user_code = st_ace(value=sample["Prompt"], language="python", theme="monokai", height=300, key="prompt_editor")

st.subheader("❌ Reference Insecure Code")
st.code(sample["Insecure_code"], language="python")

# Step 1: Detect Vulnerability
if st.button("🔍 Detect Vulnerabilities"):
    with st.spinner("Analyzing with GPT-3.5-turbo..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # ✅ switched model
                messages=[{"role": "user", "content": build_detection_prompt(user_code)}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            st.subheader("🛡️ Vulnerability Analysis")
            st.markdown(response["choices"][0]["message"]["content"])
        except Exception as e:
            st.error(f"Error: {e}")

# Step 2: Suggest Fix
if st.button("🛠️ Suggest Fix"):
    with st.spinner("Generating secure version..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # ✅ switched model
                messages=[{"role": "user", "content": build_fix_prompt(user_code)}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            st.subheader("✅ Secure Code & Explanation")
            st.markdown(response["choices"][0]["message"]["content"])
        except Exception as e:
            st.error(f"Error: {e}")

# Step 3: Static analysis with Bandit
if st.button("🧪 Run Bandit (Static Analysis)"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as tmp:
        tmp.write(user_code)
        tmp_path = tmp.name
    try:
        result = subprocess.run(["bandit", tmp_path, "-q", "-r"], capture_output=True, text=True)
        st.subheader("📊 Bandit Result")
        if result.stdout:
            st.code(result.stdout)
        else:
            st.success("✅ No vulnerabilities found by Bandit!")
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        os.unlink(tmp_path)