import datetime
import os
import sqlite3
import time

import faiss
import plotly.express as px
from plotly.graph_objects import Figure
import numpy as np
import pandas as pd
import streamlit as st
import torch
from scipy.stats import norm
from sentence_transformers import SentenceTransformer


def similarity_search(
    index: faiss.IndexFlat, model: SentenceTransformer, in_text: str, normalize: bool,
) -> tuple[list, list]:
    encoded = encode_text(model, in_text, normalize)
    scores, idx = search(index, encoded)

    return scores, idx


@st.cache
def encode_text(model: SentenceTransformer, text: str, normalize: bool) -> np.array:
    out = np.array([model.encode(text)]).astype(np.float32)
    if normalize:
        faiss.normalize_L2(out)

    return out


def search(
    index: faiss.IndexFlat, encoding: np.array, k: int = 50000
) -> tuple[np.array, np.array]:
    score, idx = index.search(encoding, k)

    return score[0], (idx[0] + 1)  # SQLite Index Starts From 1, FAISS Index starts at 0


def get_patent_info(
    db: sqlite3.Connection,
    scores: list[int],
    idx: list[int],
    date_lower: datetime.datetime,
    date_upper: datetime.datetime,
    cpcs: str,
    sep: str,
    topk: int,
    rejected: pd.DataFrame,
) -> pd.DataFrame:

    q = f"""
        SELECT p.patent_id, p.patent_date, p.patent_title, p.cpc_group, c.claim_text, p.rowid
        FROM patents AS p, claims AS c
        WHERE
            p.patent_id = c.patent_id
        AND
            p.rowid IN {tuple(idx)} 
        AND
            p.patent_date >= "{date_lower}"
        AND
            p.patent_date <= "{date_upper}"
        """
    if cpcs.strip():
        q += "AND (p.cpc_group LIKE "
        sep += " p.cpc_group LIKE "
        q += f"""{ sep.join(['"%'+cpc.strip()+'%" ' for cpc in cpcs.split(",")])} )"""

    df = pd.read_sql(q, db)
    ordered_score = pd.DataFrame(scores, idx, columns=["score"])
    df = df.merge(ordered_score, left_on="rowid", right_index=True).sort_values(
        "score", ascending=False
    )
    mu = rejected["sim"].mean()
    sigma = rejected["sim"].std()
    df["rej"] = df["score"].apply(lambda x: norm.cdf(x, mu, sigma))
    df[["score", "rej"]] = df[["score", "rej"]].round(3)
    df.drop("rowid", axis=1, inplace=True)
    df.columns = [
        "Patent ID",
        "Date",
        "Title",
        "CPC IDs",
        "Claims Text",
        "Score",
        "Rejection Probability",
    ]

    return df.head(topk).reset_index(drop=True)


def get_probability_plot(df: pd.DataFrame, rejected: pd.DataFrame) -> Figure:
    fig = px.ecdf(rejected["sim"], labels={"value": "Similarity Score"})
    fig.add_scatter(x=[df.at[0, "Score"]], y=[df.at[0, "Rejection Probability"]])
    fig.update_layout(showlegend=False)
    return fig


os.chdir(os.path.abspath(os.path.dirname(__file__)))

st.title("Patent Application Claims Text Semantic Similarity Search")


indexes = os.listdir("./indexes")
dbs = [x for x in os.listdir("./data") if x.endswith(".db")]
models = ["AI-Growth-Lab/PatentSBERTa"]

with st.form("search"):
    db_select = st.selectbox("Select Database", dbs)
    col1, col2 = st.columns(2)
    with col1:
        index_select = st.selectbox("Select Index", indexes)
        date_lower = st.date_input(
            "Oldest Patent Date",
            value=datetime.date(2011, 1, 1),
            min_value=datetime.date(2011, 1, 1),
        )
    with col2:
        model_select = st.selectbox("Select Model", models)
        date_upper = st.date_input(
            "Latest Patent Date",
            value=datetime.datetime.now(),
            max_value=datetime.datetime.now(),
        )

    col3, col4 = st.columns([4, 1])
    with col3:
        cpcs = st.text_input("Comma Separated CPC Class")
    with col4:
        sep = st.selectbox("Search Clause", ["AND", "OR"])

    with st.expander("CPC Filter Help", False):
        st.write(
            'Example: "G01S17/10, G01S17/58, G01S7/4865" will filter patents if they belong to these classes. Do not use quotations. Use the clause on the right to specify if patents should belong to all or at least one class.',
        )

    topk = st.slider("Max Return Count", min_value=1, max_value=1000, value=100)
    in_text = st.text_area("Claim Text")

    submitted = st.form_submit_button("Run Similarity Search")
    progress = st.progress(0)

    if submitted:
        progress.progress(1)
        start = time.time()
        db = sqlite3.connect(f"./data/{db_select}")
        index = faiss.read_index(f"./indexes/{index_select}")
        progress.progress(20)
        normalize = "norm" in index_select
        device = (
            "cuda"  # GPU
            if torch.cuda.is_available()
            else "mps"  # Apple Silicon
            if torch.backends.mps.is_available()
            else None
        )
        model = SentenceTransformer(model_select, device=device)
        progress.progress(50)
        rejected = pd.read_csv("./data/rejected_scoring.tsv", sep="\t", usecols=["sim"])
        progress.progress(60)
        scores, idx = similarity_search(index, model, in_text, normalize)
        progress.progress(70)
        df = get_patent_info(
            db, scores, idx, date_lower, date_upper, cpcs, sep, topk, rejected
        )
        progress.progress(95)
        st.dataframe(
            df.style.format({"Score": "{:.3f}", "Rejection Probability": "{:.3f}"})
        )
        progress.progress(100)
        end = time.time()
        st.caption(
            f"Retrieved {len(df)} records in {round(end - start, 3)} seconds using {model.device.type}."
        )

        with st.expander("Probability of Rejection", False):
            st.plotly_chart(
                get_probability_plot(df, rejected), use_container_width=True
            )
            st.caption(
                "Probability of rejection on basis of non-novelty is based on the highest similarity score and past rejections."
            )

if submitted:
    st.download_button(
        "Download file to csv", df.to_csv(index=False), file_name="sim_search.csv"
    )
