import json
import pandas as pd

# 1. Load JSON file
with open("dataset/interactions.json", "r") as f:
    data = json.load(f)

# 2. Convert to table format
df = pd.DataFrame(data)

# 3. Keep only required columns
df = df[["user_id", "book_id", "rating"]]

# 4. Save as CSV (Surprise uses this easily)
df.to_csv("dataset/interactions.csv", index=False)

print(df.head())
print("Data converted successfully")
