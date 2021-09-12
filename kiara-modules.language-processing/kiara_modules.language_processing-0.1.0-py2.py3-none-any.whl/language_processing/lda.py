# -*- coding: utf-8 -*-
import logging
import re
import typing

from kiara import KiaraModule
from kiara.data import ValueSet
from kiara.data.values import ValueSchema


class LDAModule(KiaraModule):
    """Perform Latent Dirichlet Allocation on a tokenized corpus."""

    _module_type_name = "LDA"

    def create_input_schema(
        self,
    ) -> typing.Mapping[
        str, typing.Union[ValueSchema, typing.Mapping[str, typing.Any]]
    ]:
        inputs: typing.Dict[str, typing.Dict[str, typing.Any]] = {
            "tokens_array": {"type": "array", "doc": "The text corpus."},
            "num_topics": {
                "type": "integer",
                "doc": "The number of topics.",
                "default": 7,
            },
            "compute_coherence": {
                "type": "boolean",
                "doc": "Whether to train the model without coherence calculation.",
                "default": False,
            },
        }
        return inputs

    def create_output_schema(
        self,
    ) -> typing.Mapping[
        str, typing.Union[ValueSchema, typing.Mapping[str, typing.Any]]
    ]:

        outputs = {
            "topic_model": {
                "type": "table",
                "doc": "A table with 'topic_id' and 'words' columns (also 'num_topics', if coherence calculation was switched on).",
            }
        }
        return outputs

    def compute_with_coherence(self, corpus, id2word, corpus_model):

        import gensim
        import pandas as pd
        from gensim.models import CoherenceModel
        from pyarrow import Table

        topics_nr = []
        coherence_values_gensim = []
        models = []
        models_idx = [x for x in range(3, 20)]
        for num_topics in range(3, 20):
            # fastest processing time preset (hypothetically less accurate)
            model = gensim.models.ldamulticore.LdaMulticore(
                corpus, id2word=id2word, num_topics=num_topics, eval_every=None
            )
            # slower processing time preset (hypothetically more accurate) approx 20min for 700 short docs
            # model = gensim.models.ldamulticore.LdaMulticore(corpus, id2word=id2word, num_topics=num_topics, chunksize=1000, iterations = 200, passes = 10, eval_every = None)
            # slowest processing time preset approx 35min for 700 short docs (hypothetically even more accurate)
            # model = gensim.models.ldamulticore.LdaMulticore(corpus, id2word=id2word, num_topics=num_topics, chunksize=2000, iterations = 400, passes = 20, eval_every = None)
            models.append(model)
            coherencemodel = CoherenceModel(
                model=model, texts=corpus_model, dictionary=id2word, coherence="c_v"
            )
            coherence_value = coherencemodel.get_coherence()
            coherence_values_gensim.append(coherence_value)
            topics_nr.append(str(num_topics))

        df_coherence = pd.DataFrame(topics_nr, columns=["Number of topics"])
        df_coherence["Coherence"] = coherence_values_gensim

        # Create list with topics and topic words for each number of topics
        num_topics_list = []
        topics_list = []
        for i in range(len(models_idx)):
            numtopics = models_idx[i]
            num_topics_list.append(numtopics)
            model = models[i]
            topic_print = model.print_topics(num_words=30)
            topics_list.append(topic_print)

        df_coherence_table = pd.DataFrame(columns=["topic_id", "words", "num_topics"])

        idx = 0
        for i in range(len(topics_list)):
            for j in range(len(topics_list[i])):
                df_coherence_table.loc[idx] = ""
                df_coherence_table["topic_id"].loc[idx] = j + 1
                df_coherence_table["words"].loc[idx] = ", ".join(
                    re.findall(r'"(\w+)"', topics_list[i][j][1])
                )
                df_coherence_table["num_topics"].loc[idx] = num_topics_list[i]
                idx += 1

        return Table.from_pandas(df_coherence_table, preserve_index=False)

    def process(self, inputs: ValueSet, outputs: ValueSet) -> None:

        import gensim
        import pandas as pd
        from gensim import corpora
        from pyarrow import Table

        logging.getLogger("gensim").setLevel(logging.ERROR)
        tokens_array = inputs.get_value_data("tokens_array")
        tokens = tokens_array.to_pylist()
        num_topics = inputs.get_value_data("num_topics")

        compute_coherence = inputs.get_value_data("compute_coherence")
        id2word = corpora.Dictionary(tokens)
        corpus = [id2word.doc2bow(text) for text in tokens]

        model = gensim.models.ldamulticore.LdaMulticore(
            corpus, id2word=id2word, num_topics=num_topics, eval_every=None
        )
        topic_print_model = model.print_topics(num_words=30)

        if not compute_coherence:
            df = pd.DataFrame(topic_print_model, columns=["topic_id", "words"])
            # TODO: create table directly
            result = Table.from_pandas(df)
        else:
            result = self.compute_with_coherence(
                corpus=corpus, id2word=id2word, corpus_model=tokens
            )

        outputs.set_value("topic_model", result)
