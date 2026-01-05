import streamlit as st
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="Knife Skills AI", page_icon="🔪")
st.title("🔪 Knife Knowledge & Skills AI Tutor")
st.write("Educational knife skills, diagrams, and knowledge.")

def search_wikipedia(query):
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action":"query","list":"search","srsearch":query,"format":"json"},
            timeout=5
        )
        r.raise_for_status()
        data = r.json()
        return data["query"]["search"][0]["title"]
    except:
        return None

def get_summary(title):
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}",
            timeout=5
        )
        r.raise_for_status()
        return r.json().get("extract","")
    except:
        return "Information temporarily unavailable."

def blade_angle():
    fig, ax = plt.subplots()
    ax.plot([0,5],[0,0],linewidth=3)
    ax.plot([0,5],[0,2])
    ax.text(2.2,0.4,"15–20°")
    ax.axis("off")
    st.pyplot(fig)

def knife_anatomy():
    fig, ax = plt.subplots()
    ax.plot([0,5],[1,1],linewidth=4)
    ax.plot([5,7],[1,1],linewidth=6)
    ax.text(2,1.3,"Blade")
    ax.text(5.5,1.3,"Handle")
    ax.axis("off")
    st.pyplot(fig)

question = st.text_input("Ask a knife question:")

if question:
    if "angle" in question or "sharpen" in question:
        blade_angle()

    if "parts" in question or "anatomy" in question:
        knife_anatomy()

    title = search_wikipedia(f"knife {question}")
    if title:
        st.subheader("AI Answer")
        st.write(get_summary(title))
    else:
        st.write("Could not find reliable information.")

st.caption("⚠️ Educational use only. Always practice knife skills safely.")
