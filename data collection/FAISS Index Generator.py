import os
import sqlite3

import faiss
import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm

tqdm.pandas()

os.chdir(os.path.abspath(os.path.dirname(__file__)))

gpu_available = torch.cuda.is_available()
device = (
    "cuda"  ## GPU
    if gpu_available
    else "mps"  ## Apple Silicon
    if torch.backends.mps.is_available()
    else None
)
print(f"Running model on {device}")
model = SentenceTransformer("AI-Growth-Lab/PatentSBERTa", device=device)

con = sqlite3.connect("../streamlit app/data/all_patents.db")
cur = con.cursor()

cs = 100000
table = pd.read_sql("SELECT * FROM claims", con, chunksize=cs)
total = pd.read_sql("SELECT COUNT(*) as c FROM claims", con).at[0, "c"]
chunks = []
print(f"Encoding {total} texts.")
for chunk in tqdm(table, total=(total // cs + 1)):
    encoded_chunk = model.encode(chunk["claim_text"].to_list(), show_progress_bar=True, batch_size=256)
    chunks.extend(encoded_chunk)

embs = np.asarray(chunks)

## Saving embeddings as checkpoint
## With this numpy file, different indexes can be created without re-encoding texts again.
print("Saving encoded numpy array.")
np.save("embs.npy", embs)

## Build a flat (CPU) index
# embs = np.load("embs.npy", allow_pickle=True)  ## Uncomment to load encoded numpy array
print("Building FAISS Index.")
dimensions = embs.shape[1]
index_flat = faiss.index_factory(dimensions, "Flat", faiss.METRIC_INNER_PRODUCT)

if gpu_available:
    ## Make it into a GPU index
    res = faiss.StandardGpuResources()
    index_flat = faiss.index_cpu_to_gpu(res, 0, index_flat)

print("Normalizing array.")
faiss.normalize_L2(embs)

print("Populating Index.")
index_flat.add(embs)

os.chdir("data")
index_name = "faiss_ip_norm_index"
print(f"Saving Index as {index_name}.")
if gpu_available:
    faiss.write_index(faiss.index_gpu_to_cpu(index_flat), index_name)
else:
    faiss.write_index(index_flat, index_name)
