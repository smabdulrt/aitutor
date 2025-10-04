"""Teaching Assistant module"""

from .ta_core import TeachingAssistant, SessionState, ActivityMonitor
from .emotional_intelligence import EmotionalIntelligence, EmotionState, EmotionDetectionResult
from .context_provider import ContextProvider, ContextResult, ContextType

__all__ = [
    'TeachingAssistant',
    'SessionState',
    'ActivityMonitor',
    'EmotionalIntelligence',
    'EmotionState',
    'EmotionDetectionResult',
    'ContextProvider',
    'ContextResult',
    'ContextType'
]
