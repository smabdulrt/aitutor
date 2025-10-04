"""Teaching Assistant module"""

from .ta_core import TeachingAssistant, SessionState, ActivityMonitor
from .emotional_intelligence import EmotionalIntelligence, EmotionState, EmotionDetectionResult

__all__ = [
    'TeachingAssistant',
    'SessionState',
    'ActivityMonitor',
    'EmotionalIntelligence',
    'EmotionState',
    'EmotionDetectionResult'
]
