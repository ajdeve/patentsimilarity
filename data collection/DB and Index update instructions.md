# Instructions for downloading and updating database and FAISS index
Steps:
1. Download all files to data folder
2. Process downloaded into one SQLite database
3. Encode claims text to numpy array and create FAISS index

## 1. Download all files to data folder
- #### Simply run "Data Downloader.py" or alternatively:
- To start, create a folder for all downloaded data
- Go to https://patentsview.org/download/data-download-tables
- Download the following files:
    - `g_patent` (https://s3.amazonaws.com/data.patentsview.org/download/g_patent.tsv.zip)
        - Contains basic patent information
    - `g_cpc_current` (https://s3.amazonaws.com/data.patentsview.org/download/g_cpc_current.tsv.zip)
        - Contains CPC information for all patents
- Next, download Claims text files by year at https://patentsview.org/download/claims
    - Choose and download all years necessary 
    - These files contains the Claims text for patents 
- Files do NOT need to be unzipped in the interest of saving space, though processing may be slower overall. 
## 2. Process downloaded into one SQLite database
> :warning: **Column names may change since initial processing**: You may need to adjust scripts accordingly!
- Use the "File Processor.py" file  to process all files and create SQL db.
- Note that file names and directory may need adjustment.

## 3. Encode claims text to numpy array and create FAISS index
> It is highly recommended to run this on GPU, which will still take hours. Check if your machine has GPU available and is compatible with CUDA and PyTorch.
- Run the "FAISS Index Generator.py" file to create a FAISS index. By default, this will create a normalized Flat Inner Product index. Without a normalized inner product, the output score will not be cosine similarity.

# Files and Directory Structure
```
.
├── streamlit app/
│   ├── data/
│   │   ├── all_patents.db  # Or other db name
│   │   └── rejected_scoring.tsv 
│   ├── indexes/
│   │   ├── faiss_flat_index
│   │   └── faiss_ip_norm_index # Or other FAISS Index
│   └── app.py
└── data collection/
    ├── data/
    │   ├── g_cpc_current.tsv.zip
    │   ├── g_patent.tsv.zip
    │   ├── g_claims_2022.tsv.zip
    │   └── ...  # Claims files for other years
    ├── Data Downloader.py
    ├── File Processor.py
    └── FAISS Index Generator.py
```    