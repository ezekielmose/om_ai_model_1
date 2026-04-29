import streamlit as st
from main import run_pipeline
from services.instagram_finder_v2 import find_instagram_profile
from services.instagram_reels_scraper import get_reels_from_profile
#from services.instagram_finder_v2 import find_instagram_link


# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="OM AI Analizer",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ===============================
# UI STYLE
# ===============================
st.markdown("""
<style>
    .main {
        background-color: #e6f0ff;
        color: #000000;
    }

    section[data-testid="stSidebar"] {
        background-color: #0b3c5d;
        color: white;
    }

    .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    h1, h2, h3 {
        color: #0b3c5d;
    }

    .stButton>button {
        background-color: #1d4ed8;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
    }

    .stButton>button:hover {
        background-color: #16a34a;
    }

    /* Horizontal scene viewer */
    .scene-row {
        display: flex;
        gap: 12px;
        overflow-x: auto;
        padding: 10px 0;
    }

    .scene-box {
        min-width: 180px;
        background: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #1d4ed8;
        flex-shrink: 0;
    }
</style>
""", unsafe_allow_html=True)


# ===============================
# SESSION STATE
# ===============================
if "instagram_result" not in st.session_state:
    st.session_state.instagram_result = None

if "reels_data" not in st.session_state:
    st.session_state.reels_data = None

if "reel_analysis" not in st.session_state:
    st.session_state.reel_analysis = {}

if "batch_results" not in st.session_state:
    st.session_state.batch_results = []

if "air_results" not in st.session_state:
    st.session_state.air_results = []


# ===============================
# SIDEBAR MENU
# ===============================
st.sidebar.title("OM AI Model")

menu = st.sidebar.radio(
    ".",
    [
        "Hotel Profiles & Reels Analysis",
        "Batch Reels Analysis",
        "Air Videos Analysis",
        "Upload on Air",
        "Reports"
    ]
)


