import json
import math
from typing import List, Optional

import regex as re
from lang_trans.arabic import buckwalter
from pelecanus import PelicanJson

from .entity_mapper import EntityMapper
from .fact import Fact
from .parsers import AddressParser, ContactEmailNamePairParser, ContactEmailParser, ContactPhoneParserHighPrecision, \
    ContactPhoneParserHighRecall, ContactPhoneParserStrict
from .russian_transliterator import Transliterate


russian_transliterator = Transliterate()


class Document:
    """
    Class for isolating the different values of MLP like pos_tags, lemmas etc
    and their formatting. For adding/changing the values, create a function with the name
    of the analyzer like "forms()" that handles populating the __forms attribute and a "get_forms()"
    function to format it. In the end add "get_forms()" to the to_json() function.
    """
    langs_to_transliterate = ["ru", "ar"]

    FACT_NAME_EMAIL = "EMAIL"
    FACT_NAME_ADDRESS = "ADDR"
    FACT_NAME_PHONE_HIGH_RECALL = "PHONE_high_recall"
    FACT_NAME_PHONE_HIGH_PRECISION = "PHONE_high_precision"
    FACT_NAME_PHONE_STRICT = "PHONE_strict"
    FACT_NAMES_NER = ("PER", "ORG", "GPE", "LOC")
    FACT_NAME_NAMEMAIL = "NAMEMAIL"
    FACT_NAME_BOUNDED = "BOUNDED"

    KNOWN_ENTITIES = (FACT_NAME_EMAIL, FACT_NAME_ADDRESS, FACT_NAME_PHONE_STRICT, FACT_NAME_NAMEMAIL) + FACT_NAMES_NER

    CLOSE_FACT_DISTANCE = 150


    def __init__(
            self,
            original_text: str,
            dominant_language_code: str,
            analysis_lang: str,
            stanza_sentences: [list],
            stanza_entities,
            concat_resources: dict,
            entity_mapper: Optional[EntityMapper] = None,
            doc_path: str = "text",
            json_doc: dict = None,
            analyzers: list = [],
            error: str = "",
    ):

        self.original_text = original_text
        self.doc_path = doc_path
        self.analyzers = analyzers
        self.dominant_language_code = dominant_language_code
        self.analysis_lang = analysis_lang
        self.error = error
        self.json_doc = json_doc

        self.entity_mapper = entity_mapper
        self.stanza_sentences = stanza_sentences
        self.stanza_words = [word for sentence in self.stanza_sentences for word in sentence]
        self.stanza_entities = stanza_entities

        self.concat_resources = concat_resources

        self.__words = []
        self.__lemmas = []
        self.__pos_tags = []
        self.__transliteration = []
        self.__texta_facts: List[Fact] = []

        self.__handle_existing_facts()
        self.words()


    def __get_doc_path(self, field: str) -> str:
        """
        :param field: Whether the doc_path uses the text or lemmas field.
        :return: MLP representation of the doc_path
        """
        content = f"{self.doc_path}_mlp.{field}"
        return content


    def __handle_existing_facts(self):
        """
        Add existing texta_facts inside the document into the private
        fact container variable so that they wouldn't be overwritten.
        """
        if self.json_doc and "texta_facts" in self.json_doc:
            existing_facts = self.json_doc.get("texta_facts", [])
            facts = Fact.from_json(existing_facts)
            for fact in facts:
                self.add_fact(fact)


    @staticmethod
    def handle_null_values_in_facts(facts: List[dict]):
        container = []
        if facts:
            for fact in facts:
                new_fact = {key: value for key, value in fact.items() if value is not None}
                container.append(new_fact)
        return container


    @staticmethod
    def remove_duplicate_facts(facts: List[dict]):
        if facts:
            facts = Document.handle_null_values_in_facts(facts)
            set_of_jsons = {json.dumps(fact, sort_keys=True, ensure_ascii=False) for fact in facts}
            without_duplicates = [json.loads(unique_fact) for unique_fact in set_of_jsons]
            return without_duplicates
        else:
            return []


    def facts_to_json(self) -> dict:
        facts = [fact.to_json() for fact in self.__texta_facts]
        unique_facts = Document.remove_duplicate_facts(facts)
        return {"texta_facts": unique_facts}


    def add_fact(self, fact: Fact):
        self.__texta_facts.append(fact)


    @staticmethod
    def edit_doc(doc: dict, doc_path: str, new_value) -> dict:
        """
        :param doc: Original dictionary into which you add content.
        :param doc_path: Dot separated field paths to the nested value you wish to add.
        :param new_value: Value you wish to add into the nested path.
        :return: Dictionary with the new value added into it according to the path.
        """
        wrapper = PelicanJson(doc)
        path = doc_path.split(".")
        wrapper.set_nested_value(path, new_value, force=True)
        return wrapper.convert()


    def document_to_json(self, use_default_doc_path=True) -> dict:
        """
        :param use_default_doc_path: Normal string values will be given the default path for facts but for dictionary input you already have them.
        """
        list_of_path_keys = self.doc_path.split(".")
        root_key = "{}_mlp".format(list_of_path_keys[-1])
        path_to_mlp = list_of_path_keys[:-1] + [root_key] if len(list_of_path_keys) > 1 else [root_key]
        mlp_result = self.to_json(use_default_doc_path)
        nested_dict_wrapper = PelicanJson(self.json_doc)
        nested_dict_wrapper.set_nested_value(path_to_mlp, mlp_result["text"], force=True)
        nested_dict_wrapper.set_nested_value(["texta_facts"], mlp_result["texta_facts"], force=True)

        return nested_dict_wrapper.convert()


    def to_json(self, use_default_doc_path=True) -> dict:
        container = dict()
        container["text"] = self.get_words(ssplit="sentences" in self.analyzers)
        texta_facts = self.facts_to_json()
        container["language"] = {
            "detected": self.dominant_language_code,
            "analysis": self.analysis_lang
        }
        if self.error:
            container["error"] = self.error

        if "lemmas" in self.analyzers:
            container["lemmas"] = self.get_lemma()
        if "pos_tags" in self.analyzers:
            container["pos_tags"] = self.get_pos_tags()
        # if "sentiment" in self.analyzers: container["sentiment"] = self.get_sentiment()
        if "transliteration" in self.analyzers and self.__transliteration:
            container["transliteration"] = self.get_transliteration()
        if use_default_doc_path:
            for fact in texta_facts["texta_facts"]:
                fact["doc_path"] = "text.text"
        return {"text": container, **texta_facts}


    def lemmas(self):
        for sent in self.stanza_sentences:
            self.__lemmas.append([word.lemma.replace("_", "") if word and word.lemma else "X" for word in sent])


    def get_lemma(self) -> str:
        sentences = []
        for sent_lemmas in self.__lemmas:
            sentences.append(" ".join([a.strip() for a in sent_lemmas]))

        if "sentences" in self.analyzers:
            return "\n".join(sentences)
        else:
            return " ".join(sentences)


    def words(self):
        for sent in self.stanza_sentences:
            self.__words.append([word.text for word in sent])


    def sentences(self):
        pass


    def get_words(self, ssplit=False) -> str:
        if ssplit:
            return "\n".join([" ".join(sent_words) for sent_words in self.__words])
        else:
            return " ".join([" ".join(sent_words) for sent_words in self.__words])


    def pos_tags(self):
        self.__pos_tags = [word.xpos if word and word.xpos and word.xpos != "_" else "X" if word.xpos == "_" else "X"
                           for word in self.stanza_words]


    def get_pos_tags(self) -> str:
        return " ".join([a.strip() for a in self.__pos_tags])


    def entities(self):
        """
        Retrieves list-based entities.
        """
        text = self.get_words()
        lemmas = self.get_lemma()

        hits = self.entity_mapper.map_entities(text)
        lemma_hits = self.entity_mapper.map_entities(lemmas, entity_types=["CURRENCY"])

        # make facts
        for entity_type, entity_values in hits.items():
            for entity_value in entity_values:
                new_fact = Fact(
                    fact_type=entity_type,
                    fact_value=entity_value["value"],
                    doc_path=self.__get_doc_path("text"),
                    spans=[[entity_value["span"][0], entity_value["span"][1]]]
                )
                self.__texta_facts.append(new_fact)

        for entity_type, entity_values in lemma_hits.items():
            for entity_value in entity_values:
                new_fact = Fact(
                    fact_type=entity_type,
                    fact_value=entity_value["value"],
                    doc_path=self.__get_doc_path("lemmas"),
                    spans=[[entity_value["span"][0], entity_value["span"][1]]]
                )
                self.__texta_facts.append(new_fact)

        # declare the entities processed
        self.entities_processed = True


    def currency_sum(self):
        """
        Extracts currency + sum and sum + currency patterns from text using regexp.
        Saves extractions as facts.
        """
        text = self.get_words()
        currency_facts = [fact for fact in self.__texta_facts if fact.fact_type == "CURRENCY"]
        for fact in currency_facts:
            regexes = (
                f"{fact.fact_value} [0-9,\.]+",
                f"[0-9,\.]+ {fact.fact_value}[a-z]*"
            )
            for currency_regex in regexes:
                pattern = re.compile(currency_regex)
                for match in pattern.finditer(text):
                    fact_value = match.string[match.start():match.end()]
                    # recheck that string contains a number
                    if any(map(str.isdigit, fact_value)):
                        new_fact = Fact(
                            fact_type="CURRENCY_SUM",
                            fact_value=fact_value,
                            doc_path=self.__get_doc_path("text"),
                            spans=[match.start(), match.end()]
                        )
                        self.__texta_facts.append(new_fact)


    def emails(self):
        text = self.get_words()
        emails = ContactEmailParser(text).parse()
        self.__texta_facts.extend((email.to_fact(Document.FACT_NAME_EMAIL, self.__get_doc_path("text")) for email in emails))


    def phone_strict(self):
        text = self.get_words()
        phone_numbers_strict = ContactPhoneParserStrict(text).parse()
        self.__texta_facts.extend(
            (number.to_fact(Document.FACT_NAME_PHONE_STRICT, self.__get_doc_path("text")) for number in phone_numbers_strict))


    def phone_high_recall(self):
        text = self.get_words()
        phone_numbers = ContactPhoneParserHighRecall(text, months=self.concat_resources["months"]).parse()
        self.__texta_facts.extend(
            (number.to_fact(Document.FACT_NAME_PHONE_HIGH_RECALL, self.__get_doc_path("text")) for number in phone_numbers))


    def phone_high_precision(self):
        text = self.get_words()
        phone_numbers_high_precision = ContactPhoneParserHighPrecision(text).parse()
        self.__texta_facts.extend((number.to_fact(Document.FACT_NAME_PHONE_HIGH_PRECISION, self.__get_doc_path("text")) for number in
                                   phone_numbers_high_precision))


    def addresses(self):
        text = self.get_words()
        addresses = AddressParser(text, self.stanza_entities, self.dominant_language_code).parse()
        self.__texta_facts.extend((addr.to_fact(Document.FACT_NAME_ADDRESS, self.__get_doc_path("text")) for addr in addresses))


    def transliteration(self):
        if self.dominant_language_code in Document.langs_to_transliterate:
            for word in self.stanza_words:
                if self.dominant_language_code == "ru":
                    translit_word = self._transliterate_russian_word(word)
                elif self.dominant_language_code == "ar":
                    translit_word = self._transliterate_arabic_word(word)
                self.__transliteration.append(translit_word)


    @staticmethod
    def _transliterate_russian_word(word):
        translit_word = russian_transliterator([word.text.strip()])
        try:
            translit_word = translit_word[0].strip()
        except IndexError:
            translit_word = word.text.strip()
        return translit_word


    @staticmethod
    def _transliterate_arabic_word(word):
        translit_word = buckwalter.transliterate(word.text.strip())
        if not translit_word:
            translit_word = word.text.strip()
        return translit_word


    def get_transliteration(self) -> str:
        return " ".join(['X' if not a.strip() else a for a in self.__transliteration])


    def entity_lemmas(self, entity_value):
        lemmas = ""
        splitted = entity_value.split(" ")
        for i, word in enumerate(self.stanza_words):
            if word.text == splitted[0]:
                if len(splitted) > 1:
                    isthatphrase = True
                    j = i
                    for entity_word in splitted[1:]:
                        j += 1
                        if j < len(self.stanza_words) and entity_word != self.stanza_words[j].text:
                            isthatphrase = False
                        if j >= len(self.stanza_words):
                            isthatphrase = False
                    if isthatphrase:
                        lemmas += word.lemma
                        for i_, entity_word in enumerate(splitted[1:]):
                            lemmas += " " + self.stanza_words[i_ + i + 1].text
                        return lemmas
                else:
                    return word.lemma
        return lemmas


    def ner(self):
        tokenized_text = self.get_words()
        known_entities = Document.FACT_NAMES_NER
        not_entities = self.concat_resources["not_entities"]
        for entity in self.stanza_entities:
            if entity.text.lower() in not_entities:
                continue
            if entity.type in known_entities:
                # finds the closest spans in tokenized text
                # this is because stanza returns spans from non-tokenized text
                pattern = re.compile(re.escape(entity.text))  # Use re.escape to avoid trouble with special characters existing in the text.
                matching_tokenized_spans = [(match.start(), match.end()) for match in pattern.finditer(tokenized_text)]
                best_matching_span = None
                best_matching_distance = math.inf
                non_tokenized_span = (entity.start_char, entity.end_char)
                # matching spans are always equal or larger
                for span in matching_tokenized_spans:
                    span_distance = (span[0] - non_tokenized_span[0]) + (span[1] - non_tokenized_span[1])
                    if abs(span_distance) < best_matching_distance:
                        best_matching_distance = abs(span_distance)
                        best_matching_span = span
                # create and append fact
                # ignore facts whose match fails
                if best_matching_span:
                    new_fact = Fact(
                        fact_type=entity.type,
                        fact_value=entity.text,
                        doc_path=self.__get_doc_path("text"),
                        spans=[best_matching_span]
                    )
                    self.__texta_facts.append(new_fact)


    def namemail(self):
        """
        Find name-email pairs.

        """
        text = self.get_words()
        email_name_pairs = ContactEmailNamePairParser(text).parse()  # bounded -> str "name mail"
        self.__texta_facts.extend(
            (emailpair.to_fact(Document.FACT_NAME_NAMEMAIL, self.__get_doc_path("text")) for emailpair in email_name_pairs))


    def remove_duplicate_facts_by_span(self, facts):
        """if there are emailpairs, then:
        [{fact_type: "NAMEMAIL", value: "Aleksander Great aleksandersuur 356eKr@mail.ee", spans(30,60)}, {fact_type: "PER", value: "Aleksander Great", spans:(30,40)}] ==>
        [{fact_type: "MAIL", value: "aleksandersuur 356eKr@mail.ee", spans(40,60)}, {fact_type: "PER", value: "Aleskander Great", spans:(30,40)}]
        NAMEMAIL is used, because sometimes the ner_tagger only gets the PER or the EMAIL. This makes double sure that we get most of the entities and there is no overlaping entities
        (as it was before).
        """
        starts = []
        ends = []
        new_facts = []
        facts_values = list()
        for fact in facts:
            fact.fact_value = fact.fact_value.strip("><\)\(:;-\.,\!\?")
        for fact in facts:
            facts_values += [fact.fact_value]
            if fact.fact_type == Document.FACT_NAME_NAMEMAIL:
                splitted_value = fact.fact_value.split(" ")
                name_fact_value = " ".join(splitted_value[:2])
                name_fact = Fact(
                    fact_type="PER",
                    fact_value=name_fact_value.strip("><\)\(:;-\.,\!\?"),
                    doc_path=self.__get_doc_path("text"),
                    spans=[(fact.spans[0][0], fact.spans[0][0] + len(name_fact_value))]
                )

                email_fact_value = " ".join(splitted_value[2:])
                email_fact = Fact(
                    fact_type="EMAIL",
                    fact_value=email_fact_value.strip("><\)\(:;-\.,\!\?"),
                    doc_path=self.__get_doc_path("text"),
                    spans=[(fact.spans[0][1] - len(email_fact_value), fact.spans[0][1])]
                )

                new_facts += [email_fact, name_fact]
                starts += [email_fact.spans[0][0], name_fact.spans[0][0]]
                ends += [email_fact.spans[0][1], name_fact.spans[0][1]]

        for fact in facts:
            if fact.fact_type != Document.FACT_NAME_NAMEMAIL and fact.spans[0][0] not in starts and fact.spans[0][
                1] not in ends:
                fact.fact_value = fact.fact_value.strip("><\)\(:;-\.,\!\?")
                new_facts += [fact]
        new_facts_values = list()
        for fact in new_facts:
            new_facts_values += [fact.fact_value]
        return new_facts


    @staticmethod
    def clean_similar_in_strval(bound1):
        """
        #'PER': 'Павел Губарев', 'Павел Юрьевич Губарев' ==> 'PER': Павел Юрьевич Губарев
        #{'Народного Совета по промышленности и торговле': 'ORG', 'Народного Совета': 'ORG'} ==> {'Народного Совета по промышленности и торговле': 'ORG'}
        """
        bound = {}
        for entity_type in bound1:
            for entity_value in bound1[entity_type]:
                bound[entity_value] = entity_type
        new_bound = {}
        no_is = []
        for i, item1 in enumerate(bound.items()):
            issubitem = False
            for j, item2 in enumerate(bound.items()):
                if i != j and i not in no_is and j not in no_is:
                    if re.search("(^|\s)" + re.escape(item1[0].strip("><)(:;-.,!?")) + "(\s|$|\@[a-z]{4,5}\.[a-z]{2})",
                                 item2[0].strip("><)(:;-.,!?")) and len(item1[0].strip("><\)\(:;-\.,\!\?")) <= len(
                        item2[0].strip("><\)\(:;-\.,\!\?")):
                        if item2[1] in new_bound:
                            new_bound[item2[1]] += [item2[0].strip("><)(:;-.,!?")]
                        else:
                            new_bound[item2[1]] = [item2[0].strip("><)(:;-.,!?")]
                        no_is += [i]
                        issubitem = True
                    else:  # each word of this entity exists also in the other one.
                        notsameparts = False
                        for part_of_entity in item1[0].split(" "):
                            if not re.search("(^|\s)" + re.escape(part_of_entity.strip("><)(:;-.,!?")) + "(\s|$)",
                                             item2[0].strip("><)(:;-.,!?")):
                                notsameparts = True
                                break
                        if not notsameparts and len(item1[0].strip("><)(:;-.,!?")) <= len(
                                item2[0].strip("><)(:;-.,!?")):
                            if item2[1] in new_bound:
                                new_bound[item2[1]] += [re.sub("(\'|\")", "*", item2[0].strip("><)(:;-.,!?"))]
                            else:
                                new_bound[item2[1]] = [re.sub("(\'|\")", "*", item2[0].strip("><)(:;-.,!?"))]
                            no_is += [i]
                            issubitem = True
            if not issubitem:
                if item1[1] in new_bound:
                    new_bound[item1[1]] += [re.sub("(\'|\")", "*", item1[0].strip("><\)\(:;-\.,\!\?"))]
                else:
                    new_bound[item1[1]] = [re.sub("(\'|\")", "*", item1[0].strip("><\)\(:;-\.,\!\?"))]
        for entity_type in new_bound:
            new_bound[entity_type] = list(set(new_bound[entity_type]))
        return new_bound


    def space_between_ok(self, text, first_spans, second_spans):
        """
        tests if between the entities there is no beginning of a new letter
        """
        if first_spans[1] > 15:  # s@yandex.ru > : Hello, Steven! | l@gmail.com :\nHello, Stephanie!
            text_between = text[first_spans[1] - 15:second_spans[0]]
            pat = re.compile("\p{L}@\p{L}{3,10}\.\p{L}{2,3} {0,2}>? ?:\s")
            if pat.search(text_between):
                return False
        text_between = text[first_spans[1]:second_spans[0]]
        if re.search(self.concat_resources["space_between_not_ok"], text_between):
            return False
        for month in self.concat_resources["months"]:
            if re.search("[0-9]{1,2} ?" + month + " ?\.? ?[0-9]{4}( г\.)? ?, ?в? [0-9]{2} ?: ?[0-9]{2}",
                         text_between.lower()):
                return False
        return True


    @staticmethod
    def key_value_single_pairs(d1):
        """d1 = {'a': [1,2], 'b':[3,4]} --> [('a', 1), ('a',2), ('b',3), ('b',4)]"""
        d1_pairs = []
        for key, values in d1.items():
            for value in values:
                d1_pairs += [(key, value)]
        return d1_pairs


    def bound_close_ones(self, facts):
        """
        Bound facts found in that email, that has distance of  <=self.CLOSE_FACT_DISTANCE and that has self.space_between_ok True, together.
        """
        facts = sorted(facts, key=lambda item: item.spans[0][0])
        new_bound = {'doc_path': self.__get_doc_path("text"), 'fact': Document.FACT_NAME_BOUNDED, 'spans': [], 'str_val': {},
                     "str_values": []}
        new_bounded = []
        for fact in facts:
            if len(new_bound["spans"]) == 0:
                new_bound["spans"] += fact.spans
                new_bound["str_val"][fact.fact_type] = [fact.fact_value]
                new_bound["str_values"] = [(fact.fact_value, fact.fact_type)]
            else:
                if abs(fact.spans[0][0] - new_bound["spans"][-1][
                    -1]) < self.CLOSE_FACT_DISTANCE and self.space_between_ok(self.get_words(), new_bound["spans"][-1],
                                                                              fact.spans[0]):
                    new_bound["spans"] += fact.spans
                    new_bound["str_values"] += [(fact.fact_value, fact.fact_type)]
                    if fact.fact_type in new_bound["str_val"]:
                        new_bound["str_val"][fact.fact_type] += [fact.fact_value]
                    else:
                        new_bound["str_val"][fact.fact_type] = [fact.fact_value]
                else:  # start a new bound
                    if len(new_bound["spans"]) > 1:
                        new_bounded += [new_bound]
                    new_bound = {'doc_path': self.__get_doc_path("text"), 'fact': 'BOUNDED', 'spans': [], "str_val": {},
                                 "str_values": []}
                    new_bound["spans"] += fact.spans
                    new_bound["str_values"] = [(fact.fact_value, fact.fact_type)]
                    new_bound["str_val"][fact.fact_type] = [fact.fact_value]
        if len(new_bound["spans"]) > 1:
            new_bounded += [new_bound]
        return new_bounded


    def remove_overlaping_in_bounded(self, new_bounded):
        """
        if bounded has two entities with spans starting on the same index, pick the longest one.
        For example:
        'spans': '[[174, 194], [174, 185]]',
   'str_val': "{'EMAIL': ['89179012978@mail.ru]'], 'PHONE': ['89179012978']}"},
       clean_similar_in_strval: strvals contain each other, concatenate.
       """
        new_bounded_coinciding_erased = []
        for new_bound in new_bounded:
            to_delete_is = []
            for i, span1 in enumerate(new_bound["spans"]):
                for j, span2 in enumerate(new_bound["spans"]):
                    if span1[0] == span2[0] and i != j:
                        if span1[1] > span2[1]:
                            to_delete_is += [j]
                        elif span1[1] < span2[1]:
                            to_delete_is += [i]
            new_bound_erased_coinciding = {'doc_path': self.__get_doc_path("text"), 'fact': Document.FACT_NAME_BOUNDED, 'spans': [],
                                           'str_val': {}}
            for i, span1 in enumerate(new_bound["spans"]):
                if i not in to_delete_is:
                    new_bound_erased_coinciding["spans"] += [span1]

                    if new_bound["str_values"][i][1] in new_bound_erased_coinciding["str_val"]:
                        new_bound_erased_coinciding["str_val"][new_bound["str_values"][i][1]] += [
                            new_bound["str_values"][i][0]]
                    else:
                        new_bound_erased_coinciding["str_val"][new_bound["str_values"][i][1]] = [
                            new_bound["str_values"][i][0]]
            new_bound_erased_coinciding["str_val"] = self.clean_similar_in_strval(
                new_bound_erased_coinciding["str_val"])
            hasmanyentities = False
            for entity_type in new_bound_erased_coinciding["str_val"]:
                if len(new_bound_erased_coinciding["str_val"][entity_type]) > 1:
                    hasmanyentities = True
                    break
            if len(new_bound_erased_coinciding["spans"]) > 1 and (
                    hasmanyentities or len(new_bound_erased_coinciding["str_val"].items()) > 1):
                new_bounded_coinciding_erased += [new_bound_erased_coinciding]
        return new_bounded_coinciding_erased


    def concatenate_subset_bounds(self, new_bounded):
        """
        When one BOUNDED is a subset of another one by strings, concatenate
        As this is the last finishing touch, add lemmas to the string_value
        """
        concatenated_bound_is = []
        new_bounds = list()
        for i, new_bound in enumerate(new_bounded):
            issubset = False
            for j, another_bound in enumerate(new_bounded):
                set_comparison = set(self.key_value_single_pairs(new_bound["str_val"])) <= set(self.key_value_single_pairs(another_bound["str_val"]))
                if j not in concatenated_bound_is and i not in concatenated_bound_is and i != j and set_comparison:
                    issubset = True
                    another_bound["spans"] += new_bound["spans"]
                    concatenated_bound_is += [i]
            if not issubset:
                lemmas = {}
                for key in new_bound["str_val"]:
                    for entity in new_bound["str_val"][key]:
                        lemma = self.entity_lemmas(entity)
                        if not lemma:
                            lemma = "UNK"
                        if key in lemmas:
                            lemmas[key] += [lemma]
                        else:
                            lemmas[key] = [lemma]
                new_fact = Fact(
                    fact_type=new_bound["fact"],
                    fact_value=str(new_bound["str_val"]),  ##add lemmas
                    fact_lemma=str(lemmas),
                    doc_path=self.__get_doc_path("text"),
                    spans=new_bound["spans"]
                )
                new_bounds.append(new_fact)
        return new_bounds


    def remove_old_bounded_and_add_phone_high_recall(self, facts):
        """
        remove previous BOUNDED facts
        remove previous phone facts
        add phoneparser made for emails (ContactPhoneParserHighRecall)
        """
        new_facts = [fact for fact in facts if not re.match("PHONE|" + Document.FACT_NAME_BOUNDED, fact.fact_type)]
        text = self.get_words()
        phone_numbers = ContactPhoneParserHighRecall(text, months=self.concat_resources["months"]).parse()
        new_facts.extend(
            (number.to_fact(Document.FACT_NAME_PHONE_HIGH_RECALL, self.__get_doc_path("text")) for number in phone_numbers))
        return new_facts


    def bounded(self):
        facts = self.remove_duplicate_facts_by_span(self.__texta_facts)
        facts = self.remove_old_bounded_and_add_phone_high_recall(
            facts)  # bounded uses only ContactPhoneParserHighRecall results and doesn't look at old BOUNDED facts.
        new_bounded = self.bound_close_ones(facts)
        new_bounded = self.remove_overlaping_in_bounded(new_bounded)
        new_bounded = self.concatenate_subset_bounds(new_bounded)
        for new_bound in new_bounded:
            self.__texta_facts.append(new_bound)
