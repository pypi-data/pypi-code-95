import zipfile
from typing import Any, Dict, List

import pandas as pd

from ..model.entities import Protocol
from ..model.utility import ensure_path, touch, unlink
from .interface import ITagger, TaggedDocument


def tag_speech_items(tagger: ITagger, speech_items: List[dict]) -> List[dict]:

    speech_texts = [item['text'] for item in speech_items]

    documents: List[TaggedDocument] = tagger.tag(speech_texts)

    for i, document in enumerate(documents):
        speech_items[i].update(
            annotation=tagger.to_csv(document),
            num_tokens=document.get("num_tokens"),
            num_words=document.get("num_words"),
        )

    return speech_items


def tag_protocol(tagger: ITagger, protocol: Protocol, skip_size: int = 5) -> List[dict]:
    """Tag protocol using `tagger`.

    Args:
        tagger (ITagger): Stanza or spaCy wrapper
        protocol (Protocol): ParlaClarin XML protocol
        skip_size (int, optional): Skip text less then size. Defaults to 5.

    Returns:
        List[dict]: [description]
    """

    speech_items: List[Dict[str, Any]] = tag_speech_items(tagger, protocol.to_dict(skip_size=skip_size))

    return speech_items


def bulk_tag_protocols(tagger: ITagger, protocols: List[Protocol], skip_size: int = 5) -> List[List[dict]]:

    speech_items: List[Dict[str, Any]] = []
    protocol_refs = {}

    for protocol in protocols:
        idx = len(speech_items)
        speech_items.extend(protocol.to_dict(skip_size=skip_size))
        protocol_refs[protocol.name] = (idx, len(speech_items) - idx)

    speech_items: List[Dict[str, Any]] = tag_speech_items(tagger, speech_items)

    protocol_speech_items = []
    for protocol in protocols:
        idx, n_count = protocol_refs[protocol.name]
        protocol_speech_items.append(speech_items[idx : idx + n_count])

    return protocol_speech_items


def _store_tagged_protocol(output_filename: str, speech_items: List[dict]) -> None:
    """Store tagged speeches in `output_filename`, and create and store index."""

    if output_filename.endswith("zip"):

        with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as fp:

            """Store each speech as a CSV"""
            for item in speech_items:
                item['filename'] = f"{item['document_name']}.csv"
                fp.writestr(item['filename'], (item['annotation'] or ""))

            """Create document index and store as a CSV"""
            for item in speech_items:
                del item['annotation']
                del item['text']

            document_index: pd.DataFrame = (
                pd.DataFrame(speech_items)
                .set_index('document_name', drop=False)
                .rename_axis('')
                .assign(document_id=range(0, len(speech_items)))
            )

            fp.writestr('document_index.csv', document_index.to_csv(sep='\t', header=True))

    else:

        raise ValueError("Only Zip store currently implemented")


def tag_protocol_xml(input_filename: str, output_filename: str, tagger: ITagger) -> None:
    """Annotate XML protocol `input_filename` to `output_filename`.

    Args:
        input_filename (str, optional): Defaults to None.
        output_filename (str, optional): Defaults to None.
        tagger (StanzaTagger, optional): Defaults to None.
    """

    try:
        ensure_path(output_filename)
        unlink(output_filename)

        protocol: Protocol = Protocol.from_file(input_filename)

        if protocol.has_speech_text():

            tagged_speeches = tag_protocol(tagger, protocol)

            _store_tagged_protocol(output_filename, tagged_speeches)

        else:

            touch(output_filename)

    except Exception:
        print(f"failed: {input_filename}")
        raise