# ===============================
# MODULE 1 (UPDATED WITH AUTO FILL)
# ===============================
if menu == "Hotel Profiles & Reels Analysis":

    import pandas as pd

    # -----------------------------
    # TITLE
    # -----------------------------
    st.title("🏨 Smart Instagram Profile Finder")
    st.write("Find the best matching Instagram profile for a hotel.")

    # -----------------------------
    # GOOGLE SHEET CONFIG
    # -----------------------------
    SHEET_ID = "1gh2QMj4vngL-JLf6SPmWvjSuCgl9uItTAMteY3acVNg"
    SHEET_GID = "204054788"

    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET_GID}"

    # -----------------------------
    # LOAD SHEET
    # -----------------------------
    @st.cache_data
    def load_sheet():
        return pd.read_csv(SHEET_URL, dtype=str)

    # -----------------------------
    # CLEAN ID FUNCTION
    # -----------------------------
    def clean_id(value):
        return str(value).strip().lower() if value else ""

    # -----------------------------
    # AUTO FILL SECTION
    # -----------------------------
    st.subheader("⚡ Auto Fill from Item ID")

    item_id = st.text_input(
        "Item ID",
        placeholder="e.g. 846e9ee4-e5e4-434d-b6ac-ef67c301b3e8"
    )

    if st.button("⚡ Auto Fill"):

        if item_id:
            try:
                df = load_sheet()

                # Column B = Item ID
                id_column = df.iloc[:, 1].apply(clean_id)
                input_id = clean_id(item_id)

                match = df[id_column == input_id]

                if not match.empty:
                    st.session_state.hotel_name = str(match.iloc[0, 2]).strip()
                    st.session_state.city = str(match.iloc[0, 3]).strip()
                    st.session_state.country = str(match.iloc[0, 4]).strip()

                    st.success("✅ Auto-filled successfully!")

                else:
                    st.error("❌ Item ID not found in sheet.")

            except Exception as e:
                st.error(f"Error loading sheet: {e}")

        else:
            st.warning("⚠️ Please enter an Item ID.")

    # -----------------------------
    # INPUT FIELDS
    # -----------------------------
    hotel_name = st.text_input(
        "Hotel Name",
        value=st.session_state.get("hotel_name", ""),
        placeholder="e.g. Sweets Ijdoornlaanbrug"
    )

    city = st.text_input(
        "City",
        value=st.session_state.get("city", ""),
        placeholder="e.g. Amsterdam"
    )

    country = st.text_input(
        "Country",
        value=st.session_state.get("country", ""),
        placeholder="e.g. Netherlands"
    )

    # -----------------------------
    # INSTAGRAM SEARCH
    # -----------------------------
    if st.button("Instagram Page"):

        if not hotel_name or not city or not country:
            st.warning("Please fill Hotel Name, City and Country")

        else:
            with st.spinner("Finding Instagram profile using AI matching..."):
                result = find_instagram_profile(hotel_name, city, country)

            if result:
                result["instagram"] = result.get("url")

            st.session_state.instagram_result = result
            st.session_state.reels_data = None
            st.session_state.reel_analysis = {}

    # -----------------------------
    # DISPLAY RESULT
    # -----------------------------
    if st.session_state.instagram_result:

        result = st.session_state.instagram_result

        if result and result.get("instagram"):

            st.success("Instagram Found")

            st.markdown(f"[Open Profile]({result['instagram']})")
            st.caption(f"Username: {result.get('username', '')}")

            username = result.get("username") or result["instagram"].rstrip("/").split("/")[-1]

        else:
            st.error("No Instagram page found")

            if st.button("Fetch Reels"):

                with st.spinner("Fetching reels..."):
                    reels_data = get_reels_from_profile(username)

                st.session_state.reels_data = reels_data

        

    # -----------------------------
    # DISPLAY REELS
    # -----------------------------
    if st.session_state.reels_data:

        reels_data = st.session_state.reels_data

        if reels_data.get("success"):

            st.markdown("## Reels Found")

            for idx, reel in enumerate(reels_data.get("reels", []), 1):

                url = reel.get("url")

                st.markdown(f"### Reel {idx}")
                st.write(url)

                col1, col2 = st.columns([1, 3])

                if col1.button(f"Analyze Reel {idx}"):

                    status = st.status("Analyzing reel and extracting scenes...", expanded=True)
                    scene_placeholder = st.empty()

                    with status:

                        st.write("Running AI pipeline...")

                        result = run_pipeline(url)

                        st.write("Processing scenes...")

                        results = result.get("results", [])
                        total = len(results)

                        st.session_state.reel_analysis[url] = result

                        for i, scene in enumerate(results, 1):

                            scene_placeholder.markdown(
                                f"""
                                **Scene {i}/{total}**

                                {scene.get('analysis', 'Processing...')}

                                ---
                                """
                            )

                        st.write("Finalizing analysis...")

                if url in st.session_state.reel_analysis:

                    result = st.session_state.reel_analysis[url]

                    c1, c2, c3 = st.columns(3)

                    c1.metric("Score", result.get("score", 0))
                    c2.metric("Duration", result.get("duration", 0))
                    c3.metric("Status", "PASSED" if result.get("passed") else "FAILED")

                    if not result.get("passed"):

                        st.error("❌ Issues")
                        for issue in result.get("issues", []):
                            if isinstance(issue, list):
                                for sub_issue in issue:
                                    st.write(f"- {sub_issue}")
                            else:
                                st.write(f"- {issue}")

                    else:

                        st.success("✅ Approved Reel")

                        positives = []
                        results = result.get("results", [])

                        elements = []
                        for scene in results:
                            elements.extend(scene.get("hotel_elements", []))

                        unique_elements = list(set([e for e in elements if e]))

                        if unique_elements:
                            positives.append(
                                "Showcases hotel experience: " + ", ".join(unique_elements)
                            )

                        for i, scene in enumerate(results, 1):
                            analysis = (scene.get("analysis") or "").strip()
                            if analysis:
                                positives.append(f"Scene {i}: {analysis}")

                        full_text = " ".join(
                            [(scene.get("analysis") or "").lower() for scene in results]
                        )

                        signal_map = {
                            "smooth": "Smooth camera movement",
                            "lighting": "Good lighting quality",
                            "well lit": "Good lighting quality",
                            "luxury": "Strong luxury/premium appeal",
                            "premium": "Strong luxury/premium appeal",
                            "clear": "Clear and well-framed visuals",
                            "experience": "Clearly communicates hotel experience",
                            "cinematic": "Cinematic visual style",
                        }

                        for keyword, label in signal_map.items():
                            if keyword in full_text:
                                positives.append(label)

                        if not positives:
                            positives.append(
                                "Approved based on overall visual quality, clarity, and engagement signals"
                            )

                        st.markdown("### 🟢 Why this reel was approved")

                        for p in positives:
                            st.write(f"- {p}")

                    st.markdown("---")

        else:
            st.error(reels_data.get("error", "Failed to fetch reels"))

