import pkg_resources
from shutil import copy


class Genome:
    def __init__(self, name):
        self.sizes = {}
        self.build = name
        path = self.genome_path(name)

        with open(path) as f:
            for line in f:
                chrom, length = line.strip().split()
                self.sizes[chrom] = int(length)

    def __getitem__(self, key):
        return self.sizes[key]

    def items(self):
        return self.sizes.items()

    def chroms(self):
        return [k for k in self.sizes.keys()]

    def size_of(self, chrom):
        return self.sizes[chrom]

    def genome_path(self, name):
        return pkg_resources.resource_filename("wgba.sizes", f"{name}.chrom.sizes")
        # Try except here for names not found


def build_genomes():
    genomes = []

    files = [
        i.replace(".chrom.sizes", "")
        for i in pkg_resources.resource_listdir("wgba.sizes", ".")
        if i not in ["__init__.py", "__pycache__"]
    ]
    for g in files:
        genomes.append(Genome(g))

    return genomes


def add_build(path):
    assert (
        ".chrom.sizes" in path
    ), "Your file name must begin with the build ID and end with .chrom.sizes"

    files = [
        i.replace(".chrom.sizes", "")
        for i in pkg_resources.resource_listdir("wgba.sizes", ".")
        if i not in ["__init__.py", "__pycache__"]
    ]
    folder = (
        "/".join(
            pkg_resources.resource_filename("wgba.sizes", files[0]).split("/")[:-1]
        )
        + "/"
    )

    copy(path, folder + path)

    print(
        f"WGBA: Successfully added '{path.split('/')[-1].replace('.chrom.sizes', '')}' to the list of known genomes."
    )
