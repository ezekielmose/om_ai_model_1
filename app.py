import streamlit as st
from main import run_single_pipeline

st.title("Genesis Digital Reel Analyzer")

reel_url = st.text_input("Enter Instagram Reel URL")

if st.button("Analyze Reel"):

    if reel_url:

        with st.spinner("Analyzing video..."):
            result = run_single_pipeline(reel_url)

        st.success("Analysis Complete")

        st.write("Final Score:", result["score"])
        st.write("Passed:", result["passed"])
        st.write("Duration:", result["duration"])

        st.subheader("Issues")
        st.write(result["issues"])

        st.subheader("Positives")
        st.write(result["positives"])

    else:
        st.warning("Please enter a URL")
