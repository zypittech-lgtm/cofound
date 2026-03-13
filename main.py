import streamlit as st
from sqlalchemy import create_engine, text
import random as rn
import requests

# =========================
# RAPIDAPI KEYS
# =========================
rapidapi1 = "6b9e6656a7mshb9cb119d7ced4bfp1b7e4bjsn3ce33b5f0b31"
rapidapi2 = "8274915d9fmsh2eb8cf5020f9a29p16f610jsn0cf7ae99e4c4"
rapidapi3 = "b7efb94b03msh0152780f05d2292p17d0c0jsn56a4769a94c2"
rapidapi4 = "f2a1062537msh6f4ce61895f3d86p1f06f8jsn9e4cfec8bcb8"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Zypit Cofounder Dashboard",
    layout="wide"
)
PASSWORD = "zypitisthebest"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password_input = st.text_input("Enter password", type="password")

    if password_input == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.stop()
st.title("Zypit Cofounder Dashboard")

# =========================
# DATABASE CONNECTION
# =========================
DATABASE_URL = "postgresql://postgres:tEHexGzOJxcZzDvHcdbxzfnqmxYWQDZx@ballast.proxy.rlwy.net:37416/railway"
engine = create_engine(DATABASE_URL)

# =========================
# RANDOM KEY SELECTOR
# =========================
def keyselector(n1, n2, n3, n4):
    randnum = rn.randint(0, 3)
    if randnum == 0:
        return n1
    elif randnum == 1:
        return n2
    elif randnum == 2:
        return n3
    else:
        return n4

# =========================
# PLATFORM DETECTION
# =========================
def detect_platform(link):
    if not link:
        return "Unknown"
    link_lower = link.lower()
    if "instagram.com" in link_lower:
        return "Instagram"
    elif "youtube.com" in link_lower or "youtu.be" in link_lower:
        return "YouTube"
    elif "tiktok.com" in link_lower:
        return "TikTok"
    elif "facebook.com" in link_lower:
        return "Facebook"
    return "Unknown"

# =========================
# SAFE JSON VALUE EXTRACTOR
# =========================
def deep_get(data, possible_paths, default=None):
    for path in possible_paths:
        current = data
        found = True
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                found = False
                break
        if found and current is not None:
            return current
    return default

# =========================
# INSTAGRAM STATS FETCHER
# =========================
def clean_instagram_url(url):
    if not url:
        return url

    url = url.strip()

    # Remove query params like ?igsh=...
    url = url.split("?")[0]

    # Remove trailing slash duplicates
    url = url.rstrip("/")

    # Keep canonical Instagram reel/post URL format
    return url + "/"

def fetch_instagram_details(posturl):
    key = keyselector(rapidapi4, rapidapi1, rapidapi2, rapidapi3)
    posturl = clean_instagram_url(posturl)
    url = "https://instagram-statistics-api.p.rapidapi.com/posts/one"
    querystring = {"postUrl": posturl}

    headers = {
        "x-rapidapi-key": key,
        "x-rapidapi-host": "instagram-statistics-api.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()
# =========================
# FETCH USERS WITH SUBMISSIONS
# =========================
users_query = text("""
SELECT DISTINCT u.id, u.full_name
FROM users u
JOIN campaign_participants cp
    ON u.id = cp.creator_id
ORDER BY u.full_name
""")

with engine.connect() as conn:
    creators = conn.execute(users_query).fetchall()

creator_names = [creator.full_name for creator in creators]

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("Creators with Submissions")
    selected_creator = st.selectbox("Select Creator", creator_names)

# =========================
# FETCH SELECTED CREATOR DETAILS
# =========================
details_query = text("""
SELECT
    u.id,
    u.full_name,
    ai.email,
    cpr.upi_id,
    cp.reel_link
FROM users u
LEFT JOIN auth_identities ai
    ON u.id = ai.user_id
LEFT JOIN creator_profiles cpr
    ON u.id = cpr.user_id
LEFT JOIN campaign_participants cp
    ON u.id = cp.creator_id
WHERE u.full_name = :selected_creator
ORDER BY cp.id DESC
LIMIT 1
""")

with engine.connect() as conn:
    creator_details = conn.execute(
        details_query,
        {"selected_creator": selected_creator}
    ).fetchone()

# =========================
# DISPLAY DETAILS
# =========================
if creator_details:
    st.subheader("Creator Details")
    st.write(f"**Name:** {creator_details.full_name}")
    st.write(f"**Email:** {creator_details.email if creator_details.email else 'Not available'}")
    st.write(f"**UPI ID:** {creator_details.upi_id if creator_details.upi_id else 'Not available'}")

    st.subheader("Instagram")

    platform = detect_platform(creator_details.reel_link)
    st.write(f"**Platform:** {platform}")

    if creator_details.reel_link:
        st.markdown(f"**Content Link:** [Open Link]({creator_details.reel_link})")

        if platform == "Instagram":
            stats = fetch_instagram_details(creator_details.reel_link)
            likes = stats["data"]["likes"]
            views = stats["data"]["views"]
            comments = stats["data"]["comments"]
            st.write(f"**Likes:** {likes}")
            st.write(f"**Views:** {views}")
            st.write(f"**Comments:** {comments}")
            if views < 5000:
                st.write("NOT APPLICABLE FOR A PAYOUT")
            else:
                payout =views/1000 * 100
                st.write(f"**Payout:** Rupees {payout}")
        else:
            st.info("Selected link is not an Instagram link.")
    else:
        st.write("**Content Link:** Not available")
else:
    st.warning("No details found for the selected creator.")

PASSWORD = "mypassword123"
