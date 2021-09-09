import json
import argparse
from mutalyzer_retriever.related import _fetch_ncbi_esummary, _fetch_ncbi_elink, _extract_link_uids, _get_summary_result_one, _fetch_ncbi_datasets_gene_accession
import hashlib


path = "/home/mihai/projects/lumc/mutalyzer/retriever/tests/data/"


def get_hash(uids):
    uids.sort()
    s_i = ",".join(uids)
    return hashlib.md5(s_i.encode('utf-8')).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", help="endpoint")
    parser.add_argument("-i", help="id")
    parser.add_argument("-l", help="summary for all the links", action="store_true")
    parser.add_argument("-g", help="gene summary", action="store_true")
    args = parser.parse_args()
    if args.e == "esummary":
        if "," in args.i:
            uid = get_hash(args.i.split(","))
        else:
            uid = args.i
        print(uid)
        p = path + f"esummary_nucleotide_{uid}.json"
        print(p)
        with open(p, 'w') as outfile:
            json.dump(_fetch_ncbi_esummary("nucleotide", args.i), outfile, indent=2)

    elif args.e == "elink":
        uid = args.i
        p = path + f"elink_nucleotide_nucleotide_{uid}.json"
        print(p)
        with open(p, 'w') as outfile:
            json.dump(_fetch_ncbi_elink("nucleotide", "nucleotide", args.i), outfile, indent=2)
    elif args.e == "datasets":
        uid = args.i
        p = path + f"{uid}.ncbi_datasets_gene_accession.json"
        print(p)
        with open(p, 'w') as outfile:
            json.dump(_fetch_ncbi_datasets_gene_accession(args.i), outfile, indent=2)
    if args.l:
        summary = _get_summary_result_one(_fetch_ncbi_esummary("nucleotide", args.i))
        uid_links = _extract_link_uids(_fetch_ncbi_elink("nucleotide", "nucleotide", args.i), summary["genome"])
        print(uid_links)
        uid = get_hash(uid_links)
        p = path + f"esummary_nucleotide_{uid}.json"
        with open(p, 'w') as outfile:
            json.dump(_fetch_ncbi_esummary("nucleotide", ",".join(uid_links)), outfile, indent=2)
    if args.g:
        uid = args.i
        p = path + f"esummary_gene_{uid}.json"
        print(p)
        with open(p, 'w') as outfile:
            json.dump(_fetch_ncbi_esummary("gene", args.i), outfile, indent=2)


if __name__ == "__main__":
    main()
