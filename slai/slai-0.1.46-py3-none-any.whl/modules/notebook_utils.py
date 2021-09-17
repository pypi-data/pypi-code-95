import json
import tokenize
import re
import datetime

from pathlib import Path
from jinja2 import Template
from slai.constants import NOTEBOOK_TRAINER_PREFIX, DEFAULT_TRAINER_TIMEOUT_S


def parse_notebook(notebook_path):
    """
    Parses notebook contents into a model trainer.
    """

    notebook_data = None

    with open(notebook_path, "r") as f_in:
        notebook_data = json.load(f_in)

    output_source = []

    # only use cells that contain the NOTEBOOK_TRAINER_PREFIX comment
    for cell in notebook_data["cells"]:
        cell_source_line_iter = iter(cell["source"])

        tokens = list(tokenize.generate_tokens(lambda: next(cell_source_line_iter)))

        for token_type, token_value, begin, end, line in tokens:
            if token_type == tokenize.COMMENT:
                m = re.match(NOTEBOOK_TRAINER_PREFIX, line)
                if m:
                    output_source.extend(cell["source"])
                    output_source[-1] = output_source[-1].strip() + "\n"
                    break

    import_lines = list(
        filter(
            lambda l: l.startswith("import ") or l.startswith("from "), output_source
        )
    )

    for idx, _ in enumerate(import_lines):
        import_lines[idx] = import_lines[idx].strip() + "\n"

    output_source = list(
        filter(
            lambda l: not l.startswith("import ") and not l.startswith("from "),
            output_source,
        )
    )

    output_source = list(
        filter(lambda l: NOTEBOOK_TRAINER_PREFIX not in l, output_source)
    )

    for idx in range(len(output_source)):
        if output_source[idx] != "\n":
            output_source[idx] = (" " * 8) + output_source[idx]

    imports = "".join(import_lines)
    trainer = "".join(output_source)

    return imports, trainer


def generate_trainer_from_template(*, model_name, imports, trainer, model_version_id):
    slai_module_path = Path(__file__).parent.parent
    trainer_template_path = f"{slai_module_path}/templates/trainer.py.template"

    template_variables = {
        "SLAI_MODEL_NAME": model_name,
        "SLAI_TRAINER_CREATED_AT": datetime.datetime.now().isoformat(),
        "SLAI_TRAINER_IMPORTS": imports,
        "SLAI_TRAINER_CONTENTS": trainer,
        "SLAI_CURRENT_MODEL_VERSION": model_version_id,
        "SLAI_TRAINER_TIMEOUT": DEFAULT_TRAINER_TIMEOUT_S,
    }

    template_contents = None
    rendered_template = None

    with open(trainer_template_path, "r") as f_in:
        template_contents = f_in.read()
        t = Template(template_contents)
        rendered_template = t.render(**template_variables)

    return rendered_template
