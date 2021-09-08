""" Pattern and template based chatbot dialog engines """
import logging
import os
import spacy
import numpy as np

from qary.constants import DATA_DIR
from qary.etl.dialog_parse import DialogTurns

# FIXME: make this a config option
DEFAULT_STATE_NAME = '__default__'
FINISH_STATE_NAME = 'finish'
MULTIPLE_CATS_PRBLM = os.path.join(DATA_DIR, 'yes_no/multiple_cats_problem.txt')
INTERN_QUIZ = os.path.join(DATA_DIR, 'yes_no/intern_quiz.txt')
MIN_SIMILARITY = 0.7

log = logging.getLogger(__name__)

# FIXME: convert to standard qary style nlp
nlp = spacy.load('en_core_web_md')


def normalize_docvectors(docvectors):
    """Convert a table (2D matrix) of row-vectors into a table of normalized row-vectors
    borrowed from faqs.py

    >>> vecs = normalize_docvectors([[1, 2, 3], [4, 5, 6], [0, 0, 0], [-1, 0, +2]])
    >>> vecs.shape
    (4, 3)
    >>> np.linalg.norm(vecs, axis=1).round()
    array([1., 1., 0., 1.])
    """
    docvectors = np.array(docvectors)
    log.info(f'docvectors.shape: {docvectors.shape}')
    norms = np.linalg.norm(docvectors, axis=1)
    iszero = norms <= 0
    log.info(f'norms.shape: {norms.shape}')
    norms_reshaped = norms.reshape(-1, 1).dot(np.ones((1, docvectors.shape[1])))
    log.info(f'norms_reshaped.shape: {norms_reshaped.shape}')
    if np.any(iszero):
        log.info(
            f'Some doc vectors are zero like this first one: docvectors[{iszero},:] = {docvectors[iszero,:]}'
        )
    norms_reshaped[iszero, :] = 1
    normalized_docvectors = docvectors / norms_reshaped
    log.info(f'normalized_docvectors.shape: {normalized_docvectors.shape}')
    assert normalized_docvectors.shape == docvectors.shape
    return normalized_docvectors


def vector_dict(statements, keys=None):
    """Borrowed from glossaries.py"""
    statements = [str(t) if t else '' for t in statements]
    keys = statements if keys is None else list(keys)
    vector_list = []
    log.info(f'Computing doc vectors for {len(statements)} statements...')
    for k, term in zip(keys, statements):
        vec = nlp(
            term
        ).vector  # s can sometimes (rarely) be a float because of pd.read_csv (df_titles)
        vec /= np.linalg.norm(vec) or 1.0
        mask_zeros = np.abs(vec) > 0
        if mask_zeros.sum() < len(mask_zeros):
            log.debug(f'BAD VEC: {term} [0]*{mask_zeros.sum()}')
        vector_list.append((k, vec))

    # TODO: make sure this isn't needed
    # mask = np.array([bool(stmt) and (len(str(stmt).strip()) > 0) for stmt, _ in vector_list])
    docvectors = [vector for statement, vector in vector_list]
    vectors_norm = normalize_docvectors(docvectors)
    vector_list_new = []
    for (statement, _), vector in zip(vector_list, vectors_norm):
        vector_list_new.append((statement, vector))
    # vector_list_new = np.array([qv for qv, m in zip(question_vectors, mask) if m])
    return dict(vector_list_new)


def load():
    """Loads the skill data file and creates a vector"""


class Skill:
    r"""Skill for factqest type scenarios"""

    def __init__(self, datafile=None):
        """ """
        global nlp
        self.nlp = nlp
        datafile = datafile or MULTIPLE_CATS_PRBLM
        dialog_turns = DialogTurns(datafile)
        dialog_turns.parse_dialog_lines()
        self.turns = dialog_turns.turns
        player_replies = ['\n'.join(turn['player']) for turn in self.turns]
        self.player_replies_vector = np.array(list(vector_dict(player_replies).values()))
        self.state = None
        return

    def reply(self, statement, context=None):
        r"""Suggest responses to a user statement string according to a quest script

        Examples:
            >>> s = Skill()
            >>> s.reply(None) # doctest: +ELLIPSIS
            [(1.0, 'A woman went on ...Ready?')]
            >>> s.reply('Yes') # doctest: +ELLIPSIS
            [(1.0, 'Great! Ask me your first question...puzzle.')]
            >>> s.reply('Did the cat go missing and have babies and came back?') # doctest:+ELLIPSIS
            [(1.0, 'It appears that ...questions?')]
            >>> s.reply('Did he think that the lady would recognize her cat among these 8 cats?') # doctest: +ELLIPSIS
            [(1.0, 'Yes.\nKudos! ...crack another one.')]
        """
        if not self.state:
            response = '\n'.join(self.turns[0]['bot'])
            self.state = 'welcome'
        elif self.state == 'welcome':
            if statement.lower().startswith('yes'):
                response = '\n'.join(self.turns[1]['bot'])
                self.state = 'play'
            elif statement.lower().startswith('no'):
                self.state = None
                response = 'Exiting, bye!'
            else:
                response = 'Please answer yes or no'
        else:
            question_vector = self.nlp(statement).vector
            question_vector /= np.linalg.norm(question_vector)
            question_similarities = self.player_replies_vector.dot(question_vector.reshape(-1, 1))
            mask = np.array(question_similarities).flatten() >= MIN_SIMILARITY
            if sum(mask) >= 1:
                idx = question_similarities.argmax()
                turn = self.turns[idx]
                if turn['state'] == FINISH_STATE_NAME:  # game over
                    self.state = None
                response = '\n'.join(turn['bot'])
            else:
                response = 'Irrelevant'
        return [(1.0, response)]


# def main():
#     b = Skill()
#     response = b.reply(None)
#     response = b.reply('yes')
#     response = b.reply('Did the cat go missing and have babies and came back?')
#     response = b.reply('Did he think that the lady would recognize her cat among these 8 cats?')

#     return


# if __name__ == '__main__':
#     main()


# def xtest_current():
#     s = Skill()
#     response = s.reply(None)
#     print(response)
#     return
