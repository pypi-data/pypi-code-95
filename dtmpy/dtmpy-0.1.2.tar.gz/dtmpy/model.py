"""Module with helper functions for writing DTM inputs and reading DTM outputs."""
from pathlib import Path
from typing import Optional, List, Tuple, Union, Dict
import numpy as np

from _dtmpy import dtm


class DTM:
    """Class for Dynamic Topic Modeling."""

    def __init__(
        self,
        corpus_prefix: str,
        output_name: str,
        n_topics: int = 10,
        mode: str = "fit",
        model: str = "dtm",
        initialize_lda: bool = True,
        lda_max_em_iter: int = 20,
        lda_sequence_max_iter: int = 20,
        lda_sequence_min_iter: int = 1,
        lda_inference_max_iter: int = 25,
        top_chain_var: float = 0.005,
        top_obs_var: float = 0.5,
        alpha: float = 0.01,
        rng_seed: int = 0,
        lda_model_prefix: str = "",
        influence_flat_years: int = -1,
        influence_mean_years: float = 20,
        influence_stdev_years: float = 15,
        max_number_time_points: int = 200,
        resolution: float = 1,
        time_resolution: float = 0.5,
        fix_topics: int = 0,
        forward_window: int = 1,
        normalize_docs: str = "normalize",
        save_time: int = 2147483647,
        lambda_convergence: float = 0.01,
        heldout_corpus_prefix: str = "",
        heldout_time: int = -1,
        params_file: str = "settings.txt",
        sigma_c: float = 0.05,
        sigma_cv: float = 1e-6,
        sigma_d: float = 0.05,
        sigma_l: float = 0.05,
        output_table: str = "",
        start: int = -1,
        end: int = -1,
    ):
        """Initialize DTM model parameters.

        Args:
            corpus_prefix: Directory and file name prefix to use when writing
                the input data. For example, if corpus_prefix is "foo/bar",
                the DTM input files are written to "foo/bar-seq.dat" and
                "foo/bar-mult.dat".
            output_name: Directory name used to write model output files to,
                relative to corpus_path.
            n_topics: The number of requested latent topics to be extracted from the
                training corpus.
            mode: The function to perform in the model, "fit", "est", or "time".
            model: The model to use, either dynamic topic model ("dtm") or dynamic
                inference model ("dim").
            initialize_lda: If true, initialize the DTM model with an LDA
                model.
            lda_max_em_iter: Max iterations for LDA initialization.
            lda_sequence_max_iter: The maximum number of iterations used for
                fitting DTM.
            lda_sequence_min_iter: The minimum number of iterations used for
                fitting DTM.
            lda_inference_max_iter: Max iterations to use for dynamic inference model.
            top_chain_var: Gaussian parameter defined in the beta distribution
                to dictate how the beta values evolve over time.
            top_obs_var: Observed variance used to approximate the true and
                forward variance.
            alpha: The prior probability for the model.
            rng_seed: Specifies the random seed. If 0, seeds pseudo-randomly.
            lda_model_prefix: The name of a fit model to be used for testing
                likelihood. Appending "info.dat" to this should give the name of
                the file.
            influence_flat_years: How many years is the influence nonzero? If
                nonpositive, a lognormal distribution is used.
            influence_mean_years: How many years is the mean number of citations?
            influence_stdev_years: How many years is the stdev number of citations?
            max_number_time_points: Used for the influence window.
            resolution: Used to determine how far out the beta mean should be.
            time_resolution: This is the number of years per time slice.
            fix_topics: Fix a set of this many topics. This amounts to fixing
                these  topics' variance at 1e-10.
            forward_window: The forward window for deltas. If negative, we use
                a beta with mean 5.
            normalize_docs: Describes how documents's wordcounts are considered
                for finding influence. Options are "normalize", "none",
                "occurrence", "log", or "log_norm".
            save_time: Save a specific time. If -1, save all times.
            lambda_convergence: Specifies the level of convergence required for
                lambda in the phi updates.
            heldout_corpus_prefix: Path and prefix of heldout corpus mult and seq files.
            heldout_time: A time up to (but not including) which we wish to
                train, and at which we wish to test.
            params_file: A file containing parameters for this run.
            sigma_c: Undocumented DTM input parameter.
            sigma_cv: Undocumented DTM input parameter.
            sigma_d: Undocumented DTM input parameter.
            sigma_l: Undocumented DTM input parameter.
            output_table: Undocumented DTM input parameter.
            start: Undocumented DTM input parameter.
            end: Undocumented DTM input parameter.
        """
        self.corpus_prefix = corpus_prefix
        self.corpus_path = Path(self.corpus_prefix).parent
        self.output_path = f"{self.corpus_path}/{output_name}"
        self.n_topics = n_topics
        self.top_chain_var = top_chain_var
        self.top_obs_var = top_obs_var
        self.alpha = alpha
        self.mode = mode
        self.model = model
        self.initialize_lda = initialize_lda
        self.lda_max_em_iter = lda_max_em_iter
        self.lda_sequence_max_iter = lda_sequence_max_iter
        self.lda_sequence_min_iter = lda_sequence_min_iter
        self.lda_inference_max_iter = lda_inference_max_iter
        self._rng_seed = rng_seed
        self._lda_model_prefix = lda_model_prefix
        self._influence_flat_years = influence_flat_years
        self._influence_mean_years = influence_mean_years
        self._influence_stdev_years = influence_stdev_years
        self._max_number_time_points = max_number_time_points
        self._resolution = resolution
        self._time_resolution = time_resolution
        self._fix_topics = fix_topics
        self._forward_window = forward_window
        self._normalize_docs = normalize_docs
        self._save_time = save_time
        self._lambda_convergence = lambda_convergence
        self._heldout_corpus_prefix = heldout_corpus_prefix
        self._heldout_time = heldout_time
        self._params_file = params_file
        self._sigma_c = sigma_c
        self._sigma_cv = sigma_cv
        self._sigma_d = sigma_d
        self._sigma_l = sigma_l
        self._output_table = output_table
        self._start = start
        self._end = end

        self._model_fit = False

        # Create output directory if it does not exist
        if not Path(self.output_path).is_dir():
            Path(self.output_path).mkdir(parents=True, exist_ok=True)

    def read_corpus(self, corpus_prefix: Optional[str] = None):
        """Create bow_corpus and time_slices from existing mult and seq input files.

        Args:
            corpus_prefix: Directory and file name prefix to use when writing
                the input data. For example, if corpus_prefix is "foo/bar",
                the DTM input files are written to "foo/bar-seq.dat" and
                "foo/bar-mult.dat". If not specified, corpus_prefix from DTM
                initialization will be used.

        Returns:
            Bag-of-words corpus list
            Time slices list
        """
        # Default to existing
        if corpus_prefix is None:
            corpus_prefix = self.corpus_prefix
        self._read_seq_file(f"{corpus_prefix}-seq.dat")
        self._read_mult_file(f"{corpus_prefix}-mult.dat")
        return self.bow_corpus, self.time_slices

    def fit(
        self,
        bow_corpus: List[List[Tuple[int, int]]],
        time_slices: Optional[List[int]] = None,
        n_time_slices: int = 20,
    ):
        """Fit DTM model to corpus data.

        This function creates a DTM model and fits it using bag-of-words corpus
        data. It also creates `seq` and `mult` input files needed by the DTM.
        The bow_corpus is a list of lists (pertaining to documents), with each
        list containing a tuple (word_index, count) for each unique word in the
        corresponding document. The time slices are a list of the number of
        documents to be used in each time slice in the DTM. Thus, the corpus
        must also be ordered chronologically.

        Args:
            bow_corpus: Bag-of-words corpus corresponding to documents in
                chronological order. Each document is a list of tuples, with each
                tuple (word_index, count) corresponding to a unique word in the
                document.
            time_slices: List of number of documents to use for each time slice
                in the model.
            n_time_slices: Evenly divides the documents of the corpus across
                this number of time slices to be used in the `seq` file. Ignored if
                time_slices is passed explicitly.
        """
        self.bow_corpus = bow_corpus
        if time_slices is None:
            time_slices = [
                len(self.bow_corpus) // n_time_slices for _ in range(n_time_slices)
            ]
            # Distribute the remainder of docs evenly
            for ix in range(len(self.bow_corpus) % n_time_slices):
                time_slices[ix] += 1
        self.time_slices = time_slices
        self.n_time_slices = len(self.time_slices)
        self._init_model_inputs()
        return self._fit()

    def _fit(self):
        self._fit_dtm_model()
        self._model_fit = True
        return self

    @staticmethod
    def load(corpus_prefix: str, output_name: str):
        """Load outputs from a previously-fit model.

        Args:
            corpus_prefix: Directory and file name prefix to use when writing
                the input data. For example, if corpus_prefix is "foo/bar",
                the DTM input files are written to "foo/bar-seq.dat" and
                "foo/bar-mult.dat".
            output_name: Directory name used to write model output files to,
                relative to corpus_path.
        """
        m = DTM(corpus_prefix, output_name)
        model_info = m.read_model_info()
        m.n_topics = model_info["num_topics"]
        m.n_time_slices = model_info["seq_length"]
        m.bow_corpus, m.time_slices = m.read_corpus()
        m._model_fit = True
        return m

    def _fit_dtm_model(self):
        """Initialize DTM model parameters, run model, and write model outputs."""
        model = dtm(
            corpus_prefix=self.corpus_prefix,
            outname=self.output_path,
            initialize_lda=self.initialize_lda,
            lda_max_em_iter=self.lda_max_em_iter,
            lda_model_prefix=self._lda_model_prefix,
            mode=self.mode,
            model=self.model,
            ntopics=self.n_topics,
            output_table=self._output_table,
            params_file=self._params_file,
            start=self._start,
            top_chain_var=self.top_chain_var,
            top_obs_var=self.top_obs_var,
            influence_flat_years=self._influence_flat_years,
            influence_mean_years=self._influence_mean_years,
            influence_stdev_years=self._influence_stdev_years,
            max_number_time_points=self._max_number_time_points,
            resolution=self._resolution,
            sigma_c=self._sigma_c,
            sigma_cv=self._sigma_cv,
            sigma_d=self._sigma_d,
            sigma_l=self._sigma_l,
            time_resolution=self._time_resolution,
            rng_seed=self._rng_seed,
            fix_topics=self._fix_topics,
            forward_window=self._forward_window,
            lda_sequence_max_iter=self.lda_sequence_max_iter,
            lda_sequence_min_iter=self.lda_sequence_min_iter,
            normalize_docs=self._normalize_docs,
            save_time=self._save_time,
            lambda_convergence=self._lambda_convergence,
            alpha=self.alpha,
            end=self._end,
            heldout_corpus_prefix=self._heldout_corpus_prefix,
            heldout_time=self._heldout_time,
            lda_inference_max_iter=self.lda_inference_max_iter,
        )
        model.fit()

    def _read_seq_file(self, seq_path: Union[str, Path]) -> None:
        """Build time_slices list from DTM `seq` file."""
        seq = []
        with open(seq_path, "r") as f:
            for line in f:
                seq.append(int(line))
        self.n_time_slices, *self.time_slices = seq

    def _read_mult_file(self, mult_path: Union[str, Path]) -> None:
        """Build bow_corpus from DTM `mult` file."""
        corpus = []
        with open(mult_path, "r") as f:
            for line in f:
                n_words, *word_counts = line.split()
                corpus.append([tuple(map(int, wc.split(":"))) for wc in word_counts])
        self.bow_corpus = corpus

    def _write_seq_file(self, seq_path: Union[str, Path]) -> None:
        """Write DTM `seq` file from document numbers in time_slices list."""
        with open(seq_path, "w") as f:
            f.write(f"{len(self.time_slices)}\n")
            for ts in self.time_slices:
                f.write(f"{ts}\n")

    def _write_mult_file(self, mult_path: Union[str, Path]) -> None:
        """Write DTM `mult` file from bow corpus."""
        with open(mult_path, "w") as f:
            for c in self.bow_corpus:
                f.write(f"{len(c)}")
                for word, count in c:
                    f.write(f" {word}:{count}")
                f.write("\n")

    def _init_model_inputs(self) -> None:
        """Write DTM input data from BoW corpus."""
        if not self.corpus_path.is_dir():
            self.corpus_path.mkdir()
        self._write_seq_file(f"{self.corpus_prefix}-seq.dat")
        self._write_mult_file(f"{self.corpus_prefix}-mult.dat")
        self.model_init = True

    def read_topic_mixtures(self) -> np.ndarray:
        """Return matrix of topic mixtures for documents.

        Reads the DTM `gam.dat` file located in the DTM.output_path and
        transforms the data into a matrix of topic mixtures, where the
        proportion of topic n in document m is topic_mixtures[m, n].

        Returns:
            Matrix of topic mixtures
        """
        with open(f"{self.output_path}/lda-seq/gam.dat", "r") as f:
            topic_mixtures = np.fromfile(f, sep="\n")
        topic_mixtures = topic_mixtures.reshape(-1, self.n_topics)
        topic_mixtures /= topic_mixtures.sum(axis=1).reshape(-1, 1)
        return topic_mixtures

    def read_model_info(self) -> Dict[str, Union[int, float]]:
        """Read DTM model info (n_topics, num_terms, seq_length) and return as dict."""
        with open(f"{self.output_path}/lda-seq/info.dat") as f:
            info = {}
            for line in f:
                label, *value = line.split()
                info[label.lower()] = (
                    int(value[0]) if len(value) == 1 else list(map(float, value))
                )
        return info

    def read_topic_term_probabilities(self, topic_num: int) -> np.ndarray:
        """Read matrix of DTM topic term probabilities.

        Returns matrix of shape n_terms x n_time_slices for topic topic_num,
        where the probability of term n in topic topic_num at time t is
        topic_term_prob[n, t]

        Args:
            topic_num: Topic number to get probabilities for.

        Returns:
            Term probabilities for topic topic_num.
        """
        with open(
            f"{self.output_path}/lda-seq/topic-{topic_num:03d}-var-e-log-prob.dat"
        ) as f:
            topic_term_prob = np.fromfile(f, sep="\n")
        topic_term_prob = topic_term_prob.reshape(-1, self.n_time_slices)
        return np.exp(topic_term_prob)

    def read_doc_influence(self, time: int) -> np.ndarray:
        """Read DTM document influences at time slice time.

        Returns matrix of document influence at time slice time by topic, where
        time is based on the position of the document in the seq data. The
        influence of document n on topic m at the considered time slice will be
        doc_influence[n,m].  The document index will be based on its ordering
        in the `mult` file.

        Args:
            time: time slice number with respect to order in DTM `seq` file.

        Returns:
            Document influences for the specified time slice.
        """
        with open(f"{self.output_path}/lda-seq/influence-time-{time:03d}") as f:
            doc_influence = np.fromfile(f, sep="\n")
        doc_influence = doc_influence.reshape(-1, self.n_topics)
        return doc_influence
