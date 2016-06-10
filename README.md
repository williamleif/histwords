#Word Embeddings for Historical Text

### Author: William Hamilton (wleif@stanford.edu)
### [Project Website](http://nlp.stanford.edu/projects/histwords)

## Overview 

An eclectic collection of tools for analyzing historical language change using vector space semantics.

![alt text](https://github.com/williamleif/historical-embeddings/raw/master/wordpaths.png "Two-dimensional projections of some semantic changes computed using the English SGNS vectors.")

## Pre-trained historical embeddings

Various embeddings (for many languages and using different embeddings approaches are available on the [project website](http://nlp.stanford.edu/projects/histwords).

Some pre-trained word2vec (i.e., SGNS) historical word vectors for multiple languages (constructed via Google N-grams) are also available here:
* [All English (eng-all)](http://snap.stanford.edu/historical_embeddings/eng-all_sgns.zip) 
* [English fiction (eng-fiction-all)](http://snap.stanford.edu/historical_embeddings/eng-fiction-all_sgns.zip) 
* [French (fre-all)](http://snap.stanford.edu/historical_embeddings/fre-all_sgns.zip) 
* [German (ger-all)](http://snap.stanford.edu/historical_embeddings/ger-all_sgns.zip) 
* [Chinese (chi-sim-all)](http://snap.stanford.edu/historical_embeddings/chi-sim-all_sgns.zip) 

All except Chinese contain embeddings for the decades in the range 1800s-1990s (2000s are excluded because of sampling changes in the N-grams corpus).
The Chinese data starts in 1950.

Embeddings constructed using the Corpus of Historical American English (COHA) are also available:
* [Raw words (coha-word)](http://snap.stanford.edu/historical_embeddings/coha-word_sgns.zip) 
* [Word lemmas (coha-lemma)](http://snap.stanford.edu/historical_embeddings/coha-lemma_sgns.zip) 

`example.sh` contains an example run, showing how to download and use the embeddings.
`example.py` shows how to use the vector representations in the Python code (assuming you have already run the `example.sh` script.)

[This paper](http://arxiv.org/abs/1605.09096) describes how the embeddings were constructed.
If you make use of these embeddings in your research, please cite the following:

@inproceedings{hamilton_diachronic_2016,
  title = {Diachronic {Word} {Embeddings} {Reveal} {Statistical} {Laws} of {Semantic} {Change}},
  url = {http://arxiv.org/abs/1605.09096},
  booktitle = {Proc. {Assoc}. {Comput}. {Ling}. ({ACL})},
  author = {Hamilton, William L. and Leskovec, Jure and Jurafsky, Dan},
  year = {2016}
}


## Code organization

The structure of the code (in terms of folder organization) is as follows:

Main folder for using historical embeddings:
* `representations` contains code that provides a high-level interface to (historical) word vectors and is originally based upon Omar Levy's hyperwords package (https://bitbucket.org/omerlevy/hyperwords).

Folders with pre-processing code and active research code (potentially unstable):
* `googlengram` contains code for pulling and processing historical Google N-Gram Data (http://storage.googleapis.com/books/ngrams/books/datasetsv2.html).
* `coha` contains code for pulling and processing historical data from the COHA corpus (http://corpus.byu.edu/coha/).
* `statutils` contains helper code for common statistical tasks.
* `vecanalysis` contains code for evaluating and analyzing historical word vectors.
* `sgns` contains a modified version of Google's word2vec code (https://code.google.com/archive/p/word2vec/)

`statistical-laws.ipynb` contains an IPython notebook with the main code necessary for replicating the key results of our [published work](http://arxiv.org/abs/1605.09096).

`example.py` shows how to compute the simlarity series for two words over time, which is how we evaluated different methods against the attested semantic shifts listed in our paper. 

<!--- * `notebooks` contains notebooks useful for replicating my published results-->

<!--- *See REPLICATION.md for detailed instructions on how to replicate specific published/submitted results.-->

## Dependencies

Core dependencies:
  * python 2.7
  * sklearn: http://scikit-learn.org/stable/
  * cython: http://docs.cython.org/src/quickstart/install.html
  * statsmodels: http://statsmodels.sourceforge.net/

You will also need Juptyer/IPython to run any IPython notebooks.
