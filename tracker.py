import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import requests
from bs4 import BeautifulSoup

GOV_URL = "https://www.gov.uk/government/publications/regulatory-judgements-and-enforcement-notices"
CSV_PATH = "data.csv"


def get_latest_data():
  page = requests.get(GOV_URL).text
  soup = BeautifulSoup(page, "html.parser")
  file_url = next(
      a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".xlsx")
  )

  df = pd.read_excel(file_url, sheet_name="Regulatory Judgements")
  cols = [
      "Reg Code",
      "Landlord",
      "Governance Grade",
      "Viability Grade",
      "Consumer grade",
      "Publication Date",
  ]
  df = df[[c for c in cols if c in df.columns]].fillna("-").astype(str)
  df["Publication Date"] = df["Publication Date"].str.split(" ").str[0]
  return df


def send_alert(changes):
  msg = MIMEMultipart()
  msg["From"] = os.environ["EMAIL_USER"]
  msg["To"] = os.environ["EMAIL_TO"]
  msg["Subject"] = "🚨 RSH Regulatory Judgements Update"

  html = "<h3>New RSH Updates Detected</h3><ul>"
  for item in changes:
    html += f"<li>{item}</li>"
  html += "</ul>"
  msg.attach(MIMEText(html, "html"))

  with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
    server.send_message(msg)


def main():
  new_df = get_latest_data()
  changes = []

  if os.path.exists(CSV_PATH):
    old_df = pd.read_csv(CSV_PATH, dtype=str).fillna("-")
    for _, row in new_df.iterrows():
      old_row = old_df[old_df["Reg Code"] == row["Reg Code"]]
      if old_row.empty:
        changes.append(
            f"<b>Added:</b> {row['Landlord']} (G:{row['Governance Grade']}, V:{row['Viability Grade']}, C:{row['Consumer grade']})"
        )
      else:
        diffs = [
            f"{g}: {old_row.iloc[0][g]} → {row[g]}"
            for g in ["Governance Grade", "Viability Grade", "Consumer grade"]
            if row[g] != old_row.iloc[0][g]
        ]
        if diffs:
          changes.append(f"<b>Changed:</b> {row['Landlord']} ({', '.join(diffs)})")

    for _, row in old_df.iterrows():
      if new_df[new_df["Reg Code"] == row["Reg Code"]].empty:
        changes.append(f"<b>Removed:</b> {row['Landlord']}")

  new_df.to_csv(CSV_PATH, index=False)

  if changes:
    send_alert(changes)


if __name__ == "__main__":
  main()
