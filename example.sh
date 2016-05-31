#!/bin/bash

# This example downloads the English fiction embeddings and tests the
# performance of the 1990s embeddings on the Bruni MEN similarity tast

mkdir embeddings
cd embeddings
curl -o eng-fiction-all.zip http://snap.stanford.edu/historical_embeddings/eng-fiction-all_sgns.zip
unzip eng-fiction-all.zip
mv sgns eng-fiction-all_sgns
cd ..
python -m vecanalysis.ws_eval embeddings/eng-fiction-all_sgns/1990 vecanalysis/simtestsets/ws/bruni_men.txt --type SGNS
