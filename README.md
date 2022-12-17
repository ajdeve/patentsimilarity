# Patent Application Claims Text Semantic Similarity Search
### Capstone Project for University of Chicago Analytics (MSCA) Program 
Team: Ahjeong Yeom, Akhir Syabani, Han-yi Lin, Kenji Laurens 
Capstone Partner: Raytheon Technologies

<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue"><img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white"><img src="https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white"><img src="https://img.shields.io/badge/Numpy-777BB4?style=for-the-badge&logo=numpy&logoColor=white"><img src="https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white"><img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white">


An application for searching for similar patents using only claims text. The intended usage is to help applicants in their prior art search and predict whether their claims application will be rejected on the basis of non-novelty. 


<img width="729" alt="Screenshot 2022-11-28 at 4 54 03 PM" src="https://user-images.githubusercontent.com/50029982/204462467-c5cf56cb-c6be-47db-8c2c-9bc0076309e1.png">

## Citations

Sentence BERT https://github.com/UKPLab/sentence-transformers
```
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "http://arxiv.org/abs/1908.10084",
}
```

FAISS https://github.com/facebookresearch/faiss
```
@article{johnson2019billion,
  title={Billion-scale similarity search with {GPUs}},
  author={Johnson, Jeff and Douze, Matthijs and J{\'e}gou, Herv{\'e}},
  journal={IEEE Transactions on Big Data},
  volume={7},
  number={3},
  pages={535--547},
  year={2019},
  publisher={IEEE}
}
```
