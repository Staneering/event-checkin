import streamlit as st
import pandas as pd
import os

# ----------------------------
# Load participants CSV
# ----------------------------
CSV_FILE = "participants.csv"

if not os.path.exists(CSV_FILE):
    st.error(f"CSV file '{CSV_FILE}' not found!")
    st.stop()

df = pd.read_csv(CSV_FILE)

# Ensure checkin_status column exists
if "checkin_status" not in df.columns:
    df["checkin_status"] = "Not Checked In"

# ----------------------------
# App Title
# ----------------------------
st.title("Event Check-In App")
st.write("Scan the QR code or enter email to verify registration.")

# ----------------------------
# QR Code Scan / Email Input
# ----------------------------
# Option 1: URL Query param (for QR code links like https://yourapp.app/?code=email)
scanned_email = st.experimental_get_query_params().get("code", [""])[0]

# Option 2: Manual entry (backup)
manual_email = st.text_input("Or enter attendee email manually:")

email_to_check = scanned_email if scanned_email else manual_email

if email_to_check:
    # Lookup attendee
    match = df[df["email"].str.strip().str.lower() == email_to_check.strip().lower()]

    if len(match) == 1:
        attendee = match.iloc[0]
        st.subheader(f"✅ Registered: {attendee['attendee_name']}")
        st.write(f"Email: {attendee['email']}")
        st.write(f"Phone: {attendee['phone_number']}")
        st.image(attendee['qrcode_url'], width=200)

        # Check-in button
        if attendee["checkin_status"] != "Checked In":
            if st.button("Check In"):
                df.loc[df["email"].str.strip().str.lower() == email_to_check.strip().lower(), "checkin_status"] = "CHECKED IN"
                df.to_csv(CSV_FILE, index=False)
                st.success(f"{attendee['attendee_name']} has been checked in!")
        else:
            st.warning(f"{attendee['attendee_name']} is already checked in.")
    else:
        st.error("❌ Attendee not found in registration list.")

else:
    st.info("Waiting for QR scan or manual email input…")

# ----------------------------
# Optional: Show summary
# ----------------------------
st.markdown("---")
st.subheader("Check-in Summary")
checked_in = df[df["checkin_status"] == "Checked In"]
not_checked = df[df["checkin_status"] != "Checked In"]

st.write(f"✅ Checked in: {len(checked_in)}")
st.write(f"❌ Not checked in: {len(not_checked)}")
