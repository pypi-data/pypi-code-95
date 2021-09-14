# Upload an SBOL file to SynBioHub

import argparse

import sbol2


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("sbol", metavar="SBOL_FILE")
    parser.add_argument("url", metavar="PARTSHOP_URL")
    parser.add_argument('-d', '--description', default='test description')
    parser.add_argument('-n', '--name', default='test data')
    parser.add_argument('-i', '--id', default='test')
    parser.add_argument('-u', '--user', default='testuser')
    parser.add_argument('-p', '--password', default='test')
    args = parser.parse_args(args)
    return args


def main(argv=None):
    args = parse_args(argv)

    doc = sbol2.Document(args.sbol)
    doc.description = args.description
    doc.displayId = args.id
    doc.name = args.name

    part_shop = sbol2.PartShop(args.url)
    # part_shop.spoof('https://synbiohub.org')
    part_shop.login(args.user, args.password)
    part_shop.submit(doc)


if __name__ == '__main__':
    main()
