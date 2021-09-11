"""
Xwalk (version 0.6)
-------------------

INTRODUCTION
------------
Chemical cross-linking of proteins or protein complexes and the mass
spectrometry based localization of the cross-linked amino acids is a powerful
method for generating distance information on the substrate topology. Here we
introduce the algorithm Xwalk for predicting and validating these cross-links on
existing protein structures. Xwalk calculates and displays non-linear distances
between chemically cross-linked amino acids on protein surfaces, while mimicking
the flexibility and non-linearity of cross-linker molecules. It returns a
"Solvent Accessible Surface" (SAS) distance, which corresponds to the length of
the shortest path between two amino acids, where the path leads through solvent
occupied space without penetrating the protein surface.


TEST
-----
Test examples to execute Xwalk can be found in the test subdirectory.


CLASSPATH
---------
You might want to consider adding the bin directory into the CLASSPATH
environment of your SHELL, which avoids the usage of the -cp flag when executing
Xwalk.


COMMANDLINE PARAMETERS
----------------------
A list of all commandline parameters can be retrieved by typing -help before
a Xwalk execution.


OUTPUT
------
Distance information will be printed out to the STDOUT channel or via -out to a
local file in the following tab delimeted format:
...
1   1brs.pdb    LYS-1-D-CB  LYS-2-D-CB  1   5.9 6.6 0.0449  0.0685  KKAVINGEQIR-KAVINGEQIR
...
1st column: index
2nd column: filename
3rd column: PDB information of the 1st amino acid in the format:
            PDBThreeLetterCode-ResidueId-ChainId-AtomName
4th column: PDB information of the 2nd amino acid in the format:
            PDBThreeLetterCode-ResidueId-ChainId-AtomName
5th column: Sequence distance within the PDB file as calculated from the residue
            identifiers of the 1st and 2nd amino acid.
6th column: Euclidean distance between 1st and 2nd amino acid.
7th column: SAS distance between  1st and 2nd amino acid.
8th column: Probability for observing the Euclidean distance in a XL experiment
            using DSS or BS3.
9th column: Probability for observing the SAS distance in a XL experiment using
            DSS or BS3.
10th column: shortest tryptic peptide sequence for both amino acids.

Setting -pymol -out xxx.pml on the commandline will write a PyMOL script into
the file xxx.pml, which can be load into the molecular viewer PyMOL to visualise
the SAS distance paths (see NOTES).


ALGORITHM
---------
The SAS distance is calculated using a grid and the breadth-first search algorithm
to search within the grid for the shortest path between two points on the protein
surface using following algorithm:
1.)    Read in input data
    a. xyz.pdb, spatial coordinates of a protein or protein complex in PDB
       format.
    b. maxdist: maximum distance of the path (i.e. the length of the
       cross-linker + AA side chain length)
    c. listXL, a list of experimentally determined cross-linked lysine residues.
2.)    Remove all non-protein atoms in xyz.pdb and assign protein atoms a van der
    Waals radius sum of SURFNET atom radii + solvent radius
3.)    Select a random lysine pair AAab from listXL,
4.)    Check Euclidean distance (Euc) of AAab. Continue, if Euc > maxdist,
    disregard otherwise and go back to 3.)
5.)    Generate a grid of size maxdist and grid spacing 1 Angstroem centered at AAa
6.)    Set Integer.MAX_VALUE as distance for all grid cells and label grid cells as
    residing in the
    a. protein
    b. solvent
    c. boundary between protein and solvent
7.)    Label grid cells residing in AAab as solvent
8.)    Set distance dist = 0.0 for central grid cell of AAa and store grid cell in
    the active list listactive
9.)    Start breadth-first search. Iterate through listactive
    a. Check that grid cell i is labeled as solvent
    b. Find all immediate neighbors listneighbour
    c. Iterate through listneighbour
        i. Check that grid cell j is labeled as solvent
        ii. Compute new distance for grid cell j as the sum of the distance in
            grid cell i and the Euclidean distance between grid cell i and j
        iii. If distance sum in 9.c.ii is smaller than the current distance in
             grid cell j, store the distance sum as new distance for grid cell j
             and add grid cell j to the new active list listnew_active,
10.) Go back to step 9.) with listactive = listnew_active



NOTES
-----
- As the SAS distance is based on a grid calculation, the default heap size of
  the Java VM with 64MB is likely to be too small. You can increase the heap
  size with "java -Xmx512m"
- You can obtain PyMOL for free at the webpage: http://pymol.org/
- Beware that in order for PyMOL to recognize the script file, the file must
  have the name ending .pml
- You can load the script directly at the startup of PyMOL, i.e. with the
  command pymol 1brs.pml.


CONTACT
-------
abdullah@imsb.biol.ethz.ch


LICENCE
-------
Xwalk executable and libraries are available under the Creative Commons
Attribution-NonCommercial-ShareAlike 3.0 Unported License via the Xwalk website.

Anyone is free:
     to copy, modify, distribute the software;

Under the following conditions:
    - the original authors must be given credit by citing the original Xwalk paper:
        Kahraman A., Malmström L., Aebersold R. (2011). Xwalk: Computing and
        Visualizing Distances in Cross-linking Experiments. Bioinformatics,
        doi:10.1093/bioinformatics/btr348.
    - the software or derivate works must not be used for commercial purposes
    - derivate works must be licenced under the same or similar licence

Any of the above conditions can be waived if the authors give permission.


Xwalk on GitHub
---------------
https://github.com/abxka/Xwalk


COMMAND EXAMPLES
----------------
    # Help with information on the available parameter
java -cp ../bin/ Xwalk -help

    # Example executions on the barnase-barstar complex 1brs.pdb.
    # Calculate the Euclidean distance (-euc)
    # between the closest atoms of lysine residue (-aa1 lys -aa2 lys)
    # that have a maximum distance of 30 Angstroem.
java -cp ../bin/ Xwalk -infile 1brs.pdb -aa1 lys -aa2 lys -euc

    # Calculate the Euclidean distance (-euc)
    # between the closest atoms of aspartic (-aa1 asp) and glutamic (-aa2 glu) acid residues
    # that have a maximum distance of 30 Angstroem.
java -cp ../bin/ Xwalk -infile 1brs.pdb -aa1 asp -aa2 glu -euc -max 21.4

    # Calculate SASD
    # between beta-carbon atoms (-a1 cb -a2 cb)
    # of lysine residues (-aa1 lys -aa2 lys).
    # that have a maximum distance of 21.4 Angstroem (-max 21.4).
    # and remove prior to calculation all side chains (-bb)
java -Xmx256m -cp ../bin/ Xwalk -infile 1brs.pdb -aa1 lys -aa2 lys -a1 cb -a2 cb -max 21.4 -bb

    # Calculate SASD of intermolecular cross-links (-inter)
    # between the epsilon-nitrogen atoms (-a1 nz -a2 nz)
    # of lysine residues (-aa1 lys -aa2 lys).
    # that have a maximum distance of 11.4 Angstroem (-max 11.4).
    # and remove prior to calculation all side chains (-bb)
    # and output PyMOL script to visualize the SASD path (-pymol -out 1brs.pml)
java -Xmx256m -cp ../bin/ Xwalk -infile 1brs.pdb -aa1 lys -aa2 lys -a1 nz -a2 nz -max 21.4 -inter -pymol -out 1brs.pml


Xwalk HELP MESSAGE
------------------
EXAMPLARY command for program execution:
Xwalk -in 1brs.pdb -aa1 ARG -aa2 lys -a1 CB -a2 CB -bb -max 21

ABOUT
Version 0.6
Xwalk calculates and outputs distances in Angstroem for potential cross-links
between -aa1 type amino acids and -aa2 type amino acids in the PDB file -in.

IMPORTANT
If large protein complexes are processed, the Java heap size might need to be
increased from the default 64MB to 256MB, with the Java parameter -Xmx256m

OUTPUT FORMAT:
IndexNo InfileName      Atom1info       Atom2info       DistanceInPDBsequence   EuclideanDistance       SolventAccessibleSurfaceDistance        EucProbability  SASDprobability PeptidePairSequences

where the Solvent Accessible Surface (SAS) distance corresponds to a number code, when a Distance file (-dist) is provided:
        >= 0: SAS distance (when -euc is NOT set)
        -1: Distance exceeds the maximum distance (-max)
        -2: First atom is solvent-inaccessible
        -3: Second atom is solvent-inaccessible
        -4: Both atoms are solvent-inaccessible
        -5: First atom is in a cavity which prohibited proper shortest path calculations


Virtual cross-links are sorted first by decreasing probability, then by increasing SAS distance and finally by increasing Euclidean distance.

Commandline PARAMETER:
INPUT/OUTPUT:
        -infile <path>  Any PDB file; .tar, .gz and .tar.gz files with PDB file content are also accepted [required].
        -xSC    [switch]        Removes only side chain atoms of cross-linked amino acids except for CB atoms and keeps -radius at 1.4 prior to calculating SAS distances. This might be of value when side chain conformations of cross-linked residues are unknown [optional].
        -bb     [switch]        Reads in only backbone and beta carbon atom coordinates from the input file and increases -radius to 2.0. Be cautious using the option, as it might cause shortest path calculalations through "molecular tunnels" in your protein [optional][see also -xSC].
        -dist   <path>  Distance file holding at least the first 4 columns of the Xwalk output format. The file will be used to extract the indices and the residue pairs for the distance calculation [optional].
        -keepName       [switch]        Uses the same name (2nd column) in the output as in the distance file. [optional].
        -out    <path>  Writes output to this file, otherwise output is directed to the STDOUT channel. If -pymol is set than filename must have .pml filename ending [optional].
        -f      [switch]        Forces output to be written into a file even if file already exists [optional].
        -pymol  [switch]        Outputs a PyMOL (http://www.pymol.org/) script highlighting the calculated distances of the potential cross-links [optional].
        -v      [switch]        Outputs various information other than distances [optional].
        -grid   [switch]        Outputs on STDOUT channel the grid, which is used to calculate the Solvent Accessible Surface Distance. The grid is in PDB format with distances in the B-factor column [optional].

RESIDUE/ATOM SELECTION:
        -aa1    [String]        Three letter code of 1st amino acid. To specify more than one amino acid use '#' as a delimeter [required, if -r1 is not set].
        -aa2    [String]        Three letter code of 2nd amino acid. To specify more than one amino acid use '#' as a delimeter [required, if -r2 is not set].
        -r1     [String]        Amino acid residue number. To specify more than one residue number use '#' as a delimeter. [required, if -aa1 is not set].
        -r2     [String]        Amino acid residue number. To specify more than one residue number use '#' as a delimeter. [required, if -aa2 is not set].
        -c1     [String]        Chain ids for -aa1 or -r1. For blank chain Id use '_'. To specify more than one chain Id, append chain ids to a single string, e.g. ABC [optional](default: all chain Ids).
        -c2     [String]        Chain ids for -aa2 or -r2. For blank chain Id use '_'. To specify more than one chain Id, append chain ids to a single string, e.g. ABC [optional](default: all chain Ids).
        -a1     [String]        Atom type for -aa1 or -r1. To specify more than one atom type use '#' as a delimeter. [optional].
        -a2     [String]        Atom type for -aa2 or -r2. To specify more than one atom type use '#' as a delimeter. [optional].
        -l1     [String]        Alternative location id for -aa1 or -r1. To specify more than one alternative location, append alternative location ids to a single string, e.g. AB [optional].
        -l2     [String]        Alternative location id for -aa2 or -r1. To specify more than one alternative location, append alternative location ids to a single string, e.g. AB [optional].
        -intra  [switch]        Outputs only "intra-molecular" distances [optional].
        -inter  [switch]        Outputs only "inter-molecular" distances [optional].
        -homo   [double]        Outputs only shortest distance of potential cross-links between equally numbered residues. Reduces redundancy if PDB file is a homomeric protein complex. [optional].

DIGESTION RELATED:
        -trypsin        [switch]        Digests in silico the protein with trypsin and excludes peptides that are shorter than 5 AA or larger than 40 AA [optional].

DISTANCE RELATED:
        -max    [double]        Calculates distances in Angstroem only up-to this value, where the value must be smaller than 100.0 for SAS distance calculations. (default: 34.0).
        -euc    [switch]        Skips Solvent-Path-Distance calculation and outputs only Euclidean distances [optional].
        -prob   [switch]        Outputs probability information for each vXL as determined by experimental data on DSS and BS3 cross-linking experiments [optional].
        -bfactor        [switch]        Adds the uncertainty of the atom coordinates as expressed by their B-factor/temperature factor to the maximum distance threshold [optional].

SOLVENT-PATH-DISTANCE GRID RELATED:
        -radius [double]        Solvent radius for calculating the solvent accessible surface area [optional](default 1.4).
        -space  [double]        Spacing in Angstroem between grid cells. [optional](default 1.0).

"""

