import streamlit as st
import pandas as pd
from pyzbar.pyzbar import decode
from PIL import Image

# ----------------------------
# Load participants CSV
# ----------------------------
CSV_FILE = "participants.csv"

try:
    df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    st.error(f"CSV file '{CSV_FILE}' not found!")
    st.stop()

# Ensure checkin_status column exists
if "checkin_status" not in df.columns:
    df["checkin_status"] = "NOT CHECKED IN"

# ----------------------------
# App Title
# ----------------------------
st.title("Event Check-In App")
st.write("Scan the QR code or enter email manually to verify registration.")

# ----------------------------
# Camera QR Scanner
# ----------------------------
st.subheader("📷 Scan QR Code")
img_file = st.camera_input("Point your camera at the attendee's QR code")

scanned_email = None

if img_file is not None:
    img = Image.open(img_file)
    decoded_objects = decode(img)
    
    if decoded_objects:
        scanned_email = decoded_objects[0].data.decode("utf-8").strip()
        st.success(f"Scanned: {scanned_email}")
    else:
        st.error("No QR code detected. Try again!")

# ----------------------------
# Manual email input (backup)
# ----------------------------
st.subheader("Or Enter Email Manually")
manual_email = st.text_input("Enter attendee email:")
email_to_check = scanned_email if scanned_email else manual_email

# ----------------------------
# Lookup and Check-in Logic
# ----------------------------
if email_to_check:
    match = df[df["email"].str.strip().str.lower() == email_to_check.strip().lower()]
    
    if len(match) == 1:
        attendee = match.iloc[0]
        st.subheader(f"✅ Registered: {attendee['attendee_name']}")
        st.write(f"Email: {attendee['email']}")
        st.write(f"Phone: {attendee['phone_number']}")
        if "qr_code" in attendee and pd.notna(attendee["qr_code"]):
            st.image(attendee["qr_code"], width=200)
        
        if attendee["checkin_status"] != "CHECKED IN":
            if st.button("Check In"):
                df.loc[df["email"].str.strip().str.lower() == email_to_check.strip().lower(), "checkin_status"] = "CHECKED IN"
                df.to_csv(CSV_FILE, index=False)
                st.success(f"{attendee['attendee_name']} has been checked in!")
        else:
            st.warning(f"{attendee['attendee_name']} is already checked in.")
    else:
        st.error("❌ Attendee not found in registration list.")

# ----------------------------
# Check-in Summary Panel
# ----------------------------
st.markdown("---")
st.subheader("Check-in Summary")
checked_in = df[df["checkin_status"] == "CHECKED IN"]
not_checked = df[df["checkin_status"] != "CHECKED IN"]

st.write(f"✅ Checked in: {len(checked_in)}")
st.write(f"❌ Not checked in: {len(not_checked)}")
