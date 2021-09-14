import pandas as pd
import pyBigWig

from .genomes import build_genomes


def check_bigwig(path: str, summary: bool = False, tol: int = 2, **other) -> list:
    bw = pyBigWig.open(path)

    consistent = {}
    for g in build_genomes():
        consistent[g.build] = {}
        for chrom, length in bw.chroms().items():
            if chrom not in g.chroms():
                consistent[g.build][chrom] = False
                continue

            if length > g[chrom]:
                consistent[g.build][chrom] = False
            else:
                consistent[g.build][chrom] = True

    genomes = report(path, consistent, summary=summary, tol=tol)
    return genomes


def check_bed(path: str, summary: bool = False, tol: int = 2, **other) -> list:
    consistent = {}
    genomes = build_genomes()
    for g in genomes:
        consistent[g.build] = {}
        for chrom in g.chroms():
            consistent[g.build][chrom] = True

    with open(path) as bed:
        for line in bed:
            chr, start, end = line.strip().split("\t")[0:3]
            for g in genomes:
                if chr in g.chroms():
                    if int(end) > g.size_of(chr):
                        consistent[g.build][chr] = False

    genomes = report(path, consistent, summary=summary, tol=tol)
    return genomes


def report(path: str, consistent: dict, summary: bool = False, tol: int = 2) -> list:
    genomes = []
    for g in consistent.keys():
        if summary:
            print(f"Not consistent with {g}:")
        n_not = 0
        for chrom in consistent[g].keys():
            if not consistent[g][chrom]:
                n_not += 1
                if summary:
                    print(f"\t{chrom}")

        if n_not < tol:
            genomes.append(g)

    if len(genomes) > 0:
        print(f"{path} is probably built on {', '.join(genomes)}.")
    else:
        print(f"{path} doesn't match any genomes that I know about.")

    return genomes