import os
import re

import numpy as np
import pandas as pd


def extract_xwalk_cmd(xwalk_cmd):
    aa1 = re.findall('-aa1 (.+?) ', xwalk_cmd, re.I)[0]
    aa2 = re.findall('-aa2 (.+?) ', xwalk_cmd, re.I)[0]
    a1 = re.findall('-a1 (.+?) ', xwalk_cmd, re.I)[0]
    a2 = re.findall('-a2 (.+?) ', xwalk_cmd, re.I)[0]
    inter_intra = re.findall('-(inter|intra)', xwalk_cmd, re.I)
    inter_intra = inter_intra[0] if inter_intra else None
    max_length = re.findall('-max (\d+?)[> ]', xwalk_cmd, re.I)[0]
    return aa1, aa2, a1, a2, inter_intra, max_length


def read_command_file(cmd_file, pdb_name):
    cmd_list = []
    with open(os.path.abspath(cmd_file), 'r') as cmd_handle:
        for each_line in cmd_handle:
            each_cmd = each_line.strip('\n')
            if not each_cmd:
                continue
            aa1, aa2, a1, a2, inter_intra, maxlength = extract_xwalk_cmd(each_cmd)

            rearranged_cmd = 'java -Xmx1024m Xwalk -infile {}.pdb -aa1 {} -aa2 {} -a1 {} -a2 {}{} -max {} -bb >'.format(
                pdb_name, aa1, aa2, a1, a2, ' -{}'.format(inter_intra) if inter_intra else '', maxlength)
            out_filename = '{pdb_filename}-{aa1}_{aa2}_{a1}_{a2}{inter_intra}-{maxlength}.txt'.format(
                pdb_filename=pdb_name, aa1=aa1, aa2=aa2, a1=a1, a2=a2,
                inter_intra='-{}'.format(inter_intra) if inter_intra else '', maxlength=maxlength)

            cmd_list.append((rearranged_cmd, out_filename))
    return cmd_list


