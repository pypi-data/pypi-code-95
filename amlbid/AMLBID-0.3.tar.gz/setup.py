from setuptools import setup, find_packages

setup(
    name='AMLBID',
    version='0.3',
    description='Transparent and Auto-explainable AutoML',
    long_description="""

AMLBID is a Python-Package representing a meta learning-based framework for automating the process of algorithm selection, and hyper-parameter tuning in supervised machine learning. Being meta-learning based, the framework is able to simulate the role of the machine learning expert as a decision support system. In particular, AMLBID is considered the first complete, transparent and auto-explainable AutoML system for recommending the most adequate ML configuration for a problem at hand, and explain the rationale behind the recommendation and analyzing the predictive results in an interpretable and faithful manner through an interactive multiviews artifact.


A deployed example can be found at https://colab.research.google.com/drive/1zpMdccwRsoWe8dmksp_awY5qBgkVwsHd?usp=sharing
""",
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    package_dir={'AMLBID': 'AMLBID'},  
    package_data={
        'AMLBID': ['Explainer/assets/*', 'Recommender/builtins/KnowledgeBase/*'],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Dash",
        "Framework :: Flask",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"],
    install_requires=['dash>=1.20', 'dash-bootstrap-components', 'jupyter_dash', 'dash-auth',
                    'dtreeviz>=1.3', 'numpy', 'pandas>=1.1', 'scikit-learn', 
                    'shap>=0.37', 'joblib', 'oyaml', 'click', 'waitress',
                    'flask_simplelogin', 'scikit-learn', 'xgboost', 'termcolor', 'pdpbox', 'shortuuid'],
    python_requires='>=3.6',
    author='Moncef GAROUANI',
    author_email='mgarouani@gmail.com',
    keywords=['machine learning', 'Automated machine learning', 'explainability'],
    url='https://github.com/LeMGarouani/AMLBID',
    project_urls={
        "Github page": "https://github.com/LeMGarouani/AMLBID",
        "Documentation": "https://github.com/LeMGarouani/AMLBID",
    },
)
