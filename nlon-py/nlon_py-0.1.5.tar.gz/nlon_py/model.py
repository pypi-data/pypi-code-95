"""Machine learning models for nlon-py."""
from time import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
# explicitly require this experimental feature
from sklearn.experimental import enable_halving_search_cv
from sklearn.feature_selection import SelectKBest, chi2, f_classif
from sklearn.metrics import (ConfusionMatrixDisplay, auc,
                             classification_report, confusion_matrix, f1_score,
                             plot_roc_curve, roc_auc_score, roc_curve)
from sklearn.model_selection import (HalvingGridSearchCV,
                                     StratifiedShuffleSplit, cross_val_score,
                                     cross_validate, train_test_split)
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from glmnet import LogitNet
from nlon_py.data.make_data import get_category_dict
from nlon_py.features import NLoNFeatures

names = ["Naive Bayes", "Nearest Neighbors", "SVM", "glmnet"]

classifiers = [GaussianNB(),
               KNeighborsClassifier(),
               SVC(kernel='rbf', gamma=0.01, C=10, probability=True, random_state=0),
               LogitNet()]

dict_name_classifier = dict(zip(names, classifiers))


def NLoNModel(X, y, features='C3_FE', model_name='SVM', stand=True, kbest=True, n_classes=7):
    if model_name in dict_name_classifier:
        clf = dict_name_classifier[model_name]
    else:
        raise RuntimeError('Param model_name should be in ' + names.__str__())
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.4, random_state=0, stratify=y)

    pipeline_steps = []
    if stand:
        stand_scaler = StandardScaler()
        pipeline_steps.append(('standardscaler', stand_scaler))
    if kbest:
        anova_filter = SelectKBest(f_classif, k=100)
        pipeline_steps.append(('selectkbest', anova_filter))
    pipeline_steps.append(('clf', clf))
    nlon_clf = Pipeline(steps=pipeline_steps)

    X_train = NLoNFeatures.fit_transform(X_train, feature_type=features)
    nlon_clf.fit(X_train, y_train)
    X_test = NLoNFeatures.transform(X_test, feature_type=features)
    score = nlon_clf.score(X_test, y_test)
    y_pred = nlon_clf.predict(X_test)
    y_score = nlon_clf.predict_proba(X_test)
    f1 = f1_score(y_test, y_pred, average='weighted')
    auc = roc_auc_score(y_test, y_score, multi_class='ovr')
    print(f'{model_name}: {score:.2f} accuracy')
    print(f'F1: {f1:.3f}, AUC: {auc:.3f}')
    if n_classes > 2:
        plot_multiclass_roc(nlon_clf, X_test, y_test, n_classes)
    else:
        plot_twoclass_roc(nlon_clf, X, y, cv=10)
    plot_confusion_matrix(y_test, y_pred, n_classes)
    return nlon_clf


def SearchParams_SVM(X, y):
    C_range = [0.01, 0.1, 1, 10, 100]
    Gamma = [1e-2, 1e-3, 1e-4]
    param_grid = [{'svc__kernel': ['rbf'], 'svc__gamma': Gamma, 'svc__C': C_range},
                  {'svc__kernel': ['linear'], 'svc__C': C_range}]
    stand_scaler = StandardScaler()
    anova_filter = SelectKBest(f_classif, k=100)
    clf = SVC(probability=True)
    svm_pipeline = make_pipeline(stand_scaler, anova_filter, clf)
    search = HalvingGridSearchCV(
        svm_pipeline, param_grid, random_state=0, scoring='roc_auc_ovr')

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.4, random_state=0)
    X_train = NLoNFeatures.fit_transform(X_train)
    search.fit(X_train, y_train)
    print("Best parameters set found on development set:")
    print(search.best_params_)
    print()
    print("Details of parameters:")
    means = search.cv_results_['mean_test_score']
    stds = search.cv_results_['std_test_score']
    for mean, std, params in zip(means, stds, search.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r"
              % (mean, std * 2, params))
    X_test = NLoNFeatures.transform(X_test)
    y_pred = search.predict(X_test)
    y_score = search.predict_proba(X_test)
    f1 = f1_score(y_test, y_pred, average='weighted')
    auc = roc_auc_score(y_test, y_score, multi_class='ovr')
    print(
        f'Best parameters {search.best_params_} with AUC {auc:.3f}, F1 {f1:.3f}')


