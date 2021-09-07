# Copyright 2018-2020 Institute of Neuroscience and Medicine (INM-1),
# Forschungszentrum Jülich GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from . import logger

import siibra
MNI152SPACE = siibra.spaces.MNI152_2009C_NONL_ASYM

MIN_SIIBRA_VERSION=0.2
import re
siibra_version = float(re.sub('[^0-9.].*$','',siibra.__version__))
if siibra_version < MIN_SIIBRA_VERSION:
    raise RuntimeError("This version of siibra jugex expects siibra-python "
            f"version {MIN_SIIBRA_VERSION} or higher.")

from scipy.stats.mstats import winsorize
from statsmodels.formula.api import ols
import statsmodels.api as sm
import numpy as np
from concurrent import futures
from collections import defaultdict


class DifferentialGeneExpression:
    """
    Compute differential gene expresssion in two different brain regions,
    following the JuGEx algorithm described in the following publication:

    Sebastian Bludau, Thomas W. Mühleisen, Simon B. Eickhoff, Michael J.
    Hawrylycz, Sven Cichon, Katrin Amunts. Integration of transcriptomic and
    cytoarchitectonic data implicates a role for MAOA and TAC1 in the
    limbic-cortical network. 2018, Brain Structure and Function.
    https://doi.org/10.1007/s00429-018-1620-6

    The code follows the Matlab implementation of the original authors, which
    is available at
    https://www.fz-juelich.de/inm/inm-1/DE/Forschung/_docs/JuGex/JuGex_node.html
    """


    def __init__(self, parcellation, gene_names=[]):
        self._pvals = None
        self._index_by_regionspec = {}
        self._regionspecs = [None,None]
        self._sampledicts = [defaultdict(dict) for _ in range(2)]
        self.genes = set(gene_names)
        if not parcellation.supports_space(MNI152SPACE):
            raise Exception(f"{MNI152SPACE.name} space not supported by selected parcellation {parcellation}.")
        self.parcellation = parcellation

    @staticmethod
    def _anova_iteration(area,zscores,donor_factors):
        """
        Run a single ANOVA iteration on the current factors.
        """
        variable_factors = {
            "area" : area,
            "zscores": zscores
        }
        mod = ols( 'zscores ~ area + specimen + age + race',
                    data={**variable_factors, **donor_factors} ).fit()
        aov_table = sm.stats.anova_lm(mod, typ=1)
        return aov_table['F'][0]

    def run(self, permutations=1000, random_seed=None):
        """
        Runs a differential gene analysis on the configured microarray samples
        in two regions of interest (ROI). Requires that gene candidates and
        ROIs have been specified in advance using add_candidate_genes(),
        define_roi1() and define_roi2().

        Parameters
        ----------
        permutations: int
            Number of permutations to perform for ANOVA. Default: 1000
        random_seed: int or None
            (optional) Random seed to be applied before doing the ANOVA
            permutations in order to produce repeated identical results.
            Default: None


        Returns
        -------
        Dictionary of resulting p-values and factors used for the analysis.
        """

        if len(self.genes)==0:
            logger.error('No candidate genes defined. Use "add_candidate_gene"')
            return

        if any(len(samples)<1 for samples in self._sampledicts):
            logger.error('Not enough samples found for the given genes and regions.')
            return

        # retrieve aggregated factors and split the constant donor factors
        factors = self.get_aggregated_sample_factors()
        donor_factors = {k:factors[k] for k in ["specimen","age","race"]}

        if random_seed is not None:
            logger.info("Using random seed {}.".format(random_seed))
            np.random.seed(random_seed)
        logger.info('Running {} random permutations. This may take a while...'.format(permutations))

        # convenience function for reuse below
        run_iteration = lambda t: self._anova_iteration(t[0],t[1],donor_factors)

        # first iteration
        Fv = np.array([ run_iteration((factors['area'],mean_zscores))
                       for _,mean_zscores
                       in factors['zscores'].items()])

        # multi-threaded permutations
        trials = ((np.random.permutation(factors['area']),mean_zscores)
                  for _,mean_zscores
                  in factors['zscores'].items()
                  for _ in range(permutations-1))
        with futures.ThreadPoolExecutor() as executor:
            scores = list(executor.map(run_iteration, trials))
            Fm = np.array(scores).reshape((-1,permutations-1)).T

        # collate result
        FWE_corrected_p = np.apply_along_axis(
                lambda arr : np.count_nonzero(arr)/permutations, 0,
                Fm.max(1)[:, np.newaxis] >= np.array(Fv)
                )

        self._pvals = dict(zip(factors['zscores'].keys(), FWE_corrected_p))
        return self.result()

    def result(self):
        """
        Returns a dictionary with the results of the analysis.
        """
        if self._pvals is None:
            logger.warn('No result has been computed yet.')
            return {}
        return {**self.get_aggregated_sample_factors(), 'p-values':self._pvals}

    def add_candidate_genes(self,gene_name, reset=False):
        """
        Adds a single candidate gene or a list of multiple candidate genes to
        be used for the analysis.

        Parameters:
        -----------

        gene_name : str or list
            Name of a gene, as defined in the Allen API. See
            siibra.gene_names for a full list.
            It is also possible to provide a list of gene names instead of
            repeated calls to this function.

        reset : bool
            If True, the existing list of candidate genes will be replaced with
            the new ones. (Default: False)

        TODO on invalid parameter, we could show suggestions!
        """
        if reset:
            self.genes = set()
        if isinstance(gene_name,list):
            return all([ self.add_candidate_genes(g)
                for g in gene_name ])

        assert(isinstance(gene_name,str))
        if gene_name not in siibra.gene_names:
            logger.warn("'{}' not found in the list of valid gene names.")
            return False
        self.genes.add(gene_name)
        return True

    def _define_roi(self,regionspec,roi_index):
        """
        (Re-)Defines a region of interest.

        Parameters:
        -----------

        regionspec : str or list
            Identifier or list of identifiers for a brain region in the
            selected atlas parcellation
        roi_index : 0 or 1
            index of the roi to be updated
        """
        if type(regionspec) == str:
            new_samples = self._retrieve_samples(regionspec)
            if new_samples is None:
                raise Exception("Could not define ROI.")
            if self._regionspecs[roi_index] is not None:
                self._index_by_regionspec.pop(regionspec)
            self._regionspecs[roi_index] = regionspec
            self._sampledicts[roi_index] = new_samples
            self._index_by_regionspec[regionspec] = roi_index

        elif type(regionspec) == list:
            new_samples = None
            for region in regionspec:
                logger.info(region)
                if new_samples is None:
                    new_samples = self._retrieve_samples(region)
                else:
                    new_samples.update(self._retrieve_samples(region))
            if new_samples is None:
                raise Exception("Could not define ROI.")
            if self._regionspecs[roi_index] is not None:
                self._index_by_regionspec.pop(regionspec)
            self._regionspecs[roi_index] = "Merged ROI1"
            self._sampledicts[roi_index] = self._filter_samples(new_samples)
            self._index_by_regionspec["Merged ROI1"] = roi_index

        else:
            logger.warning("Unsupported parameter in ROI")


    def define_roi1(self,regionspec):
        """
        (Re-)Defines the first region of interest.

        Parameters:
        -----------

        regionspec : str or list
            Identifier or list of identifiers for a brain region in the
            selected atlas parcellation
        """
        self._define_roi(regionspec,0)


    def define_roi2(self,regionspec):
        """
        (Re-)defines the second region of interest.

        Parameters:
        -----------

        regionspec : str or list
            Identifier or list of identifiers for a brain region in the
            selected atlas parcellation
        """
        self._define_roi(regionspec,1)

    def _retrieve_samples(self,regionspec):
        """
        Retrieves and prepares gene expression samples for the given region
        definition.

        Parameters:
        -----------

        regionspec : str
            Identifier for a brain region in the selected atlas parcellation

        Returns: dictionary
            Gene expression data samples for the provided region
        """
        region = self.parcellation.decode_region(regionspec)
        if region is None:
            logger.warn("Region definition '{}' could not be matched in atlas.".format(regionspec))
            return None
        samples = defaultdict(dict)
        for gene_name in self.genes:
            for f in siibra.get_features( region, "gene", gene=gene_name):
                key = tuple(list(f.location)+[regionspec])
                samples[key] = {**samples[key], **f.donor_info}
                samples[key]['mnicoord'] = tuple(f.location)
                samples[key]['region'] = region
                samples[key][gene_name] =  np.mean(
                        winsorize(f.z_scores, limits=0.1))
        logger.info('{} samples found for region {}.'.format(
            len(samples), regionspec))
        return samples


    @staticmethod
    def _filter_samples(samples):
        """
        Filter out duplicate samples from the samples dictionary.

        Parameters:
        -----------

        samples : defaultdict
            Gene expression data samples for the provided region

        Returns: dictionary
            Filtered gene expression data samples for the provided region
        """
        test_list = []

        for coord in list(samples.keys()):
            if coord[0:3] not in test_list:
                test_list.append(coord[0:3])
            else:
                del samples[coord]

        return samples


    def get_aggregated_sample_factors(self):
        """
        Creates a dictionary of flattened sample factors for the analysis from
        the two sets of collected samples per gene.
        """
        samples = {**self._sampledicts[0], **self._sampledicts[1]}
        factors = {
            'race' : [s['race'] for s in samples.values()],
            'age' : [s['age'] for s in samples.values()],
            'specimen' : [s['name'] for s in samples.values()],
            'area' : [s['region'].name for s in samples.values()],
            'zscores' : {g:[s[g] for s in samples.values()]
                          for g in self.genes},
            'mnicoord' : [s['mnicoord'] for s in samples.values()]
        }
        return factors

    def get_samples(self,regionspec):
        """
        Returns the aggregated sampel information for the region specification
        that has been used previously to define a ROI using define_roi1() or
        define_roi2().

        Parameters
        ---------
        regionspec : str
            Region identifier string used previously in define_roi1() or define_roi2()
        """
        if regionspec not in self._index_by_regionspec.keys():
            logger.warn("The provided region definition string is not known.")
            return None
        roi_index = self._index_by_regionspec[regionspec]
        return self._sampledicts[roi_index]


    def save(self,filename):
        """
        Saves the aggregated factors and computed p-values to file.

        Parameters
        ----------
        filename : str
            Output filename
        """
        import json
        data = self.result()
        with open(filename,'w') as f:
            json.dump(data,f,indent="\t")
            logger.info("Exported p-values and factors to file {}.".format(
                filename))
