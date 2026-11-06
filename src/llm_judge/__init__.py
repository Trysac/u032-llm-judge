"""LLM-as-judge with versioned rubrics, strict score parsing and kappa calibration."""

from __future__ import annotations

from .calibration import Agreement, CalibrationReport, calibrate
from .errors import JudgeError
from .judging import judge
from .models import JudgeEvent, Judgement
from .ports import FakeLLM, LLMPort, Message, RecordedLLM, RecordingExhaustedError
from .rubric import Criterion, Rubric

__all__ = [
    "Agreement",
    "CalibrationReport",
    "Criterion",
    "FakeLLM",
    "JudgeError",
    "JudgeEvent",
    "Judgement",
    "LLMPort",
    "Message",
    "RecordedLLM",
    "RecordingExhaustedError",
    "Rubric",
    "__version__",
    "calibrate",
    "judge",
]

__version__ = "0.1.0"
