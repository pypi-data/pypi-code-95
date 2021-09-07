#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
import logging
import re
from pymorphy2 import MorphAnalyzer

from django.utils.timezone import now
# from django.utils.translation import get_language

from textrank.models import Weight


logger = logging.getLogger(__name__)

# Все объекты содержатся в памяти и обновляются из базы данных при
# необходимости.
GROUPS = {
    # 1: {'name': 'Группа 1', 'code': '001'},
    # 2: {'name': 'Группа 2', 'code': '002'},
}

# Значения для автоматического обновления данных.
INFO = {
    # 'last_id': None,
    # 'last_updated': None,
}


class Word(str):
    """
    Расширенный класс строки для хранения идентификатора слов в базе.
    """
    def __new__(cls, keyword, *args, **kw):
        self = str.__new__(cls, keyword.word)
        self.object_id = keyword.id
        self.is_chain = keyword.is_chain
        self.chainwords = keyword.chainwords
        self.is_cover = keyword.is_cover
        self.coverwords = keyword.coverwords
        return self


class WordsDict(dict):
    """
    Кючом является слово (или сочетание), а значением - словарь групп со
    значением веса, например: {Word('слово'): {1: 1, 2: 2}}.
    """
    # Словарь обратного сопоставления слов по их идентификатору.
    objects = {}


# Ключевые слова - это одиночные слова.
KEYWORDS = WordsDict()
# Цепочка слов - слова, разделённые нижним подчёркиванием, все эти слова
# идут в строгой последовательности друг за другом.
CHAINWORDS = WordsDict()
# Покрытие слов - слова, разделённые знаком +, все эти слова
# должны находится в любом месте текста, в любой последовательности.
COVERWORDS = WordsDict()


def check_updates():
    """Проверяет и подтягивает обновления из базы в память."""

    start = now()
    logger.info('start check_updates()')

    last_updated = INFO.get('last_updated')
    last_id = INFO.get('last_id')
    logger.debug('last_updated = %s, last_id = %s', last_updated, last_id)
    qs = Weight.objects.select_related('group', 'keyword')
    if last_updated:
        qs = qs.filter(updated__gt=last_updated)
    qs = qs.order_by('updated', 'id')
    for weight in qs:
        last_id = weight.id
        last_updated = weight.updated
        gid = weight.group_id
        word = Word(weight.keyword)
        world_id = word.object_id
        # Сначала удаляем из 2-х других словарей старое значение слова.
        # Это необходимо, когда слово было одиночным, а потом изменилось на
        # сочетание или наоборот.
        if word.is_chain:
            dst_dict = CHAINWORDS
            old_dicts = (KEYWORDS, COVERWORDS)
        elif word.is_cover:
            dst_dict = COVERWORDS
            old_dicts = (KEYWORDS, CHAINWORDS)
        else:
            dst_dict = KEYWORDS
            old_dicts = (CHAINWORDS, COVERWORDS)
        for dic in old_dicts:
            if world_id in dic.objects:
                old_word = dic.objects[world_id]
                dic.pop(old_word)
                dic.objects.pop(world_id)
                logger.info('removed old word: %s', old_word)
        # Когда само слово или сочетание изменилось, то нужно удалить старое
        # значение. Для этого ищем его по идентификатору в словаре назначения.
        old_word = dst_dict.objects.get(world_id)
        if old_word and old_word != word:
            dst_dict.pop(old_word)
            dst_dict.objects.pop(world_id)
            logger.info('removed old word: %s', old_word)
        # Когда вес стал неактивным, то убираем группу из значения ключевого
        # слова, но само слово остаётся до тех пор, пока есть группы.
        if not weight.is_active:
            logger.info('update not active: %s', weight)
            if word in dst_dict:
                groups = dst_dict[word]
                if gid in groups:
                    groups.pop(gid)
                # Удаляем слово из словаря.
                if not groups:
                    dst_dict.pop(word)
        # Добавляем или обновляем активное слово или сочестание.
        else:
            logger.info('update active: %s', weight)
            if word in dst_dict:
                dst_dict[word][gid] = weight.value
            else:
                dst_dict[word] = {gid: weight.value}
            group = weight.group
            GROUPS[gid] = {'name': group.name, 'code': group.code}
    INFO['last_updated'] = last_updated
    INFO['last_id'] = last_id
    logger.debug('set last_updated = %s, last_id = %s', last_updated, last_id)

    utime = (now() - start).total_seconds()
    logger.info('update time = %s sec', utime)
    logger.info(
        'length KEYWORDS = %s, CHAINWORDS = %s, COVERWORDS = %s',
        len(KEYWORDS), len(CHAINWORDS), len(COVERWORDS)
    )
    return utime


