import argparse
import re
import json
from .analyzer import TuroyoAnalyzer


def main(text):
    a = TuroyoAnalyzer()

    words = re.findall('\\b(\\w[\\w\\-]*\\w|\\w)\\b', text)
    analyses = a.analyze_words(words, format='json')
    print(json.dumps(analyses, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze Turoyo words and sentences from command line.\n'
                                                 'Usage: python3 -m uniparser-turoyo (Turoyo sentence here.)')
    parser.add_argument('text', default='', help='Text in Turoyo (Latin-based alphabet)')
    args = parser.parse_args()
    text = args.text
    main(text)
