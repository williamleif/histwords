#Word Embeddings for Historical Text

### Author: William Hamilton (wleif@stanford.edu)

## Overview 

** NOTE: this is research code that is currently undergoing some restructuring. Please email if you have issues and be warned that things will be changing over the coming days

This code base contains an eclectic collection of tools for analyzing historical language change using vector space semantics.
Links to pre-trained historical word vectors will be released soon (please email me if you need these asap)!!
The structure of the code (in terms of folder organization) is as follows:

* `googlengram` contains code for pulling and processing historical Google N-Gram Data (http://storage.googleapis.com/books/ngrams/books/datasetsv2.html).
* `coha` contains code for pulling and processing historical data from the COHA corpus (http://corpus.byu.edu/coha/).
* `statutils` contains helper code for common statistical tasks.
* `representations` contains code that provides a high-level interface to (historical) word vectors and is originally based upon Omar Levy's hyperwords package (https://bitbucket.org/omerlevy/hyperwords).
* `sgns` contains a modified version of Google's word2vec code (https://code.google.com/archive/p/word2vec/)

<!--- * `notebooks` contains notebooks useful for replicating my published results-->

<!--- *See REPLICATION.md for detailed instructions on how to replicate specific published/submitted results.-->

## Dependencies

Core dependencies:
  * python 2.7
  * sklearn: http://scikit-learn.org/stable/
  * cython: http://docs.cython.org/src/quickstart/install.html
  * statsmodels: http://statsmodels.sourceforge.net/

You will also need Juptyer/IPython to run any IPython notebooks.
