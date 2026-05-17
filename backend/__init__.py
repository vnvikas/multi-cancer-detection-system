"""
Multi-Cancer Detection System - Backend Package
"""

# Import database models
from backend.database.models import db, User, Patient, Scan, Prediction, TreatmentPlan, FollowUpSchedule, MedicalHistory, ModelPerformance, SystemLog

# Import services with error handling
try:
    from backend.services.patient_service import PatientService
except ImportError as e:
    print(f"Warning: Could not import PatientService: {e}")
    PatientService = None

try:
    from backend.services.prediction_service import PredictionService
except ImportError as e:
    print(f"Warning: Could not import PredictionService: {e}")
    PredictionService = None

try:
    from backend.services.report_service import ReportService
except ImportError as e:
    print(f"Warning: Could not import ReportService: {e}")
    ReportService = None

try:
    from backend.services.analytics_service import AnalyticsService
except ImportError as e:
    print(f"Warning: Could not import AnalyticsService: {e}")
    AnalyticsService = None

__version__ = '1.0.0'
__all__ = [
    'db', 'User', 'Patient', 'Scan', 'Prediction', 'TreatmentPlan', 
    'FollowUpSchedule', 'MedicalHistory', 'ModelPerformance', 'SystemLog',
    'PatientService', 'PredictionService', 'ReportService', 'AnalyticsService'
]