def xwalk_run(cmd_list, result_add):
    cmd_num = len(cmd_list)
    for cmd_series, _ in enumerate(cmd_list):
        rearranged_cmd, out_filename = _
        each_cmd = '{}"{}"'.format(rearranged_cmd, os.path.join(result_add, out_filename))
        print('{}/{} Now running {}'.format(cmd_series + 1, cmd_num, each_cmd))
        os.system(each_cmd)


def merge_result(result_add):
    result_file_list = os.listdir(result_add)
    file_num = len(result_file_list)
    with open(os.path.join(result_add, 'MergedIntra.txt'), 'w') as intra_handle, open(os.path.join(result_add, 'MergedInter.txt'), 'w') as inter_handle:
        for file_series, each_result in enumerate(result_file_list):
            print('{}/{} Merging {}'.format(file_series + 1, file_num, each_result))
            intra_handle.write(each_result + '\n')
            inter_handle.write(each_result + '\n')

            result_path = os.path.join(result_add, each_result)
            with open(result_path, 'r') as result_handle:
                for each_line in result_handle:
                    if not each_line.strip('\n'):
                        continue
                    split_line = each_line.split('\t')
                    first_site = split_line[2]
                    second_site = split_line[3]
                    if first_site.split('-')[2] == second_site.split('-')[2]:
                        intra_handle.write(each_line)
                    else:
                        inter_handle.write(each_line)
            intra_handle.write('\n')
            inter_handle.write('\n')


