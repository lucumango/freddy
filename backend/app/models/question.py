from enum import Enum


class QuestionType(str, Enum):
    short_text = "short_text"
    long_text = "long_text"
    number = "number"
    likert = "likert"
    single_choice = "single_choice"
    multiple_choice = "multiple_choice"
    date = "date"
