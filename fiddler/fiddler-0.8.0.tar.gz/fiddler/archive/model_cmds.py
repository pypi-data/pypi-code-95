import pandas as pd
import yaml

from fiddler.fiddler_api import FiddlerApi


def execute_cmd(args):
    client = FiddlerApi(url=f'http://localhost:{args.port}', org_id=args.org)
    df = pd.read_csv('dataset.csv')
    if args.index:
        df = df.loc[[int(args.index)]]
    else:
        df = df.head()
    print('Input: ')
    print(df)
    result = client.run_model(args.project, args.model, df)
    print('Result: ')
    print(result)


def explain_cmd(args):
    client = FiddlerApi(url=f'http://localhost:{args.port}', org_id=args.org)
    df = pd.read_csv('dataset.csv')
    if args.index:
        df = df.loc[[int(args.index)]]
    else:
        df = df.head(1)
    print('Input: ')
    print(df)
    if args.explanations:
        explanations = args.explanations
    else:
        explanations = 'shap'
    result = client.run_explanation(
        args.project,
        args.model,
        df,
        dataset_id='titanic',
        explanations=explanations,
    )
    print('Output: ')
    print(yaml.dump(result))