class SiteConverter(object):

    def __init__(
            self,
            conversion_file,
            sheet_name=None,
            pdb_sites_col_name='PDBPos',
            fasta_sites_col_name='FastaPos',
            aa3_col_name='',
    ):

        self.conversion_info_df = self._read_conversion_file(conversion_file, sheet_name)

        self.pdb_sites = self.conversion_info_df[pdb_sites_col_name].tolist()
        self.fasta_sites = self.conversion_info_df[fasta_sites_col_name].tolist()
        self.correspond_aa3 = self.conversion_info_df[aa3_col_name].tolist()

    @staticmethod
    def _read_conversion_file(conversion_file, sheet_name=None) -> pd.DataFrame:
        if conversion_file.endswith('xlsx') or conversion_file.endswith('xls'):
            df = pd.read_excel(conversion_file, dtype=str, sheet_name=sheet_name)
        elif conversion_file.endswith('txt') or conversion_file.endswith('tsv'):
            df = pd.read_csv(conversion_file, sep='\t', dtype=str)
        elif conversion_file.endswith('csv'):
            df = pd.read_csv(conversion_file, sep=',', dtype=str)
        else:
            raise
        return df

    def pdb_to_fasta(self, pdb_pos):
        try:
            idx = self.pdb_sites.index(pdb_pos)
            return self.correspond_aa3[idx], self.fasta_sites[idx]
        except ValueError:
            print('not find pdb position: {}'.format(pdb_pos))
            return None

    def fasta_to_pdb(self, fasta_pos):
        """
        :param fasta_pos: type=str
        :return: similar to previous function
        """
        try:
            idx = self.fasta_sites.index(fasta_pos)
            return self.correspond_aa3[idx], self.pdb_sites[idx]
        except ValueError:
            print('not find fasta position: {}'.format(fasta_pos))
            return None

    def pdb_to_aa(self, pdb_pos):
        try:
            idx = self.pdb_sites.index(pdb_pos)
            return self.correspond_aa3[idx]
        except ValueError:
            print('not find pdb position {}'.format(pdb_pos))
            return None

    def fasta_to_aa(self, fasta_pos):
        try:
            idx = self.fasta_sites.index(fasta_pos)
            return self.correspond_aa3[idx]
        except ValueError:
            print('not find fasta position {}'.format(fasta_pos))
            return None


