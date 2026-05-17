from backend.database.models import db, Prediction, Scan, Patient, User
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os
from flask import current_app

class ReportService:
    
    def generate_pdf_report(self, prediction_id, doctor_id):
        """Generate PDF report for a prediction"""
        try:
            # Get data
            prediction = Prediction.query.get(prediction_id)
            if not prediction:
                return None
            
            scan = Scan.query.get(prediction.scan_id)
            patient = Patient.query.get(scan.patient_id)
            doctor = User.query.get(doctor_id)
            
            # Create reports directory if not exists
            reports_dir = os.path.join(current_app.config['REPORTS_FOLDER'], 
                                       datetime.now().strftime('%Y/%m'))
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate filename
            filename = f"report_{patient.patient_uid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(reports_dir, filename)
            
            # Create PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                alignment=1  # Center
            )
            story.append(Paragraph("Multi-Cancer Detection System", title_style))
            story.append(Paragraph("Cancer Diagnosis Report", styles['Heading2']))
            story.append(Spacer(1, 0.25 * inch))
            
            # Report Info
            story.append(Paragraph(f"Report ID: {prediction.prediction_id}", styles['Normal']))
            story.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 0.25 * inch))
            
            # Patient Information
            story.append(Paragraph("Patient Information", styles['Heading3']))
            patient_data = [
                ["Patient ID:", patient.patient_uid],
                ["Name:", patient.name],
                ["Age:", str(patient.age) if patient.age else "N/A"],
                ["Gender:", patient.gender if patient.gender else "N/A"],
                ["Contact:", patient.contact_number if patient.contact_number else "N/A"],
            ]
            
            patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(patient_table)
            story.append(Spacer(1, 0.25 * inch))
            
            # Scan Information
            story.append(Paragraph("Scan Information", styles['Heading3']))
            scan_data = [
                ["Scan ID:", scan.scan_id],
                ["Cancer Type:", scan.cancer_type.title() if scan.cancer_type else "N/A"],
                ["Scan Type:", scan.scan_type if scan.scan_type else "N/A"],
                ["Scan Date:", scan.scan_date.strftime('%Y-%m-%d') if scan.scan_date else "N/A"],
            ]
            
            scan_table = Table(scan_data, colWidths=[2*inch, 4*inch])
            scan_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(scan_table)
            story.append(Spacer(1, 0.25 * inch))
            
            # Prediction Results
            story.append(Paragraph("AI Prediction Results", styles['Heading3']))
            
            # Risk level color
            risk_score = prediction.risk_score or 0
            if risk_score < 30:
                risk_color = colors.green
                risk_level = "Low"
            elif risk_score < 70:
                risk_color = colors.orange
                risk_level = "Moderate"
            else:
                risk_color = colors.red
                risk_level = "High"
            
            prediction_data = [
                ["Cancer Type:", prediction.cancer_type or "N/A"],
                ["Subtype:", prediction.cancer_subtype or "N/A"],
                ["Stage:", prediction.cancer_stage or "N/A"],
                ["Confidence Score:", f"{float(prediction.confidence_score or 0) * 100:.1f}%"],
                ["Risk Score:", f"{risk_score}%"],
                ["Risk Level:", risk_level],
                ["Survival Rate:", f"{float(prediction.survival_rate or 0):.1f}%"],
                ["Metastasis Probability:", f"{float(prediction.metastasis_probability or 0):.1f}%"],
                ["Treatment Response:", prediction.treatment_response_prediction or "N/A"],
            ]
            
            pred_table = Table(prediction_data, colWidths=[2*inch, 4*inch])
            pred_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(pred_table)
            story.append(Spacer(1, 0.25 * inch))
            
            # Doctor Verification
            story.append(Paragraph("Doctor Verification", styles['Heading3']))
            verification_data = [
                ["Verified By:", doctor.name if doctor else "N/A"],
                ["Verification Status:", "Verified" if prediction.doctor_verified else "Pending"],
                ["Doctor Notes:", prediction.doctor_notes or "No notes provided"],
            ]
            
            verify_table = Table(verification_data, colWidths=[2*inch, 4*inch])
            verify_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(verify_table)
            story.append(Spacer(1, 0.25 * inch))
            
            # Recommendations
            story.append(Paragraph("Recommendations", styles['Heading3']))
            recommendations = [
                "• Follow up with oncologist within 2 weeks",
                "• Additional diagnostic tests may be required",
                "• Consider genetic counseling if family history present",
                "• Maintain regular screening schedule",
                "• Discuss treatment options with specialist"
            ]
            
            for rec in recommendations:
                story.append(Paragraph(rec, styles['Normal']))
            
            story.append(Spacer(1, 0.25 * inch))
            
            # Footer
            story.append(Paragraph("This report is generated by AI and should be reviewed by a qualified medical professional.", 
                                  ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
            story.append(Paragraph(f"Generated by Multi-Cancer Detection System | {datetime.now().strftime('%Y-%m-%d')}", 
                                  ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)))
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return None