# ===============================
# MODULE 2
# ===============================
elif menu == "Batch Reels Analysis":

    st.title("Batch Reels Analysis")
    st.caption("Analyze multiple reels at once")

    batch_input = st.text_area("Paste Reel URLs (one per line)", height=180)

    if st.button("Run The Analysis"):

        if not batch_input.strip():
            st.warning("Please paste reel URLs")

        else:
            urls = [u.strip() for u in batch_input.split("\n") if u.strip()]
            results = []

            progress = st.progress(0)

            for i, url in enumerate(urls):

                with st.spinner(f"Processing {i+1}/{len(urls)}"):
                    try:
                        result = run_pipeline(url)
                    except Exception as e:
                        result = {
                            "score": 0,
                            "duration": 0,
                            "passed": False,
                            "results": [],
                            "issues": [str(e)]
                        }

                results.append((url, result))
                progress.progress((i + 1) / len(urls))

            results.sort(key=lambda x: x[1].get("score", 0), reverse=True)
            st.session_state.batch_results = results

    if st.session_state.batch_results:

        st.markdown("## Ranked Results")

        for idx, (url, result) in enumerate(st.session_state.batch_results, 1):

            st.markdown(f"### #{idx} 🎬 Reel")

            c1, c2, c3 = st.columns(3)

            c1.metric("Score", result.get("score", 0))
            c2.metric("Duration", result.get("duration", 0))
            c3.metric("Status", "APPROVED" if result.get("passed") else "REJECTED")

            st.write(url)

            if not result.get("passed"):
                st.error("❌ Issues")
                for issue in result.get("issues", []):
                    if isinstance(issue, list):
                        for sub_issue in issue:
                            st.write(f"- {sub_issue}")
                    else:
                        st.write(f"- {issue}")
            else:
                st.success("✅ Approved Reel")

            st.markdown("---")


# ===============================
# MODULE 3 - AIR VIDEOS ANALYSIS
# ===============================
elif menu == "Air Videos Analysis":

    import os
    import requests

    st.title("Air Videos Analysis")
    st.caption("Download Air videos directly to local storage")

    air_url = st.text_input("Paste Air Video Download Link")

    save_path = r"D:\Air"

    if st.button("Generate and Analyze the Video"):

        if not air_url:
            st.warning("Please paste a video link")

        else:
            try:
                os.makedirs(save_path, exist_ok=True)

                with st.spinner("Generating the video..."):

                    response = requests.get(air_url, stream=True)

                    if response.status_code == 200:

                        file_name = air_url.split("/")[-1].split("?")[0]
                        if not file_name.endswith(".mp4"):
                            file_name += ".mp4"

                        full_path = os.path.join(save_path, file_name)

                        with open(full_path, "wb") as f:
                            for chunk in response.iter_content(chunk_size=1024 * 1024):
                                if chunk:
                                    f.write(chunk)

                        st.success("✅ Video downloaded successfully")
                        st.write(f"Saved to: {full_path}")

                        st.session_state.air_results.append(full_path)

                    else:
                        st.error("Failed to download video")

            except Exception as e:
                st.error(f"Error: {str(e)}")

    if st.session_state.air_results:
        st.markdown("## 📂 Downloaded Videos")

        for vid in st.session_state.air_results:
            st.write(vid)


# ===============================
# MODULE 4
# ===============================
elif menu == "Upload on Air":

    st.title("🚀 Upload on Air")
    st.info("Coming soon: Upload approved reels to Instagram or storage pipeline")


# ===============================
# MODULE 5
# ===============================
elif menu == "Reports":

    st.title("📊 Reports")
    st.info("Coming soon: analytics, trends, and performance dashboard")