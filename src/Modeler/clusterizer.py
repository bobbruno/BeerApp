'''
Created on 14/10/2014

@author: bobbruno
'''

from bokeh.server.server_backends import dataset
from sklearn.cluster import MeanShift, KMeans, AffinityPropagation, MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.feature_selection import chi2, SelectKBest, f_classif
from sklearn.grid_search import GridSearchCV, ParameterGrid
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelBinarizer, Imputer, PolynomialFeatures, StandardScaler


def cluster(dataset):
    estimators = [
            ('dummyfier', LabelBinarizer(neg_label, pos_label, sparse_output))
            ('scale_predictors', StandardScaler()),
            #  ('feature_selector', LinearSVC(penalty='l1', dual=False)),
            #  ('feature_selector', SelectKBest(score_func=f_classif)),
            #  ('linearSVC', LinearSVC())
            ('randomforests', RandomForestClassifier())
            ]
    clf = Pipeline(estimators)
    params = dict(
            #  linearSVC__C=[0.1, 1, 10],
            randomforests__max_depth=[5, 10, None],
            randomforests__n_estimators=[10, 50, 100, 1000],
            #  feature_selector__C=[0.1, 1, 10]
            #  feature_selector__score_func=[chi2],
            #  feature_selector__k=[5, 10, 'all']
            )
    if(X_holdout != None and y_holdout != None):
        grid_search = GridSearchCV(clf, param_grid=params, cv=cv_custom, scoring='roc_auc', n_jobs=6)
    else:
        grid_search = GridSearchCV(clf, param_grid=params, scoring='roc_auc', n_jobs=6)
    grid_search.fit(X, y)
    return grid_search


if __name__ == '__main__':
    pass
