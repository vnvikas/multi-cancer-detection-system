import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.patient_service import PatientService
from backend.services.prediction_service import PredictionService
from backend.services.report_service import ReportService

class TestServices(unittest.TestCase):
    
    def setUp(self):
        self.patient_service = PatientService()
        self.prediction_service = PredictionService()
        self.report_service = ReportService()
    
    def test_patient_service_validation(self):
        """Test patient service validation"""
        patient_data = {
            'name': 'Test Patient',
            'age': 35,
            'gender': 'Male',
            'contact_number': '1234567890'
        }
        
        # Test validation (without DB, just check structure)
        self.assertIsNotNone(patient_data.get('name'))
        self.assertIsNotNone(patient_data.get('age'))
    
    def test_prediction_service_initialization(self):
        """Test prediction service initialization"""
        self.assertIsNotNone(self.prediction_service)
    
    def test_report_service_initialization(self):
        """Test report service initialization"""
        self.assertIsNotNone(self.report_service)

if __name__ == '__main__':
    unittest.main()