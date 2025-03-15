import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Load the CSV file
csv_path = "/Users/kebbaleigh/Library/Mobile Documents/com~apple~CloudDocs/Documents/Education/DATA 304/data_wrangling_304/data/assignment_4/system_of_record_timestamps.csv"
df = pd.read_csv(csv_path)

# Function to parse timestamps
def parse_timestamp(timestamp):
    try:
        # Try parsing with multiple formats
        for fmt in ("%d-%m-%Y %H:%M", "%Y-%m-%dT%H:%M:%SZ", "%m/%d/%Y %I:%M %p", "%Y/%d/%m", "%Y-%m-%d"):
            try:
                return datetime.strptime(timestamp, fmt)
            except ValueError:
                continue
        return None  # Return None if no format matches
    except:
        return None

# Apply the function to the Primary_Timestamp column
df["Parsed_Timestamp"] = df["Primary_Timestamp"].apply(parse_timestamp)

# Drop rows with invalid timestamps
df = df.dropna(subset=["Parsed_Timestamp"])

# Sort by timestamp
df = df.sort_values("Parsed_Timestamp")

# Plot the data
plt.figure(figsize=(12, 6))
plt.plot(df["Parsed_Timestamp"], df["Event_Count"], marker="o", linestyle="-")
plt.title("Server Event Count Over Time")
plt.xlabel("Timestamp")
plt.ylabel("Event Count")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()