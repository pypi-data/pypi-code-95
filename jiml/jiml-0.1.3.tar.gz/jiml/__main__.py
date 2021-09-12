import argparse
import json
import pathlib
import sys

import yaml
import jiml

FORMATS = ['json', 'yaml']

LOADERS = {
    'json': json.loads,
    'yaml': yaml.safe_load,
}

DUMPERS = {
    'json': lambda *args, allow_unicode=False, **kwargs: json.dumps(
        *args, ensure_ascii=not allow_unicode, **kwargs
    ),
    'yaml': yaml.dump,
}


def parse_args():
    parser = argparse.ArgumentParser(description='Convert json to json.')
    parser.add_argument(
        '-t', '--template',
        required=True,
        type=pathlib.Path,
        help='jinja template path'
    )
    parser.add_argument(
        '-i', '--input',
        type=pathlib.Path,
        help='input json path (stdin by default)'
    )
    parser.add_argument(
        '-o', '--output',
        type=pathlib.Path,
        help='output json path (stdout by default)'
    )

    parser.add_argument(
        '-I', '--input-format',
        choices=FORMATS,
    )
    parser.add_argument(
        '-O', '--output-format',
        choices=FORMATS,
    )

    parser.add_argument('-s', '--sort-keys', action='store_true')
    parser.add_argument('-u', '--allow-unicode', action='store_true')
    parser.add_argument('-n', '--indent', type=int)

    parser.add_argument('-A', '--no-autoescape', action='store_true')

    return parser.parse_args()


def main():
    args = parse_args()
    template = args.template.read_text()
    if args.input is None:
        input_text = sys.stdin.read()
        input_suffix = None
    else:
        input_text = args.input.read_text()
        input_suffix = args.input.suffix.strip('.')
        input_suffix = input_suffix if input_suffix in FORMATS else None

    if args.output is None:
        output_suffix = None
    else:
        output_suffix = args.output.suffix.strip('.')
        output_suffix = output_suffix if output_suffix in FORMATS else None

    input_format = args.input_format or input_suffix or 'json'
    output_format = args.output_format or output_suffix or 'json'

    input_data = LOADERS[input_format](input_text)
    output_data = jiml.convert(template, input_data, autoescape=not args.no_autoescape)
    output_text = DUMPERS[output_format](
        output_data,
        indent=args.indent,
        allow_unicode=args.allow_unicode,
        sort_keys=args.sort_keys,
    )

    if args.output is None:
        sys.stdout.write(output_text)
    else:
        args.output.write_text(output_text)


if __name__ == '__main__':
    main()
