# reports_ui.py
import streamlit as st
from mailreport import send_email_report

def run_reports_ui():
    st.subheader("📧 Send Email Report")

    to_email = st.text_input("Recipient Email:", placeholder="example@gmail.com")
    subject = st.text_input("Email Subject:", value="SafeRideAI Report")
    body = st.text_area("Email Body:", value="Hello,\n\nPlease find the attached SafeRideAI report.\n\nRegards,\nSafeRideAI")

    uploaded_file = st.file_uploader("Upload Report File (PDF/CSV):", type=["pdf", "csv"])

    if st.button("Send Email"):
        if not to_email:
            st.warning("⚠️ Please enter recipient email.")
            return
        if not uploaded_file:
            st.warning("⚠️ Please upload a report file to send.")
            return

        # Save uploaded file temporarily
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_path = uploaded_file.name

        # Call the email function
        success = send_email_report(
            to_email=to_email,
            subject=subject,
            body=body,
            attachment_path=file_path
        )

        if success:
            st.success(f"✅ Email sent successfully to {to_email}")
        else:
            st.error("⚠️ Failed to send email. Check logs for details.")