pattern = re.compile(r'[\w\-]+')


def words_iterator(text):
    for w in pattern.findall(text):
        yield w.lower()


def analyze_text(text, morphology=None):
    if morphology is None:
        # Для ветки master доступно указание языка.
        # morphology = MorphAnalyzer(lang=get_language()).parse
        # Но в текущей стабильной версии 0.8 этого нет.
        morphology = MorphAnalyzer().parse

    if not morphology:
        logger.warn('no morphology')

    utime = check_updates()
    start = now()

    # Слова должны быть в оригинальной последовательности.
    words = list(words_iterator(text))

    if not GROUPS or not (KEYWORDS or CHAINWORDS or COVERWORDS):
        logger.warn('no groups and no key|chain|cover words')
        atime = (now() - start).total_seconds()
        logger.info('analyze time = %s', atime)
        return {
            'group': {},
            'found': {},
            'words': words,
            'morph': [],
            'other': [],
            'utime': utime,
            'atime': atime,
        }

    groups = {}
    score = {}

    def add(dic, word):
        for gid, weight in dic[word].items():
            if gid not in groups:
                groups[gid] = {}
                score[gid] = 0
            group = groups[gid]
            if word not in group:
                group[word] = 0
            group[word] += weight
            score[gid] += weight
            logger.debug('add "%s=%s" to %s', word, weight, GROUPS[gid])

    morph = set()
    # Поиск ключевых слов.
    logger.debug('SEARCH BY KEY')
    for word in words:
        if word in KEYWORDS:
            logger.debug('word "%s" in keywords', word)
            add(KEYWORDS, word)
        elif word.isdigit():
            logger.debug('word "%s" is digit, passed', word)
            pass
        elif morphology:
            logger.debug('checking "%s" by morphology', word)
            skip = set([word])
            for parse in morphology(word):
                normal_form = parse.normal_form
                if normal_form in skip:
                    continue
                morph.add(normal_form)
                if normal_form in KEYWORDS:
                    skip.add(normal_form)
                    add(KEYWORDS, normal_form)
    # Поиск цепочек слов.
    logger.debug('SEARCH BY CHAIN')
    full_text_words = ' '.join(words)
    for chainword, _groups in CHAINWORDS.items():
        substring = ' '.join(chainword.chainwords)
        if substring in full_text_words:
            logger.debug('substing "%s" in text', substring)
            add(CHAINWORDS, chainword)
        # elif morphology:
        #     logger.debug('checking "%s" by morphology', text)
    # Поиск покрытия слов.
    logger.debug('SEARCH BY COVER')
    for coverword, _groups in COVERWORDS.items():
        coverwords = coverword.coverwords
        found = 0
        for w in coverwords:
            if w in words:
                found += 1
                logger.debug('word "%s" in words', w)
            elif w.isdigit():
                logger.debug('word "%s" is digit, passed', w)
                pass
            elif morphology:
                logger.debug('checking "%s" by morphology', w)
                skip = set([w])
                for parse in morphology(w):
                    for lexeme in parse.lexeme:
                        variant_word = lexeme.word
                        if variant_word in skip:
                            continue
                        morph.add(variant_word)
                        if variant_word in words:
                            skip.add(variant_word)
                            found += 1
                            logger.debug('word "%s" in words', variant_word)
                            break

        if found == len(coverwords):
            logger.debug('words "%s" in coverwords', coverword)
            add(COVERWORDS, coverword)

    # Подсчёт победителя.
    win_gid, win = 0, 0
    for k, v in score.items():
        if v > win:
            win_gid, win = k, v
        # При одинаковых значениях выигрывает группа с меньшим ID.
        elif v == win and k < win_gid:
            win_gid, win = k, v

    def group_data(gid):
        data = GROUPS[gid].copy()
        data['id'] = gid
        data['score'] = score[gid]
        return data

    # Формирование результата.
    if win_gid:
        group = group_data(win_gid)
        found = groups[win_gid]
        other = [{'group': group_data(k), 'found': v}
                 for k, v in groups.items() if k != win_gid]
    else:
        group = {}
        found = {}
        other = []
    atime = (now() - start).total_seconds()
    logger.info('analyze time = %s', atime)
    return {
        'group': group,
        'found': found,
        'words': words,
        'morph': list(morph),
        'other': other,
        'utime': utime,
        'atime': atime,
    }
