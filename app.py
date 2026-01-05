# app.py
import streamlit as st
import requests
import matplotlib.pyplot as plt
import openai

# ----------------------------
# Streamlit page configuration
# ----------------------------
st.set_page_config(page_title="Knife Skills AI", page_icon="🔪")
st.title("🔪 Knife Knowledge & Skills AI Tutor")
st.write("Learn about knife skills, diagrams, and knife anatomy.")

# ----------------------------
# OpenAI API key
# ----------------------------
openai.api_key = st.secrets.get("OPENAI_API_KEY") or None
if not openai.api_key:
    st.warning("OpenAI API key not found! GPT fallback will not work.")

# ----------------------------
# Wikipedia + fallback functions
# ----------------------------
@st.cache_data(show_spinner=False)
def search_wikipedia(query):
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action":"query","list":"search","srsearch":query,"format":"json"},
            timeout=5
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("query", {}).get("search")
        if results:
            return results[0]["title"]
        return None
    except requests.RequestException:
        return None

@st.cache_data(show_spinner=False)
def get_summary(title):
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}", timeout=5)
        r.raise_for_status()
        return r.json().get("extract")
    except requests.RequestException:
        return None

def fetch_fallback(query):
    """Fallback text from DuckDuckGo Instant Answer API."""
    try:
        r = requests.get("https://api.duckduckgo.com/",
                         params={"q": query, "format": "json", "no_redirect": 1},
                         timeout=5)
        r.raise_for_status()
        data = r.json()
        return data.get("AbstractText") or None
    except requests.RequestException:
        return None

def gpt_fallback(query):
    """Fallback text from GPT if APIs fail."""
    if not openai.api_key:
        return "Sorry, no information could be found and GPT fallback is unavailable."
    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert on knife skills."},
                {"role": "user", "content": f"Explain about: {query}"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return resp.choices[0].message.content.strip()
    except openai.OpenAIError as e:   # <- fixed
        return f"Sorry, GPT fallback failed: {e}"
    except Exception as e:
        return f"Unexpected error in GPT fallback: {e}"

def get_info(query):
    """Try Wikipedia -> DuckDuckGo -> GPT fallback"""
    title = search_wikipedia(f"knife {query}")
    summary = get_summary(title) if title else None
    if summary:
        return summary
    summary = fetch_fallback(f"knife {query}")
    if summary:
        return summary
    return gpt_fallback(f"knife {query}")

# ----------------------------
# Diagram functions
# ----------------------------
def blade_angle():
    fig, ax = plt.subplots(figsize=(5,2))
    ax.plot([0,5],[0,0], linewidth=3, color="black")  # base
    ax.plot([0,5],[0,2], linewidth=2, color="red")    # blade angle
    ax.text(2.5,0.3,"15–20°", fontsize=12, color="blue")
    ax.axis("off")
    st.pyplot(fig, clear_figure=True)

def knife_anatomy():
    fig, ax = plt.subplots(figsize=(6,2))
    ax.plot([0,5],[1,1], linewidth=4, color="gray")  # blade
    ax.plot([5,7],[1,1], linewidth=6, color="brown") # handle
    ax.text(2.5,1.2,"Blade", fontsize=12)
    ax.text(5.5,1.2,"Handle", fontsize=12)
    ax.axis("off")
    st.pyplot(fig, clear_figure=True)

# ----------------------------
# User input
# ----------------------------
question = st.text_input("Ask a knife question:")

if question.strip():
    # Show diagrams based on keywords
    if any(k in question.lower() for k in ["angle", "sharpen"]):
        with st.expander("🔪 Blade Angle Diagram"):
            blade_angle()
            
    if any(k in question.lower() for k in ["parts", "anatomy"]):
        with st.expander("🗂 Knife Anatomy Diagram"):
            knife_anatomy()
    
    # Fetch summary (Wikipedia -> DuckDuckGo -> GPT)
    with st.spinner("Fetching information..."):
        summary = get_info(question)
    st.subheader("📚 AI Answer")
    st.write(summary)

st.caption("⚠️ Educational use only. Always practice knife skills safely.")
