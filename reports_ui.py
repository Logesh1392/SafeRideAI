import streamlit as st 
from mailreport import send_email_report
from report_generate import generate_report


def reports_ui():
    st.subheader("📧 Send Email Report")

    # 🔹 Report type dropdown
    report_type_ui = st.selectbox(
        "Select Report Type:",
        ["last_24h", "weekly", "monthly", "accident", "helmet"]
    )

    # 🔹 Email inputs
    to_email = st.text_input("Recipient Email:", placeholder="example@gmail.com")
    subject = st.text_input("Email Subject:", value="SafeRideAI Report")
    body = st.text_area(
        "Email Body:",
        value="Hello,\n\nPlease find the attached SafeRideAI report.\n\nRegards,\nSafeRideAI"
    )

    # 🔹 Button action
    if st.button("📤 Generate & Send Report"):
        if not to_email:
            st.warning("⚠️ Please enter recipient email.")
            return

        # Generate PDF
        file_path = generate_report(
            report_type=report_type_ui,
            output_path="report.pdf"
        )

        # Send email
        success = send_email_report(
            to_email=to_email,
            subject=subject,
            body=body,
            attachment_path=file_path
        )

        if success:
            st.success(f"✅ {report_type_ui.replace('_', ' ').title()} report sent successfully to {to_email}")
        else:
            st.error("⚠️ Failed to send email. Check logs for details.")
