import streamlit as st
import uuid
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------- CONFIG -------------------
st.set_page_config(page_title="BA Discovery Assistant", layout="centered")
st.title("Business Analyst Requirement Discovery Assistant")

# ------------------- OPENAI SETUP -------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ------------------- GOOGLE SHEETS SETUP -------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds_dict = dict(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# ✅ Your Google sheet and tab name
sheet = client.open("BA_Discovery_Data").worksheet("sessions")

# ------------------- QUESTIONS -------------------
questions = [
    "What problem are you trying to solve?",
    "Who is affected by this problem?",
    "How is this handled today?",
    "What are the main challenges with the current process?",
    "What does success look like?",
]

# ------------------- SESSION ID -------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.write(f"🧾 Session ID: `{st.session_state.session_id}`")

context = st.text_input("Discovery Context (Project / Client / Team)")

st.divider()

# ------------------- FORM -------------------
for q in questions:
    st.subheader(q)
    response = st.text_area("Stakeholder Response", key=q)

    if st.button(f"Save Answer for: {q}"):

        if context.strip() == "":
            st.error("Please enter Discovery Context first.")
            st.stop()

        if response.strip() == "":
            st.error("Response cannot be empty.")
            st.stop()

        prompt = f"""
You are a Business Analyst discovery assistant.
Extract in structured bullets:

1) Core challenge
2) Functional requirement
3) Non-functional requirement
4) Assumption
5) Open question

Stakeholder response:
{response}
"""

        try:
            ai = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            analysis = ai.choices[0].message.content

            # Save to Google Sheets
            sheet.append_row([
                st.session_state.session_id,
                context,
                q,
                response,
                analysis
            ])

            st.success("✅ Saved to Google Sheets with AI analysis!")

        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

if st.button("Start New Discovery Session"):
    st.session_state.session_id = str(uuid.uuid4())
    st.rerun()




