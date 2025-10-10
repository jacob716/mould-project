import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

# ========= CONFIG =========
INPUT_EMB = "conclusion_embeddings.csv"   # from your embedding script
INPUT_CSV = "reports_with_conclusions.csv" # original CSV with text
OUTPUT_CSV = "clustered_conclusions.csv"
N_CLUSTERS = 4                           # tweak this (try 3–6)
# ==========================

# Load embeddings
emb_df = pd.read_csv(INPUT_EMB)

# Drop the filename column to get pure vectors
X = emb_df.drop(columns=["filename"]).values

# Run KMeans
kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42)
labels = kmeans.fit_predict(X)

# Load original conclusions (to interpret clusters)
text_df = pd.read_csv(INPUT_CSV)
text_df = text_df.dropna(subset=["conclusion"])
text_df = text_df[text_df["conclusion"].str.strip() != ""]

# Add cluster labels
text_df["cluster"] = labels

# Evaluate clustering
if len(set(labels)) > 1:  # silhouette needs at least 2 clusters
    score = silhouette_score(X, labels)
    print(f"Silhouette score = {score:.3f}")

# Interpret clusters with TF-IDF keywords
def extract_keywords(texts, top_n=10):
    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
    X = vectorizer.fit_transform(texts)
    indices = X.sum(axis=0).A1.argsort()[::-1][:top_n]
    return [vectorizer.get_feature_names_out()[i] for i in indices]

for cluster_id in sorted(text_df["cluster"].unique()):
    cluster_texts = text_df[text_df.cluster == cluster_id]["conclusion"].tolist()
    keywords = extract_keywords(cluster_texts)
    print(f"\nCluster {cluster_id} — {len(cluster_texts)} conclusions")
    print("Top keywords:", keywords)

# Save results
text_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
print(f"\n✅ Clustering complete. Results saved to {OUTPUT_CSV}")
