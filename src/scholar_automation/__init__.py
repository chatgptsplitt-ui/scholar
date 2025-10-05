"""Scholarship application automation framework."""

from .profiles import UserProfile
from .discovery import ScholarshipDiscoveryEngine, Opportunity
from .navigation import ApplicationNavigator
from .forms import FormInteractor
from .page_understanding import PageUnderstandingEngine
from .submission import SubmissionManager
from .transparency import TransparencyLogger
from .controller import AutomationController

__all__ = [
    "AutomationController",
    "UserProfile",
    "ScholarshipDiscoveryEngine",
    "Opportunity",
    "ApplicationNavigator",
    "FormInteractor",
    "PageUnderstandingEngine",
    "SubmissionManager",
    "TransparencyLogger",
]
