import requests
from bs4 import BeautifulSoup
import re
from typing import Optional
from shutil import copyfile
from json import loads as _json_loads
import typer
from pathlib import Path
from os import makedirs as _os_makedirs

def fetch_soup(url: str):
    resp = requests.get(url)
    return BeautifulSoup(resp.text, 'html.parser')

def fetch_task_soup(no):
    return fetch_soup(f'https://algo-method.com/tasks/{no}')

def load_json(soup):
    return _json_loads(list(soup.find('script', {'type': 'application/json'}).next_elements)[0])


def compute_ins_and_outs(soup):
    json_data = load_json(soup)
    lines = json_data['props']['pageProps']['tasks']['body'].split('\n')
    in_examples = [i for i, line in enumerate(lines) if '### 入力例' in line]

    i = in_examples[0]
    start = None
    end = None
    ins = []
    while i < len(lines):
        line = lines[i]
        if line.startswith('```') and start is None:
            start = i
        elif line.startswith('```') and end is None:
            end = i

        if end is not None:
            in_ = []
            for j in range(start+1, end):
                in_.append(lines[j].rstrip('\r'))
            ins.append(in_)

            start, end = None, None
        i += 1

    return ins[::2], ins[1::2]


def write_task_in_outs(ins, outs, path):
    n = len(ins)
    assert len(outs) == len(ins)

    if path.exists():
        print(f'{path.absolute()} is exists')
        return None
    else:
        _os_makedirs(path)

    print(f'write into {path.absolute()}')
    for i in range(n):
        fname = path / f'in_{i+1}.txt'
        with open(str(fname), 'w') as f:
            for line in ins[i]:
                f.write(line + '\n')

        fname = path / f'out_{i+1}.txt'
        with open(str(fname), 'w') as f:
            for line in outs[i]:
                f.write(line + '\n')

app = typer.Typer(add_completion=False)

@app.command('create')
def create_main(
        task_no,
        base_dir: Path=typer.Option(Path('~/algo-methods/').expanduser(), '-b', '--base-dir', help='base directory'),
        template_file: Optional[str] = typer.Option(None, '-t', '--template-file', help='template filename')):
    soup = fetch_task_soup(task_no)
    json_data = load_json(soup)
    ins, outs = compute_ins_and_outs(soup)
    write_task_in_outs(ins, outs, base_dir / task_no)
    main_file = base_dir / task_no / 'main.py'
    if template_file:
        template_file = Path(template_file).absolute()
        copyfile(template_file, str(main_file))
    else:
        with open(str(main_file), 'w') as f:
            ...

def main():
    app()

if __name__ == '__main__':
    main()
