from rouge import Rouge


class RougeHandler(object):

    rouge = Rouge()

    @classmethod
    def batch_get_rouge_score(cls, generated_list, ground_truth_list):
        """Get rouge metric score.

        Args:
            generated_list (List[str]): list of strings splitted by space
            ground_truth_list (List[str]): list of strings splitted by space

        Returns:
            dict, rouge 1-2-l score, like:
            {
                'rouge-1': {'f': 0.4786, 'p': 0.6363, 'r': 0.3835},
                'rouge-2': {'f': 0.2608, 'p': 0.3488, 'r': 0.2083},
                'rouge-l': {'f': 0.4470, 'p': 0.5277, 'r': 0.3877},
            }
        """

        def _avg(arr):
            return sum(arr) / (len(arr) + 1e-12)

        rouge_score = cls.rouge.get_scores(
            hyps=generated_list,
            refs=ground_truth_list,
            ignore_empty=True,
            avg=True,
        )

        rouges = ["rouge-1", "rouge-2", "rouge-l"]

        rouge_score["rouge-avg"] = {
            "f": _avg([rouge_score[x]["f"] for x in rouges]),
            "p": _avg([rouge_score[x]["p"] for x in rouges]),
            "r": _avg([rouge_score[x]["r"] for x in rouges]),
        }

        return rouge_score
