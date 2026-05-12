"""
MediERP — PDF Generation Service
Génération d'ordonnances et factures professionnelles.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import cm

class PDFService:
    def __init__(self, output_dir: str = "assets/documents/prescriptions"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_prescription(self, data: dict) -> str:
        """
        Génère un PDF d'ordonnance.
        data = {
            'id': int,
            'doctor_name': str,
            'patient_name': str,
            'date': str,
            'medications': [{'name': str, 'dosage': str, 'duration': str}, ...]
        }
        """
        filename = f"prescription_{data['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        
        # Styles personnalisés
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, spaceAfter=20, textColor=colors.HexColor("#1890ff"))
        header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
        
        elements = []

        # En-tête Clinique
        elements.append(Paragraph("<b>MediERP — Clinique Médicale Intelligente</b>", title_style))
        elements.append(Paragraph(f"Médecin Traitant : {data.get('doctor_name', 'Dr. MediERP')}", styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph(f"Date : {data.get('date', datetime.now().strftime('%d/%m/%Y'))}", styles['Normal']))
        elements.append(Spacer(1, 1*cm))

        # Infos Patient
        elements.append(Paragraph(f"<b>ORDONNANCE POUR :</b> {data.get('patient_name', 'Patient')}", styles['Heading2']))
        elements.append(Spacer(1, 0.5*cm))

        # Tableau des médicaments
        table_data = [["Médicament", "Posologie", "Durée"]]
        for med in data.get('medications', []):
            table_data.append([med['name'], med['dosage'], med['duration']])

        t = Table(table_data, colWidths=[8*cm, 5*cm, 4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#fafafa")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1890ff")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 2*cm))
        elements.append(Paragraph("<i>Cachet et Signature</i>", styles['Normal']))
        
        doc.build(elements)
        return filepath

    def generate_invoice(self, data: dict) -> str:
        """Génère un PDF de facture client."""
        # Logique similaire à l'ordonnance mais pour la facturation
        filename = f"facture_{data['id']}.pdf"
        filepath = os.path.join("assets/documents/invoices", filename)
        # ... implémentation simplifiée pour l'exemple ...
        return filepath

# Instance globale
pdf_service = PDFService()