class XwalkRunner(object):
    """

    """
    xwalk_command_template = ('java -Xmx1024m -cp "{xwalk_bin}" Xwalk'
                              ' -infile "{pdb_path}"'
                              ' -pymol -out "{pymol_output}"'
                              ' -dist "{xwalk_input_file}"'
                              ' -max {max_distance} -bb -homo >"{output_path}"')

    def __init__(
            self,
            result_df: pd.DataFrame,
            link_info_colname,
            xwalk_dist_folder,
            pymol_folder,
            xwalk_bin_folder,
            pdb_path,
            max_distance: int = 100,
            equal_struct_fasta_aa_pos: bool = False,
            site_converter: dict = None,
            prot_mapper=None,
            linker_aa_file: str = None,
            task_identifier: str = None,
            logger=None,
    ):

        self.result_df = result_df
        self.link_info_colname = link_info_colname
        self.all_link_info = self.result_df[self.link_info_colname].drop_duplicates().tolist()

        self.xwalk_dist_folder = xwalk_dist_folder
        self.pymol_folder = pymol_folder
        self.xwalk_bin_folder = xwalk_bin_folder
        self.pdb_path = pdb_path
        for folder in [xwalk_dist_folder, pymol_folder, xwalk_bin_folder]:
            os.makedirs(folder, exist_ok=True)

        self.max_distance = max_distance
        if equal_struct_fasta_aa_pos:
            self.use_site_converter = False
        else:
            self.use_site_converter = True
            if site_converter is None:
                raise ValueError
            self.site_converter = site_converter

        if prot_mapper is None:
            self.prot_mapper_to_pdb = {
                'DNGAS': 'A',
                'DNG': 'A',
                'A': 'A',
                'GNB1': 'B',
                'B': 'B',
                'GNG2': 'G',
                'G': 'G',
                'Nb35': 'N',
                'NB35': 'N',
                'N': 'N',
                'GLP1R': 'R',
                'R': 'R',
                'GLP1': 'P',
                'GL': 'P',
                'P': 'P',
            }
        else:
            self.prot_mapper_to_pdb = prot_mapper

        if linker_aa_file is None:
            self.linker_linked_aa = {
                'ArGO': (('Arg', 'Arg'),),
                'KArGO': (('Lys', 'Arg'),),
                'EGS': (('Lys', 'Lys'),),
                'DSS': (('Lys', 'Lys'),),
                'BS3': (('Lys', 'Lys'),),
                'PDH': (('Glu', 'Asp'), ('Glu', 'Glu'), ('Asp', 'Asp')),
                'EDC': (('Lys', 'Glu'), ('Lys', 'Asp')),
            }
        else:
            self.linker_linked_aa = dict()
            self._read_linker_linking_info(linker_aa_file)

        self.task_identifier = task_identifier
        self.logger = logger
        self.xwalk_result = dict()

        self.output_file_path = os.path.join(self.xwalk_dist_folder, self.task_identifier + '-xwalk_output.tsv')

    def _read_linker_linking_info(self, linker_aa_file):
        with open(linker_aa_file, 'r') as f:
            linker_info = f.read().split('\n')
        for row in linker_info:
            if 'linker' in row:
                continue
            elif not row:
                continue
            else:
                split_row = row.split(',')
                if len(split_row) <= 1:
                    continue
                self.linker_linked_aa[split_row[0]] = (
                    (split_row[aa_num * 2], split_row[aa_num * 2 + 1])
                    for aa_num in range(len(split_row[1:]) // 2)
                )

    def _convert_sites(self, site, consensus_prot):
        if self.use_site_converter:
            convert_result = self.site_converter[consensus_prot].fasta_to_pdb(site)
            if convert_result is None:
                return None
            aa3, pdb_pos = convert_result
            return '{}-{}-{}-CA'.format(aa3, pdb_pos, consensus_prot)
        else:
            convert_result = self.site_converter[consensus_prot].pdb_to_aa(site)
            if convert_result is None:
                return None
            aa3 = convert_result
            return '{}-{}-{}-CA'.format(aa3, site, consensus_prot)

    def generate_xwalk_input(self):
        if self.logger is not None:
            self.logger.info('Generate xwalk input for {}'.format(self.task_identifier))

        xwalk_input = ''
        for idx, link_info in enumerate(self.all_link_info, 1):
            re_match = re.match('(.+?)\((\d+)\)-(.+?)\((\d+)\).*', link_info)

            input_aa1 = self._convert_sites(re_match.group(2), self.prot_mapper_to_pdb[re_match.group(1)])
            input_aa2 = self._convert_sites(re_match.group(4), self.prot_mapper_to_pdb[re_match.group(3)])

            if input_aa1 is not None and input_aa2 is not None:
                xwalk_input += '{}\t{}\t{}\t{}\n'.format(
                    idx, os.path.basename(self.pdb_path),
                    input_aa1,
                    input_aa2
                )
        with open(os.path.join(self.xwalk_dist_folder, self.task_identifier + '.tsv'), 'w') as f:
            f.write(xwalk_input)

    def fillin_command(self, start_time):
        str_pymol_filename = self.task_identifier + start_time + '.pml'
        command = self.xwalk_command_template.format(
            xwalk_bin=self.xwalk_bin_folder,
            pdb_path=self.pdb_path,
            pymol_output=os.path.join(self.pymol_folder, str_pymol_filename),
            xwalk_input_file=os.path.join(self.xwalk_dist_folder, self.task_identifier + '.tsv'),
            max_distance=self.max_distance,
            output_path=self.output_file_path,
        )
        return command

    def run_xwalk(self, start_time=None):
        if start_time is None:
            start_time = ''
        command = self.fillin_command(start_time)
        print('start cmd {}'.format(command))
        os.system(command)
        print('{} complete'.format(self.task_identifier))

    def collect_xwalk_result(self, output_file_path=None):
        if output_file_path is not None:
            self.output_file_path = output_file_path

        with open(self.output_file_path, 'r') as f:
            xwalk_output = f.read().strip('\n').split('\n')

        for row in xwalk_output:
            split_row = row.split('\t')
            idx = int(split_row[0])
            surface_distance = float(split_row[6])
            link_info = self.all_link_info[idx - 1]
            self.xwalk_result[link_info] = surface_distance

    def add_distance_to_plink_result(self):
        self.result_df['SASDs'] = self.result_df[self.link_info_colname].apply(
            lambda x: self.xwalk_result[x] if x in self.xwalk_result else np.nan)

    def get_result(self):
        return self.result_df.copy()

    def run_xwalk_pipeline(self):
        self.generate_xwalk_input()
        self.run_xwalk()
        self.collect_xwalk_result()
        self.add_distance_to_plink_result()
        return self.get_result()
