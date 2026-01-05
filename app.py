import streamlit as st
import requests
import matplotlib.pyplot as plt

# ----------------------------
# Streamlit page configuration
# ----------------------------
st.set_page_config(page_title="Knife Skills AI", page_icon="🔪")
st.title("🔪 Knife Knowledge & Skills AI Tutor")
st.write("Learn about knife skills, diagrams, and knife anatomy safely.")

# ----------------------------
# Wikipedia API functions
# ----------------------------
@st.cache_data(show_spinner=False)
def search_wikipedia(query):
    """Search Wikipedia and return the first matching title."""
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action":"query","list":"search","srsearch":query,"format":"json"},
            timeout=5
        )
        r.raise_for_status()
        data = r.json()
        if data["query"]["search"]:
            return data["query"]["search"][0]["title"]
        return None
    except requests.RequestException:
        return None

@st.cache_data(show_spinner=False)
def get_summary(title):
    """Get summary of a Wikipedia page by title."""
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}", timeout=5)
        r.raise_for_status()
        return r.json().get("extract", "No summary available.")
    except requests.RequestException:
        return "Information temporarily unavailable."

# ----------------------------
# Diagram functions
# ----------------------------
def blade_angle():
    """Draw a blade sharpening angle diagram."""
    fig, ax = plt.subplots(figsize=(5,2))
    ax.plot([0,5],[0,0],linewidth=3, color="black")  # base
    ax.plot([0,5],[0,2], linewidth=2, color="red")   # blade angle
    ax.text(2.5,0.3,"15–20°", fontsize=12, color="blue")
    ax.axis("off")
    st.pyplot(fig)

def knife_anatomy():
    """Draw a simple knife anatomy diagram."""
    fig, ax = plt.subplots(figsize=(6,2))
    ax.plot([0,5],[1,1], linewidth=4, color="gray")  # blade
    ax.plot([5,7],[1,1], linewidth=6, color="brown") # handle
    ax.text(2.5,1.2,"Blade", fontsize=12)
    ax.text(5.5,1.2,"Handle", fontsize=12)
    ax.axis("off")
    st.pyplot(fig)

# ----------------------------
# User input
# ----------------------------
question = st.text_input("Ask a knife question:")

if question:
    # ----------------------------
    # Show diagrams based on keywords
    # ----------------------------
    if any(k in question.lower() for k in ["angle", "sharpen"]):
        with st.expander("🔪 Blade Angle Diagram"):
            blade_angle()
            
    if any(k in question.lower() for k in ["parts", "anatomy"]):
        with st.expander("🗂 Knife Anatomy Diagram"):
            knife_anatomy()
    
    # ----------------------------
    # Fetch Wikipedia summary
    # ----------------------------
    title = search_wikipedia(f"knife {question}")
    if title:
        st.subheader("📚 AI Answer")
        st.write(get_summary(title))
    else:
        st.warning("Could not find reliable information on Wikipedia.")

st.caption("⚠️ Educational use only. Always practice knife skills safely.")
