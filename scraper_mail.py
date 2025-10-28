import os
import re
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

# Step 1: Scrape data
url = "https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
response = requests.get(url, headers=headers)
html = response.text
soup = BeautifulSoup(html, "lxml")

# Step 2: Find the correct table
table = soup.find("figure", class_="is-style-regular")

rows = []
for tr in table.find_all("tr"):
    cells = []
    for td in tr.find_all(["td", "th"]):  # include headers too
        text = td.text.strip() if td.text.strip() else ""  # handle empty cells
        cells.append(text)
    if cells:  # avoid appending empty rows
        rows.append(cells)

# Step 3: Sort the table by the 4th column
def extract_number(x):
    digits = re.sub(r"[^\d.]", "", str(x))
    return float(digits) if digits else 0

sorted_data = sorted(rows, key=lambda x: extract_number(x[3]), reverse=True)

# Step 4: Filter and format data
data = ''
for x in sorted_data:
    if len(x) > 3 and '%' in x[3]:
        data += f"{x[0]}\t{x[3]}\n"
    else:
        break

if not data:
    data = "No valid data found."

# Step 5: Email setup
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", SENDER_EMAIL)

if not (SENDER_EMAIL and APP_PASSWORD):
    raise SystemExit("❌ Missing required environment variables for email.")

# Step 6: Send email
msg = MIMEText(data)
msg["Subject"] = "Daily IPO GMP Report"
msg["From"] = SENDER_EMAIL
msg["To"] = RECEIVER_EMAIL

with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
    server.starttls()
    server.login(SENDER_EMAIL, APP_PASSWORD)
    server.send_message(msg)

print("✅ Email sent successfully!")