def CompareModels(X, y, cv=None):
    anova_filter = SelectKBest(f_classif, k=100)
    if cv is None:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.4, random_state=0)
        X_train = NLoNFeatures.fit_transform(X_train)
        X_test = NLoNFeatures.transform(X_test)
        for key, clf in dict_name_classifier.items():
            nlon_clf = make_pipeline(anova_filter, clf)
            t0 = time()
            print(f'{key} start...')
            nlon_clf.fit(X_train, y_train)
            print(f'{key} train done in {(time() - t0):0.3f}s')
            y_pred = nlon_clf.predict(X_test)
            y_score = nlon_clf.predict_proba(X_test)
            f1 = f1_score(y_test, y_pred, average='weighted')
            auc = roc_auc_score(y_test, y_score, multi_class='ovr')
            print(f"{key} test done in {(time() - t0):0.3f}s")
            print(f'{key}: AUC {auc:.3f}, F1 {f1:.3f}')
            print()
    else:
        X = NLoNFeatures.transform(X)
        for key, clf in dict_name_classifier.items():
            nlon_clf = make_pipeline(anova_filter, clf)
            scores = cross_validate(
                nlon_clf, X, y, cv=cv, scoring=('roc_auc_ovr', 'f1_micro'))
            auc = scores['test_roc_auc_ovr']
            f1 = scores['test_f1_micro']
            fit_time = scores['fit_time']
            score_time = scores['score_time']
            print()
            print(f'{key}')
            print(f'AUC: mean {auc.mean():.3f}, std {auc.std():.3f}')
            print(f'F1: mean {f1.mean():.3f}, std {f1.std():.3f}')
            print(
                f'Fit time: {fit_time.mean():.3f}, Score time: {score_time.mean():.3f}')
            print()


def ValidateModel(model, X, y):
    X = NLoNFeatures.transform(X)
    scores = cross_validate(
        model, X, y, cv=10, scoring=('roc_auc_ovr', 'f1_micro'))
    auc = scores['test_roc_auc_ovr']
    f1 = scores['test_f1_micro']
    print('10-fold cross-validation')
    print(f'AUC: mean {auc.mean():.3f}, std {auc.std():.3f}')
    print(f'F1: mean {f1.mean():.3f}, std {f1.std():.3f}')


def NLoNPredict(clf, X, features='C3_FE'):
    result = clf.predict(NLoNFeatures.transform(X, feature_type=features))
    category_dict = get_category_dict()
    result = np.vectorize(category_dict.get)(result)
    return list(result)


def plot_multiclass_roc(clf, X_test, y_test, n_classes, figsize=(11, 7)):
    y_score = clf.decision_function(X_test)
    # structures
    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    # calculate dummies once
    y_test_dummies = pd.get_dummies(y_test, drop_first=False).values
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test_dummies[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # roc for each class
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot([0, 1], [0, 1], 'k--')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('Receiver operating characteristic (ROC)')
    category_dict = get_category_dict()
    for i in range(n_classes):
        ax.plot(
            fpr[i], tpr[i], label=f'ROC curve (AUC = {roc_auc[i]:.2f}) for label {category_dict[i+1]}')
    ax.legend(loc="best")
    ax.grid(alpha=.4)
    sns.despine()
    plt.show()
    plt.savefig('roc_curve_multi.png')


def plot_twoclass_roc(clf, X, y, cv=None):
    if cv is None:
        plot_roc_curve(clf, X, y, name='NLoN for two class')
        plt.show()
        plt.savefig('roc_curve.png')
    else:
        cv = StratifiedShuffleSplit(n_splits=cv, random_state=0)
        tprs = []
        aucs = []
        mean_fpr = np.linspace(0, 1, 100)
        fig, ax = plt.subplots()
        for i, (train_index, test_index) in enumerate(cv.split(X, y)):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            clf.fit(X_train, y_train)
            viz = plot_roc_curve(
                clf, X_test, y_test, name='ROC fold {}'.format(i), alpha=0.3, lw=1, ax=ax)
            interp_tpr = np.interp(mean_fpr, viz.fpr, viz.tpr)
            interp_tpr[0] = 0.0
            tprs.append(interp_tpr)
            aucs.append(viz.roc_auc)
        ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r',
                label='Chance', alpha=.8)

        mean_tpr = np.mean(tprs, axis=0)
        mean_tpr[-1] = 1.0
        mean_auc = auc(mean_fpr, mean_tpr)
        std_auc = np.std(aucs)
        ax.plot(mean_fpr, mean_tpr, color='b',
                label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (
                    mean_auc, std_auc),
                lw=2, alpha=.8)

        std_tpr = np.std(tprs, axis=0)
        tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
        tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
        ax.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                        label=r'$\pm$ 1 std. dev.')

        ax.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05],
               title="Receiver operating characteristic (ROC)")
        ax.legend(loc="lower right")
        plt.show()
        plt.savefig('roc_curve_cv.png')


def plot_confusion_matrix(y_test, y_pred, n_classes):
    category_dict = get_category_dict()
    labels_name = [v for k, v in category_dict.items() if k <= n_classes]
    cm = confusion_matrix(y_test, y_pred)
    cm_display = ConfusionMatrixDisplay(cm,display_labels=labels_name)
    cm_display.plot()
    plt.show()
    plt.savefig('confusion_matrix_multi.png')
    print('confusion_matrix printed.')
