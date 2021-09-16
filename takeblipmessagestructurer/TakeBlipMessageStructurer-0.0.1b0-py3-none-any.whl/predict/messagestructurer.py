import re

import typing as tp

import SentenceTokenizer as st
from TakeBlipNer.nermodel import CRF

Tags_dict = tp.Dict[str, str]
Core_dict = tp.Dict[str, tp.Any]


class MessageStructurer:
    def __init__(self, ner_model: CRF):
        self.ner_model = ner_model
        self.tokenizer = st.SentenceTokenizer()
        self.ner_dict = self.__create_ner_dict()
        self.postagging_dict = self.__create_postagging_dict()
        self.entity_pattern = re.compile("B-\w+(\sI-\w+)*")
        self.tag_pattern = re.compile("(ADV|ADJ|(VERB(\sVERB|\sPART)*)|PART)")

    def __create_ner_dict(self) -> Tags_dict:
        """Create a dictionary with the entities labels.

        :return: Dictionary with the label of the entity and the name of the entity.
        :rtype: Tags_dict
        """
        ner_dict = {'B-GEN': 'generic_entity',
                    'B-PERS': 'person',
                    'B-LOC': 'local',
                    'B-FIN': 'financial',
                    'B-DATE': 'date',
                    'B-ADDR': 'address',
                    'B-DOC': 'document',
                    'B-COMP': 'company',
                    'B-WD': 'week_day',
                    'B-PHONE': 'phone',
                    'B-MONEY': 'money',
                    'B-NUMBER': 'number',
                    'B-EMAIL': 'email',
                    'B-REL': 'relative',
                    'B-VOC': 'vocative'}

        return ner_dict

    def __create_postagging_dict(self) -> Tags_dict:
        """Create a dictionary with the postagging labels.

        :return: A dictionary with the label of POSTags as the key and value as 'postagging'.
        :rtype: Tags_dict

        """
        postagging_dict = {'ADJ': 'postagging',
                           'ADV': 'postagging',
                           'ART': 'postagging',
                           'CONJ': 'postagging',
                           'INT': 'postagging',
                           'VERB': 'postagging',
                           'NUM': 'postagging',
                           'PART': 'postagging',
                           'PON': 'postagging',
                           'PREP': 'postagging',
                           'PRON': 'postagging',
                           'SIMB': 'postagging',
                           'SUBS': 'postagging'}
        return postagging_dict

    @staticmethod
    def clean_tags(sentence: list,
                   tags: list,
                   ner: list,
                   remove: list,
                   remove_entities: bool = False) -> tp.Tuple[str, str, str]:
        """Remove words of the sentence based on a list of tags

        :param sentence: List of words in a sentence.
        :type sentence: list
        :param tags: List of POSTags of words in a sentence.
        :type tags: list
        :param ner: List of entities of words in a sentence.
        :type ner: list
        :param remove: List of tags to be remove. Can be POSTags or entities.
        :type remove: list
        :param remove_entities: True if the tags to be remove are entities.
        :type remove_entities: bool
        :return: A tuple with the processed sentence, POSTags and entities.
        :rtype: tp.Tuple[str, str, str]
        """
        split_msg = sentence.copy()
        split_tags = tags.copy()
        split_ner = ner.copy()
        if remove_entities:
            values_lst = reversed(list(enumerate(ner)))
        else:
            values_lst = reversed(list(enumerate(tags)))
        for ind, tag in values_lst:
            if tag in remove:
                split_msg.pop(ind)
                split_tags.pop(ind)
                split_ner.pop(ind)
        return ' '.join(split_msg), ' '.join(split_tags), ' '.join(split_ner)

    def __find_pattern(self,
                       tags: str,
                       message: str,
                       is_postag: bool) -> tp.List[Core_dict]:
        """Return a list with the dictionary of patterns founded.

        The patterns are entities or POSTags of the label ADJ, VERB, PART, ADV.

        Output example:
        For entity:

        {'value': 'Segunda via',
        'lowercase_value': 'segunda via',
        'postags': 'B-FIN',
        'message_start': 0,
        'message_end': 1,
        'type' : 'financial'}

        For POSTags:
        {'value': 'Quero pagar',
        'lowercase_value': 'quero pagar',
        'postags': 'VERB',
        'message_start': 0,
        'message_end': 1,
        'type': 'postagging'}

        :param tags: String with the labels. Can be POSTags or entities.
        :type tags: str
        :param message: Message string.
        :type message: str
        :param is_postag: The pattern is a postag pattern.
        :type is_postag: bool
        :return: List with the dictionary of the patterns founded.
        :rtype: tp.List[Core_dict]
        """

        if is_postag:
            pattern = self.tag_pattern
            class_dict = self.postagging_dict
        else:
            pattern = self.entity_pattern
            class_dict = self.ner_dict

        splitted_message = message.split()
        data_dicts_list = []
        for match in pattern.finditer(tags):
            found_dict = {}
            message_start = len(tags[:match.start()].split())
            message_end = len(tags[:match.end()].split())
            word_type = tags[match.start(): match.end()].split()[0]
            found_word = ' '.join(splitted_message[message_start: message_end])
            found_dict['value'] = found_word
            found_dict['lowercase_value'] = found_word.lower()
            found_dict['postags'] = word_type
            found_dict['message_start'] = message_start
            found_dict['message_end'] = message_end
            found_dict['type'] = class_dict[word_type]
            data_dicts_list.append(found_dict)
        return data_dicts_list

    @staticmethod
    def get_postags(found_items: tp.List[Core_dict],
                    tags: str) -> tp.List[Core_dict]:
        """Get the postags  of the entities

        :param found_items: List of dictionary with the entities founded.
        :type found_items: tp.List[Core_dict]
        :param tags: POSTags of the sentence.
        :type tags: str
        :return: The input list with the dictionary with the postags of the entities.
        :rtype: tp.List[Core_dict]
        """
        for item in found_items:
            start = item['message_start']
            end = item['message_end']
            postags_list = tags.split()[start:end]
            item['postags'] = ' '.join(postags_list)
        return found_items

    @staticmethod
    def structure_output(message_tags: list,
                         sentence: str,
                         sentence_id: tp.Optional[int] = None) -> Core_dict:
        """Structure the core of the sentences.

        :param message_tags: A list with the dictionary with the tags of the words.
        :type message_tags: list
        :param sentence: String of the sentence.
        :type sentence: str
        :param sentence_id: The id of the message, used on batch prediction. Default is None.
        :type sentence_id: tp.Optional[int]
        :return: Dictionary with the core of the message.
        :rtype: Core_dict
        """
        sorted_content = sorted(message_tags,
                                key=lambda row: row['message_start'])
        sorted_content = [{key: value for (key, value) in item_dict.items() if
                           not key.startswith('message')} for item_dict in
                          sorted_content]
        output = {
            **({'id': sentence_id} if sentence_id else {}),
            'filtered_message': sentence,
            'lowercase_filtered_message': sentence.lower(),
            'content': sorted_content
        }
        return output

    def __get_message_dicts(self,
                            input_sentence: str,
                            input_tags: str,
                            input_ner: str,
                            tags_to_remove: list,
                            filter_entity: tp.Optional[list] = None,
                            sentence_id: tp.Optional[int] = None) -> Core_dict:
        """Return the dictionary with the core of the message

        :param input_sentence: The message to be structured.
        :type input_sentence: str
        :param input_tags: The POSTags labels of the message.
        :type input_tags: str
        :param input_ner: The entities labels of the message.
        :type input_ner: str
        :param tags_to_remove: List of POSTags to be removed.
        :type tags_to_remove: list
        :param filter_entity: List with the entities to be removed. Default is None.
        :type filter_entity: tp.Optional[list]
        :param sentence_id: The id of the message, used on batch prediction. Default is None.
        :type sentence_id: tp.Optional[int]
        :return: Dictionary with the core information of the sentence.
        :rtype: Core_dict
        """
        sentence_lst = input_sentence.split()
        tags_lst = input_tags.split()
        ner_lst = input_ner.split()
        sentence, tags, ner = self.clean_tags(sentence=sentence_lst,
                                              tags=tags_lst,
                                              ner=ner_lst,
                                              remove=tags_to_remove)
        if filter_entity:
            sentence, tags, ner = self.clean_tags(sentence=sentence_lst,
                                                  tags=tags_lst,
                                                  ner=ner_lst,
                                                  remove=filter_entity,
                                                  remove_entities=True)
        message_ner_list = self.__find_pattern(tags=ner,
                                               message=sentence,
                                               is_postag=False)
        message_tag_list = self.__find_pattern(tags=tags,
                                               message=sentence,
                                               is_postag=True)
        message_ner_list = self.get_postags(message_ner_list, tags)
        message_dict = message_ner_list + message_tag_list
        structured_output = self.structure_output(message_tags=message_dict,
                                                  sentence=sentence,
                                                  sentence_id=sentence_id)

        return structured_output

    def structure_message(self,
                          sentence: str,
                          tags_to_remove: list,
                          entities_to_remove: tp.Optional[list] = None,
                          use_pre_processing: bool = True) -> Core_dict:
        """Structures the message of a sentence

        :param sentence: The message to be structured.
        :type sentence: str
        :param tags_to_remove: List of POSTags to be removed.
        :type tags_to_remove: list
        :param entities_to_remove: List with the entities to be removed. Default is None.
        :type entities_to_remove: tp.Optional[list]
        :param use_pre_processing: Whether to pre process input data. Default True.
        :type use_pre_processing: bool
        :return: Dictionary with the core information of the sentence.
        :rtype: Core_dict
        """
        input_sentence, tags, ner = self.ner_model.predict_line(sentence,
                                                                use_pre_processing=use_pre_processing)
        return self.__get_message_dicts(input_sentence=input_sentence,
                                        input_tags=tags,
                                        input_ner=ner,
                                        tags_to_remove=tags_to_remove,
                                        filter_entity=entities_to_remove)

    def structure_message_batch(self,
                                sentences: list,
                                tags_to_remove: list,
                                entities_to_remove: tp.Optional[list] = None,
                                use_pre_processing: bool = True,
                                batch_size: int = 50,
                                shuffle: bool = True) -> tp.List[Core_dict]:
        """Structures the messages of a set of sentences

        :param sentences: List with the messages to be structured.
        :type sentences: list
        :param tags_to_remove: List of POSTags to be removed.
        :type  tags_to_remove: list
        :param entities_to_remove: List with the entities to be removed. Default is None.
        :type entities_to_remove: tp.Optional[list]
        :param use_pre_processing: Whether to pre process input data. Default True.
        :type use_pre_processing: bool
        :param batch_size: Batch size.
        :type batch_size: int
        :param shuffle: Whether to shuffle the dataset. Default True.
        :type shuffle: bool
        :return: List with the dictionary with the core information of the sentences.
        :rtype: tp.List[Core_dict]
        """
        structured_batches = []
        predictions_list = self.ner_model.predict_batch(
            filepath='',
            sentence_column='',
            batch_size=batch_size,
            shuffle=shuffle,
            use_pre_processing=use_pre_processing,
            output_lstm=False,
            sentences=sentences)

        for prediction in predictions_list:
            structured_batches.append(self.__get_message_dicts(
                input_sentence=prediction['processed_sentence'],
                input_tags=prediction['postaggings'],
                input_ner=prediction['entities'],
                sentence_id=prediction['id'],
                tags_to_remove=tags_to_remove,
                filter_entity=entities_to_remove))
        return structured_batches
