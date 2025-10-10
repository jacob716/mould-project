import os
import pandas as pd
from openai import OpenAI

# ========= CONFIG =========
INPUT_CSV = "reports_with_conclusions.csv"
OUTPUT_EMB = "conclusion_embeddings.csv"
MODEL = "text-embedding-3-small"
# ==========================

# Init OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load conclusions
df = pd.read_csv(INPUT_CSV)
df = df.dropna(subset=["conclusion"])             # drop NaN rows
df = df[df["conclusion"].str.strip() != ""]       # drop empty strings

# Generate embeddings
embeddings = []
for i, text in enumerate(df["conclusion"].tolist()):
    resp = client.embeddings.create(model=MODEL, input=text)
    vector = resp.data[0].embedding
    embeddings.append(vector)
    if i % 20 == 0:
        print(f"Processed {i}/{len(df)} conclusions")

# Save embeddings to CSV
emb_df = pd.DataFrame(embeddings)
emb_df.insert(0, "filename", df["filename"].values)  # keep filenames for reference
emb_df.to_csv(OUTPUT_EMB, index=False)

print(f"\n✅ Saved embeddings for {len(embeddings)} conclusions → {OUTPUT_EMB}")
