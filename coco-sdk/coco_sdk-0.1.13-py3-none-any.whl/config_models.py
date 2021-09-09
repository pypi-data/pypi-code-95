from enum import Enum
from typing import Dict, Optional, List, Union, Any

from pydantic import BaseModel


class TranslationConfig(BaseModel):
    # translate user inputs from source to target
    input_target_language: Optional[str]

    # translate component responses from source to target
    response_source_language: Optional[str]


class BlueprintConfig(BaseModel):
    blueprint_id: str
    component_id: Optional[str]
    translations: Optional[TranslationConfig]


class GlueNode(BaseModel):
    component_id: str
    on: Dict[str, str] = {}
    parameters: Dict[str, str] = {}
    position: Optional[Dict[str, int]]
    call_with_new_input: Optional[bool]


class GlueConfig(BlueprintConfig):
    glue_v1: Dict[str, GlueNode]


class GlueTransition(BaseModel):
    target_node_id: str


class SuccessTransition(GlueTransition):
    success: bool


class OutputTransition(GlueTransition):
    output_name: str
    output_value: str


class GlueNodeV2(BaseModel):
    component_id: str
    on: List[Union[SuccessTransition, OutputTransition, GlueTransition]] = []
    parameters: Dict[str, Any] = {}
    position: Optional[Dict[str, int]]
    call_with_new_input: Optional[bool]
    with_out_of_context: Optional[str]


class GlueV2Metadata(BaseModel):
    with_out_of_context: Optional[str]


class GlueConfigV2(BlueprintConfig):
    glue_v2: Dict[str, GlueNodeV2]
    glue_v2_metadata: Optional[GlueV2Metadata]


class ActionsConfig(BlueprintConfig):
    action_config: Dict[str, List[str]]


class QaConfigNode(BaseModel):
    question_id: str
    questions: List[str]
    answers: List[str]


class QaConfig(BlueprintConfig):
    qa_config: List[QaConfigNode]


class SurveyV1QuestionType(str, Enum):
    open = "open"
    multiple = "multiple"
    yesno = "yesno"


class CandidateAnswer(BaseModel):
    answer_id: str
    answer: str


class SurveyV1Question(BaseModel):
    question_id: str
    questions: str
    question_type: SurveyV1QuestionType
    answers: List[CandidateAnswer]


class SurveyV1Config(ActionsConfig):
    survey_v1: List[SurveyV1Question]


class QuizV1Question(SurveyV1Question):
    correct_answer_id: str


class QuizV1Config(ActionsConfig):
    quiz_v1: List[QuizV1Question]
