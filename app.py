import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import streamlit as st

# --- SECURE CONFIGURATION (Palled from Streamlit Cloud Secrets) ---
AIRTABLE_PAT = st.secrets["AIRTABLE_PAT"]
BASE_ID = st.secrets["BASE_ID"]
TABLE_NAME = st.secrets["TABLE_NAME"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = st.secrets["SENDER_EMAIL"] 
SENDER_PASSWORD = st.secrets["SENDER_PASSWORD"] 

# --- INITIALIZE SESSION STATE ---
if "sending_in_progress" not in st.session_state:
    st.session_state.sending_in_progress = False

# --- FUNCTIONS ---
def fetch_contacts():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json",
    }
    params = {"filterByFormula": "{Send} = 1"}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get("records", [])
        return []
    except Exception:
        return []

def send_email(to_email, salutation, company_name):
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
      <head><meta charset="UTF-8" /></head>
      <body style="font-family: Georgia, serif; line-height: 1.6;">
          <p>Hi {salutation},</p>
          <p>
            I'm <strong>Sumit Garg</strong> graduated from <strong>NIT Silchar</strong>, currently working as an <strong>Associate Data Scientist at ZS</strong> 
            with around <strong>1.5 years of experience</strong> in data science and machine learning.
          </p>
          <p>
            I'm exploring <strong>Data Scientist / ML Engineer</strong> roles and believe <strong>{company_name}</strong> 
            could be a great fit. Please find my resume 
            <a href="https://drive.google.com/file/d/1y3NuxZfM37wBR3r5I67NspxDL-C7LWHV/view?usp=drive_link" 
               style="color: #0073e6; text-decoration: none;">here</a>.
          </p>
          <p>Let me know the job opportunities which align with my profile</p>
          <p>Happy to connect at your convenience.</p>
          <p>
            <strong>Sumit Garg</strong><br />
            <a href="tel:+918368096808" style="color: #0073e6; text-decoration: none;">+91-8368096808</a><br />
            <a href="https://www.linkedin.com/in/sumit-garg-637b22193/" style="color: #0073e6; text-decoration: none;">LinkedIn</a>
            |
            <a href="https://github.com/sumitgarg21" style="color: #0073e6; text-decoration: none;">GitHub</a>
          </p>
      </body>
    </html>
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Exploring Data Scientist / ML Engineer opportunities at {company_name}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(html_template, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception:
        return False

# --- STREAMLIT UI ---
st.title("🚀 Outreach Portal")

button_placeholder = st.empty()

if st.session_state.sending_in_progress:
    button_placeholder.button("Sending...", disabled=True, type="secondary")
else:
    if button_placeholder.button("Extract & Send Emails", type="primary"):
        st.session_state.sending_in_progress = True
        st.rerun()

if st.session_state.sending_in_progress:
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    records = fetch_contacts()

    if not records:
        st.warning("No records found with Send = 1.")
        st.session_state.sending_in_progress = False
        st.rerun()
    
    y = len(records)
    x = 0
    
    for index, record in enumerate(records):
        fields = record.get("fields", {})
        email = fields.get("Email")
        salutation = fields.get("Salutation", "Sir/Mam")
        company = fields.get("Company", "your company")
        
        if email:
            status_text.text(f"Sending ({index + 1}/{y}) to {email}...")
            if send_email(email, salutation, company):
                x += 1
            progress_bar.progress((index + 1) / y)
            time.sleep(2.0)  # Safe spacing for mobile execution stability

    status_text.empty()
    progress_bar.empty()
    
    if x == y:
        st.success(f"🎉 Success! {x}/{y} mails sent successfully.")
    else:
        st.warning(f"⚠️ Completed with exceptions: {x}/{y} mails sent successfully.")

    st.session_state.sending_in_progress = False
    if st.button("Clear & Reset Page"):
        st.rerun()