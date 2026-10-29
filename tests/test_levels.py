"""Tests for the rough reading-grade estimator."""

from patient_handout_maker.levels import estimated_grade, text_stats

SIMPLE = "This is a short and simple sentence. It uses easy words."
COMPLEX = (
    "Multidisciplinary corroborative retrospective evaluations "
    "demonstrate nonrepresentational percutaneous intravascular "
    "characterizations in physiological pseudohypertrophies."
)


def test_stats_counts():
    words, sentences, syllables = text_stats(SIMPLE)
    assert words == 11
    assert sentences >= 2


def test_complex_text_scores_higher_than_simple():
    assert estimated_grade(COMPLEX) > estimated_grade(SIMPLE)


def test_simple_text_is_plain():
    assert estimated_grade(SIMPLE) < 8.0


def test_empty_text_returns_zero():
    assert estimated_grade("") == 0.0
