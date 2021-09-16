import datetime
import doctest
import functools
import importlib
import inspect
import io
import itertools
import json
import logging
import math
import os
import pickle
import re
import subprocess
import sys
import time
import types
import urllib.request as urllib2
from pprint import pprint

import numpy as np
import pandas as pd
import pyspark
import pyspark.ml
import rich
import rich.console
import rich.syntax
import yaml
from munch import Munch
from objprint import op
from pyspark.context import SparkContext
from pyspark.ml import Pipeline, Transformer
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator, Evaluator
from pyspark.ml.feature import (CountVectorizer, HashingTF,
                                QuantileDiscretizer, StandardScaler, Tokenizer,
                                VectorAssembler)
from pyspark.ml.linalg import DenseVector, Vectors, VectorUDT
from pyspark.ml.param import Params
from pyspark.ml.param.shared import (HasInputCol, HasOutputCol, Param, Params,
                                     TypeConverters)
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from pyspark.sql import DataFrame, GroupedData, Row, SparkSession
from pyspark.sql import functions as fn
from pyspark.sql.functions import expr as sql_
from pyspark.sql.types import *
from termcolor import colored

scoutregiment_package_path = './.scoutregiment_package'

if scoutregiment_package_path not in sys.path:
    sys.path.insert(0, scoutregiment_package_path)


def download_2f(url):
    g = globals()
    def download(filepath):
        file_uri = f"{url}/{filepath}"
        filename = filepath.split("/")[-1]
        module_name = filename.replace(".py", "")
        if not os.path.exists(scoutregiment_package_path):
            os.path.mkdir(scoutregiment_package_path)
        with open(f"{scoutregiment_package_path}/{filename}", 'w') as fw:
            with urllib2.urlopen(file_uri) as f:
                fw.write(f.read().decode())
        g[module_name] = __import__(module_name)
        if module_name in g:
            importlib.reload(g[module_name])
    return download
