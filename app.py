import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import openai
import os

# ----------------------------
# Streamlit page configuration
# ----------------------------
st.set_page_config(page_title="Knife Skills AI", page_icon="🔪")
st.title("🔪 Knife Knowledge & Skills AI Tutor")
st.write("Learn about knife skills, diagrams, knife anatomy, and see AI-generated images safely.")

# ----------------------------
# OpenAI API key (Cloud or local)
# ----------------------------
# First try Streamlit Secrets
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# If not found, try environment variable (for local testing)
if not openai.api_key:
    openai.api_key = os.getenv("OPENAI_API_KEY")

# Warn if missing
if not openai.api_key:
    st.warning("OpenAI API key not found! AI image generation will not work.")

# ----------------------------
# Wikipedia + fallback search
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
        if data.get("query", {}).get("search"):
            return data["query"]["search"][0]["title"]
        return None
    except requests.RequestException:
        return None

@st.cache_data(show_spinner=False)
def get_summary(title):
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}", timeout=5)
        r.raise_for_status()
        return r.json().get("extract", "No summary available.")
    except requests.RequestException:
        return "Information temporarily unavailable."

def fetch_fallback(query):
    """Fallback text from DuckDuckGo Instant Answer API."""
    try:
        r = requests.get("https://api.duckduckgo.com/",
                         params={"q": query, "format": "json", "no_redirect": 1},
                         timeout=5)
        r.raise_for_status()
        data = r.json()
        return data.get("AbstractText") or "No text found for this topic."
    except requests.RequestException:
        return "No additional text available."

# ----------------------------
# AI image generation (fixed size)
# ----------------------------
def generate_ai_image(prompt):
    if not openai.api_key:
        return None
    try:
        response = openai.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1536"  # vertical orientation for knives
        )
        if response.data and len(response.data) > 0:
            image_url = response.data[0].url
            return Image.open(BytesIO(requests.get(image_url).content))
        else:
            st.error("No image returned from API.")
            return None
    except Exception as e:
        st.error(f"Image generation failed: {e}")
        return None

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
    
    # Fetch Wikipedia summary with fallback
    with st.spinner("Fetching information..."):
        title = search_wikipedia(f"knife {question}")
        summary = get_summary(title) if title else fetch_fallback(f"knife {question}")
        if not summary or summary.strip() == "":
            summary = "Sorry, no information could be found for this topic."

    st.subheader("📚 AI Answer")
    st.write(summary)

    # AI-generated image
    if openai.api_key:
        with st.spinner("Generating AI image..."):
            image_prompt = f"High-quality, realistic illustration of {question} knife skill or tool"
            img = generate_ai_image(image_prompt)
            if img:
                st.subheader("🖼️ AI Image")
                st.image(img, use_column_width=True)

st.caption("⚠️ Educational use only. Always practice knife skills safely.")

