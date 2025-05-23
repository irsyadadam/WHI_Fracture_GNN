#os
import importlib.metadata
import json
import logging
import os
import re
import tempfile
import time
import ast
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union


import torch

from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings("ignore")

from train_utils.frax_utils import FRAX_maximize_youden_j

def evaluate_model(y_true, y_pred, y_prob=None, descr = None):
    """
    Computes and prints standard classification metrics: Accuracy, AUC, Precision, Recall, and F1-score.

    :param y_true: List or array of true labels (0 or 1).
    :param y_pred: List or array of predicted labels (0 or 1).
    :param y_prob: List or array of predicted probabilities (optional, needed for AUC).
    :return: Dictionary containing Accuracy, AUC, Precision, Recall, and F1-score.
    """
    metrics = {
        "Accuracy": accuracy_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred, zero_division=0),
        "Recall": recall_score(y_true, y_pred, zero_division=0),
        "F1-score": f1_score(y_true, y_pred, zero_division=0),
        "AUC": roc_auc_score(y_true, y_prob) 
    }

    # Print metrics
    if descr:
        print(descr)
    for key, value in metrics.items():
        print(f"\t{key}: {value:.4f}" if value is not None else f"{key}: N/A (Only one class present)")

    return metrics


#SKLEARN WRAPPER
def eval_run(model, x, y, 
             model_type: Optional[str] = "sklearn", 
             descr = None):

    #tensor type
    if model_type is not "sklearn":
        with torch.no_grad():
            logits = model(x)
            y_prob = torch.sigmoid(logits).detach().cpu().numpy()  # Convert logits to probabilities
            y_pred = (y_prob > 0.5).astype(int)  # Convert probabilities to binary predictions
            metrics = evaluate_model(y.detach().cpu().numpy(), y_pred, y_prob, descr = descr)
    else:
        y_pred = model.predict(x)
        y_prob = model.predict_proba(x)[:, 1]
        metrics = evaluate_model(y, y_pred, y_prob, descr = descr)
        
    return metrics

#SKLEARN WRAPPER
def eval_frax(frax_scores, labels, descr = None, threshold = None):
    if threshold:
        pass
    else:
        threshold = FRAX_maximize_youden_j(labels, frax_scores)
    y_pred = (frax_scores >= threshold).astype(int)
    evaluate_model(labels, y_pred, frax_scores, descr = descr)
    return threshold

