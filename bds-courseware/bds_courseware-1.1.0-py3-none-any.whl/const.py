MODULE_DATASETS_LIST = [
    ["msft_store"],
    ["bank"],
    ["sweets", "suicide_rates", "car_perfs", "brain"],
    ["air_quality"],
    ["hypothyroid"],
    ["movies"],
]

MODULE_DATASETS = {
    "be": ["msft_store"],
    "eda": ["bank"],
    "stats": ["sweets", "suicide_rates", "car_perfs", "brain"],
    "reg": ["air_quality"],
    "cls1": ["hypothyroid"],
    "cls2": ["movies"],
}

WORKSHOP_DATASETS = {
    # BE
    "msft_store": ("15mCEE_6GfUXBMLh58zhOYBp6Gfti7TOq", "csv"),
    # STATS
    "sweets": ("1rD-yCS4CJ2qkeBgL-f3ilahatb8pZq2G", "csv"),
}

HOMEWORK_DATASETS = {
    # STATS
    "suicide_rates": ("1fhUu_t9C7yqVuMXeqjadFFzEzAdfwgiT", "csv"),
    "car_perfs": ("1WCNKNxbTyR0DkE4wk9fKl7C9tVaTA7Al", "tsv"),
    "brain": ("1tpZxfubFR0QT-pvLEjs34_A77VR7uIhC", "tsv"),
    # EDA
    "bank": ("1mCPUi9nHDHAfHGYf0oi-tnhbkCGTb_Mg", "ssv"),
    # "bank_for_dr": ("15hKFhmB71WwTdqNF5_29TPsqW5PyGa50", "csv.gz"),
    # REG1
    "air_quality": ("1Cf1oA7L9UM2B7HemJ9gFbr9IAgHquyfT", "ssv"),
    # CLS1
    "hypothyroid": ("1m53GMGvefv99ZeTOuhjb5wLkTSwfMTCf", "csv"),
    # CLS2
    "movies": ("1ZyCVwksXfp03H4X8wOye6vRD3B3O2YFl", "csv"),
    # REG2 and TS
    "bike_sharing_day": ("1KWMuDmPznwEF5317-yhCdYxjnxFWeFbq", "csv"),
    "bike_sharing_hour": ("1p4azCzZlFR5KZNVa4bG-LrZZtx0lPds1", "csv"),
    # Clustering
    "quake": ("1S5stL1xz51y5QkGRHHfWqteacHDYOYXM", "csv")
}
DATASETS = dict(**HOMEWORK_DATASETS, **WORKSHOP_DATASETS)
