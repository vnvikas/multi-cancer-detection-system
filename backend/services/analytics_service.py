from backend.database.models import db, Patient, Scan, Prediction, User
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import json

# Try to import pandas, provide fallback if not available
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not installed. Some analytics features will be limited.")

class AnalyticsService:
    """Service for analytics and reporting"""
    
    def get_admin_dashboard_stats(self):
        """Get statistics for admin dashboard"""
        try:
            # Basic counts
            total_doctors = User.query.filter_by(role='doctor', is_active=True).count()
            total_patients = Patient.query.count()
            total_scans = Scan.query.count()
            total_predictions = Prediction.query.count()
            
            # Average confidence
            avg_confidence = db.session.query(func.avg(Prediction.confidence_score)).scalar() or 0
            
            # Monthly trends
            monthly_data = self.get_monthly_trends()
            
            # Predictions by type
            predictions_by_type = db.session.query(
                Prediction.cancer_type,
                func.count(Prediction.id)
            ).group_by(Prediction.cancer_type).all()
            
            # Recent activity
            recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
            recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(5).all()
            
            return {
                'total_doctors': total_doctors,
                'total_patients': total_patients,
                'total_scans': total_scans,
                'total_predictions': total_predictions,
                'avg_confidence': float(avg_confidence) if avg_confidence else 0,
                'monthly_data': monthly_data,
                'predictions_by_type': [{'type': t[0] or 'Unknown', 'count': t[1]} for t in predictions_by_type],
                'recent_patients': [self._patient_to_dict(p) for p in recent_patients],
                'recent_predictions': [self._prediction_to_dict(p) for p in recent_predictions]
            }
        except Exception as e:
            print(f"Error getting admin stats: {e}")
            return {}
    
    def get_doctor_dashboard_stats(self, doctor_id):
        """Get statistics for doctor dashboard"""
        try:
            # Get doctor's patients
            patients = Patient.query.filter_by(doctor_id=doctor_id).all()
            patient_ids = [p.id for p in patients]
            
            # Count scans
            scans = Scan.query.filter(Scan.patient_id.in_(patient_ids)).all() if patient_ids else []
            
            # Count predictions
            predictions = Prediction.query.join(Scan).filter(Scan.patient_id.in_(patient_ids)).all() if patient_ids else []
            
            # Verified predictions
            verified = [p for p in predictions if p.doctor_verified]
            
            # Pending verifications
            pending = [p for p in predictions if not p.doctor_verified]
            
            # Average confidence
            avg_confidence = 0
            if predictions:
                avg_confidence = sum(float(p.confidence_score or 0) for p in predictions) / len(predictions)
            
            # Weekly activity data
            weekly_activity = self._get_weekly_activity(doctor_id)
            
            return {
                'total_patients': len(patients),
                'total_scans': len(scans),
                'total_predictions': len(predictions),
                'verified_predictions': len(verified),
                'pending_verifications': len(pending),
                'avg_confidence': avg_confidence,
                'weekly_activity': weekly_activity,
                'recent_patients': [self._patient_to_dict(p) for p in patients[:5]],
                'recent_predictions': [self._prediction_to_dict(p) for p in predictions[:5]]
            }
        except Exception as e:
            print(f"Error getting doctor stats: {e}")
            return {}
    
    def get_monthly_trends(self):
        """Get monthly registration trends"""
        try:
            six_months_ago = datetime.now() - timedelta(days=180)
            
            monthly_patients = db.session.query(
                func.date_format(Patient.created_at, '%Y-%m').label('month'),
                func.count(Patient.id).label('count')
            ).filter(Patient.created_at >= six_months_ago).group_by('month').order_by('month').all()
            
            monthly_scans = db.session.query(
                func.date_format(Scan.uploaded_at, '%Y-%m').label('month'),
                func.count(Scan.id).label('count')
            ).filter(Scan.uploaded_at >= six_months_ago).group_by('month').order_by('month').all()
            
            return {
                'patients': [{'month': m[0], 'count': m[1]} for m in monthly_patients],
                'scans': [{'month': m[0], 'count': m[1]} for m in monthly_scans]
            }
        except Exception as e:
            print(f"Error getting monthly trends: {e}")
            return {'patients': [], 'scans': []}
    
    def get_prediction_analytics(self, doctor_id=None):
        """Get detailed prediction analytics"""
        try:
            query = Prediction.query
            
            if doctor_id:
                query = query.join(Scan).join(Patient).filter(Patient.doctor_id == doctor_id)
            
            total = query.count()
            
            if total == 0:
                return {}
            
            # Confidence distribution
            high_confidence = query.filter(Prediction.confidence_score >= 0.8).count()
            medium_confidence = query.filter(and_(
                Prediction.confidence_score >= 0.5,
                Prediction.confidence_score < 0.8
            )).count()
            low_confidence = query.filter(Prediction.confidence_score < 0.5).count()
            
            # Risk distribution
            high_risk = query.filter(Prediction.risk_score >= 70).count()
            medium_risk = query.filter(and_(
                Prediction.risk_score >= 30,
                Prediction.risk_score < 70
            )).count()
            low_risk = query.filter(Prediction.risk_score < 30).count()
            
            # Verification rate
            verified = query.filter(Prediction.doctor_verified == True).count()
            verification_rate = (verified / total * 100) if total > 0 else 0
            
            return {
                'total_predictions': total,
                'confidence_distribution': {
                    'high': high_confidence,
                    'medium': medium_confidence,
                    'low': low_confidence
                },
                'risk_distribution': {
                    'high': high_risk,
                    'medium': medium_risk,
                    'low': low_risk
                },
                'verification_rate': verification_rate,
                'verified_count': verified,
                'unverified_count': total - verified
            }
        except Exception as e:
            print(f"Error getting prediction analytics: {e}")
            return {}
    
    def get_patient_analytics(self, patient_id):
        """Get analytics for a specific patient"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {}
            
            scans = Scan.query.filter_by(patient_id=patient_id).all()
            predictions = []
            for scan in scans:
                predictions.extend(scan.predictions)
            
            if not predictions:
                return {'has_data': False}
            
            # Trend analysis
            predictions_sorted = sorted(predictions, key=lambda x: x.created_at)
            
            confidence_trend = [float(p.confidence_score or 0) for p in predictions_sorted]
            risk_trend = [p.risk_score or 0 for p in predictions_sorted]
            
            # Latest prediction
            latest = predictions_sorted[-1] if predictions_sorted else None
            
            return {
                'has_data': True,
                'total_scans': len(scans),
                'total_predictions': len(predictions),
                'confidence_trend': confidence_trend,
                'risk_trend': risk_trend,
                'latest_prediction': self._prediction_to_dict(latest) if latest else None,
                'dates': [p.created_at.strftime('%Y-%m-%d') for p in predictions_sorted]
            }
        except Exception as e:
            print(f"Error getting patient analytics: {e}")
            return {}
    
    def export_data(self, data_type, start_date=None, end_date=None, format='csv'):
        """Export data to CSV or JSON"""
        try:
            if data_type == 'patients':
                query = Patient.query
                if start_date and end_date:
                    query = query.filter(Patient.created_at.between(start_date, end_date))
                data = [self._patient_to_dict(p) for p in query.all()]
            
            elif data_type == 'predictions':
                query = Prediction.query
                if start_date and end_date:
                    query = query.filter(Prediction.created_at.between(start_date, end_date))
                data = [self._prediction_to_dict(p) for p in query.all()]
            
            elif data_type == 'scans':
                query = Scan.query
                if start_date and end_date:
                    query = query.filter(Scan.uploaded_at.between(start_date, end_date))
                data = [self._scan_to_dict(s) for s in query.all()]
            
            else:
                return None
            
            if format == 'csv' and PANDAS_AVAILABLE:
                df = pd.DataFrame(data)
                return df.to_csv(index=False)
            elif format == 'csv' and not PANDAS_AVAILABLE:
                # Manual CSV creation without pandas
                if not data:
                    return ""
                headers = list(data[0].keys())
                csv_rows = [','.join(headers)]
                for row in data:
                    csv_rows.append(','.join(str(row.get(h, '')) for h in headers))
                return '\n'.join(csv_rows)
            else:
                return json.dumps(data, default=str)
                
        except Exception as e:
            print(f"Error exporting data: {e}")
            return None
    
    def _get_weekly_activity(self, doctor_id):
        """Get weekly activity for doctor"""
        try:
            week_ago = datetime.now() - timedelta(days=7)
            
            scans_by_day = db.session.query(
                func.dayofweek(Scan.uploaded_at).label('day'),
                func.count(Scan.id).label('count')
            ).join(Patient).filter(
                Patient.doctor_id == doctor_id,
                Scan.uploaded_at >= week_ago
            ).group_by('day').all()
            
            predictions_by_day = db.session.query(
                func.dayofweek(Prediction.created_at).label('day'),
                func.count(Prediction.id).label('count')
            ).join(Scan).join(Patient).filter(
                Patient.doctor_id == doctor_id,
                Prediction.created_at >= week_ago
            ).group_by('day').all()
            
            # Initialize arrays for days 1-7
            scans_array = [0] * 7
            predictions_array = [0] * 7
            
            for day, count in scans_by_day:
                if 1 <= day <= 7:
                    scans_array[day-1] = count
            
            for day, count in predictions_by_day:
                if 1 <= day <= 7:
                    predictions_array[day-1] = count
            
            return {
                'scans': scans_array,
                'predictions': predictions_array
            }
        except Exception as e:
            print(f"Error getting weekly activity: {e}")
            return {'scans': [0]*7, 'predictions': [0]*7}
    
    def _patient_to_dict(self, patient):
        """Convert patient to dictionary"""
        return {
            'id': patient.patient_uid,
            'name': patient.name,
            'age': patient.age,
            'gender': patient.gender,
            'contact': patient.contact_number,
            'created_at': patient.created_at.isoformat() if patient.created_at else None
        }
    
    def _prediction_to_dict(self, prediction):
        """Convert prediction to dictionary"""
        return {
            'id': prediction.prediction_id,
            'cancer_type': prediction.cancer_type,
            'subtype': prediction.cancer_subtype,
            'stage': prediction.cancer_stage,
            'confidence': float(prediction.confidence_score) if prediction.confidence_score else 0,
            'risk_score': prediction.risk_score,
            'verified': prediction.doctor_verified,
            'created_at': prediction.created_at.isoformat() if prediction.created_at else None
        }
    
    def _scan_to_dict(self, scan):
        """Convert scan to dictionary"""
        return {
            'id': scan.scan_id,
            'cancer_type': scan.cancer_type,
            'patient_id': scan.patient.patient_uid if scan.patient else None,
            'uploaded_at': scan.uploaded_at.isoformat() if scan.uploaded_at else None
        }