import os

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

os.chdir(os.path.abspath(os.path.dirname(__file__)))
os.makedirs("data", exist_ok=True)
os.chdir("data")


def download(url: str, path: str) -> None:
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024  ## 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)
    if os.path.isfile(path) and os.path.getsize(path) >= total_size_in_bytes:
        print("File", path, "exists. Skipping download.")
        return
    with open(path, "wb") as file:
        print("Downloading", path)
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")


## Download Patent Info
download(
    "https://s3.amazonaws.com/data.patentsview.org/download/g_patent.tsv.zip",
    "g_patent.tsv.zip",
)

## Download CPC Info
download(
    "https://s3.amazonaws.com/data.patentsview.org/download/g_cpc_current.tsv.zip",
    "g_cpc_current.tsv.zip",
)


## Download Patent Claims
page = requests.get("https://patentsview.org/download/claims")
soup = BeautifulSoup(page.text, "html.parser")
for a in tqdm(soup.select("a[href*=zip]")):
    url = a.get("href")
    filename = a.get("href").split("/")[-1]

    download(url, filename)
