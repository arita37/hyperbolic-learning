# simple wrapper for gensim's poincare model
# source: https://github.com/RaRe-Technologies/gensim/blob/develop/gensim/models/poincare.py

# import libraries
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report
from sklearn.model_selection import train_test_split, ShuffleSplit, KFold
from gensim.models.poincare import PoincareModel, PoincareRelations
import logging
logging.basicConfig(level=logging.INFO)

def train_embeddings(input_path, # path to input edge relations
                     delimiter, # input file delim
                     output_path, # path to output embedding vectors 
                     size=2, # embed dimension
                     alpha=0.1, # learning rate
                     burn_in=10, # burn in train rounds
                     burn_in_alpha=0.01, # burn in learning rate
                     workers=1, # number of training threads used
                     negative=10, # negative sample size
                     epochs=100, # training rounds
                     print_every=500, # print train info
                     batch_size=10): # num samples in batch
    
    # load file with edge relations between entities
    relations = PoincareRelations(file_path=input_path, delimiter=delimiter)
    
    # train model
    model = PoincareModel(train_data=relations, size=size, alpha=alpha, burn_in=burn_in,
                          burn_in_alpha=burn_in_alpha, workers=workers, negative=negative)
    model.train(epochs=epochs, print_every=print_every,batch_size=batch_size)
    
    # save output vectors
    model.kv.save_word2vec_format(output_path)
    
    return

def load_embeddings(file_path, delim=' '):
    # load pre-trained embedding coordinates
    emb = pd.read_table(file_path, delimiter=' ')
    emb = emb.reset_index()
    emb.columns = ['node', 'x', 'y']
    return emb

# K-fold cross validation
def evaluate_model(model, X, y, max_epochs=10, cv=5, report=True):
    if report:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
        model.fit(X_train, y_train, max_epochs=max_epochs)
        y_pred = np.argmax(model.predict(X_test), axis=1)
        print(classification_report(y_test, y_pred))
    kf = KFold(n_splits=cv)
    cv_scores = []
    for train, test in kf.split(X):
        model.fit(X[train], y[train], max_epochs=max_epochs)
        y_pred = np.argmax(model.predict(X[test]), axis=1)
        cv_scores.append(f1_score(y[test], y_pred, average='macro'))
    return cv_scores