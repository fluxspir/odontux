# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/06/19
# Licence BSD
#

import pdb

from odontux.models import meta, users

from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, 
                                Spacer, Table, TableStyle, Flowable )
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, LineStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

import os
import cStringIO
import checks
import constants

L_MARG = R_MARG = 20 * mm
T_MARG = 20 * mm
B_MARG = 20 * mm
WIDTH_PAPER = 210 * mm
HEIGHT_PAPER = 297 * mm

hori_start = L_MARG
hori_stop = WIDTH_PAPER - R_MARG
vert_start = T_MARG
vert_stop = HEIGHT_PAPER - B_MARG


def generate_doc_template(output):
    doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=R_MARG,
                    leftMargin=L_MARG, topMargin=T_MARG, bottomMargin=B_MARG)

    return doc

def get_logo():
    dental_office_logo = checks.get_dental_office_logo()
    if os.path.exists(dental_office_logo):
        #logo = Image(dental_office_logo, 50 * mm, 50 * mm)
        return dental_office_logo
    return None

def generate_dental_office_informations(canvas, doc):

    def add_line(font, fontsize, text, align=''):
        canvas.setFont(font, fontsize)
        if align == 'centred':
            canvas.drawCentredString( WIDTH_PAPER / 2,
                                (HEIGHT_PAPER - T_MARG - doc.last_height),
                                text
                            )
        elif align == 'right':
            canvas.drawRightString( WIDTH_PAPER - R_MARG,
                            (HEIGHT_PAPER - T_MARG - doc.last_height),
                            text
                            )
        else:
            canvas.drawString( L_MARG, 
                        (HEIGHT_PAPER - T_MARG - doc.last_height),
                        text
                        )
        return True

    canvas.saveState()
    font = "Times-Roman"
    fontsize = 11
    logo_url = get_logo()
    if logo_url:
        logo = ImageReader(logo_url)
        width_logo = 50 * mm
        height_logo = 50 * mm
        canvas.drawImage(logo, 
                        WIDTH_PAPER/2 - width_logo / 2,
                        HEIGHT_PAPER - T_MARG - height_logo,
                        width_logo, height_logo
                        )

    dental_office_name = doc.dental_info['dental_office'].office_name
    responsable = 'RT - CD: Dr ' + doc.dental_info['dentist'].lastname + " " +\
                                    doc.dental_info['dentist'].firstname
    registration = doc.dental_info['dentist'].registration
    street_address = doc.dental_info['dental_office'].addresses[-1].street\
            + " " + doc.dental_info['dental_office'].addresses[-1].complement
    city_address = doc.dental_info['dental_office'].addresses[-1].city\
            + " - " + doc.dental_info['dental_office'].addresses[-1].zip_code
    if doc.dental_info['dentist'].mails:
        email = doc.dental_info['dentist'].mails[-1].email
    elif doc.dental_info['dental_office'].mails:
        email = doc.dental_info['dental_office'].mails[-1].email
    else:
        email = ""

    dental_office_informations = [
        dental_office_name,
        responsable, 
        registration,
        street_address,
        city_address,
        email
    ]
    for phone in doc.dental_info['dental_office'].phones:
        dental_office_informations.append(
            "(" + phone.area_code + ") " + phone.number
        )

    for idx, text in enumerate(dental_office_informations, start=0):
        if idx == 0 or idx == 1:
            font = 'Times-Bold'
        else:
            font = 'Times-Roman'
        fontsize = 11
        add_line(font, fontsize, text, doc.last_height)

        if idx == 0:
            font = 'Times-Roman'
            fontsize = 11
            city = doc.dental_info['dental_office'].addresses[-1].city
            day = doc.dental_info['appointment'].agenda.endtime.date().isoformat()
            text = city + ", o " + day
            add_line(font, fontsize, text, align='right')
        
        doc.last_height = doc.last_height + 5 * mm

    canvas.restoreState()

def get_document_base(patient_id, appointment_id):
    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)
    dental_office = (
        meta.session.query(users.DentalOffice)
           .filter(users.DentalOffice.id == 
                                    appointment.dental_unit.dental_office_id)
            .one()
    )
    dentist = ( meta.session.query(users.OdontuxUser)
        .filter(users.OdontuxUser.id == appointment.dentist_id)
        .one()
    )

    Story = []
    
    output = cStringIO.StringIO()
    doc = generate_doc_template(output)
    #doc = generate_dental_office_informations(doc)

    dental_info = { 'dental_office': dental_office, 
                    'dentist': dentist, 
                    'appointment': appointment
                }
    doc.dental_info = dental_info
    doc.last_height = 0

    Story.append(Spacer(1, 70 * mm))
    styles = getSampleStyleSheet()

    return ( output, doc, Story, styles, patient, appointment, dentist, 
            dental_office )
 
def make_presence_certificate(patient_id, appointment_id, presence_form):

    output, doc, Story, styles, patient, appointment, dentist, dental_office =\
                                get_document_base(patient_id, appointment_id)
    styles.add(ParagraphStyle(name='certificate_title', fontName='Times-Bold',
                            fontSize=16, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='signature', fontName='Times-Roman',
                            fontSize=11, alignment=TA_CENTER))

    Story.append(Paragraph('Atestado odontológico', 
                                                styles['certificate_title']))
    Story.append(Spacer(1, 30 * mm))
    text = ( presence_form.first_part.data + patient.firstname + " " +
        patient.lastname + presence_form.second_part.data + 
        presence_form.identity_number.data + presence_form.third_part.data +
        presence_form.day.data.isoformat() + " das " + 
        presence_form.starttime.data + u" às " + presence_form.endtime.data + 
        "." )

    Story.append(Paragraph(text, styles['Normal']))
    Story.append(Spacer(1, 20 * mm))
    Story.append(Paragraph('Atenciosamente,', styles['Normal']))
    Story.append(Spacer(1, 40 * mm))
    Story.append(Paragraph('Dr ' + dentist.firstname + " " + dentist.lastname,
                                            styles['signature']))
    Story.append(Paragraph(u'Cirurgião-Dentista - ' + dentist.registration, 
                                                        styles['signature']))

    doc.build(Story, onFirstPage=generate_dental_office_informations)
    pdf_out = output.getvalue()
    output.close()
    return pdf_out


def make_prescription(patient_id, appointment_id, prescription_form):

    output, doc, Story, styles, patient, appointment, dentist, dental_office =\
                                get_document_base(patient_id, appointment_id)

    styles.add(ParagraphStyle(name='prescription_title', fontName='Times-Bold',
                        fontSize=16, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='patient', fontName='Times-Roman', 
                        fontSize=11, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='posologia', fontName='Times-Roman',
                        fontSize=11, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='prescriptor', fontName='Times-Roman',
                        fontSize=11, alignment=TA_CENTER))

    if any( [ drug.special.data for drug in prescription_form.drugs ] ):
        text = 'Receituário controle especial'
    else:
        text = 'Receituário'

    Story.append(Paragraph(text, styles['prescription_title']))
    Story.append(Spacer(1, 5 * mm))

    # Patient's dentification 
    Story.append(Paragraph('Patiente: ' + patient.firstname + " "\
                                    + patient.lastname, styles['patient']))
    Story.append(Paragraph(patient.family.addresses[-1].street + " " +\
                patient.family.addresses[-1].complement, styles['patient']))
    Story.append(Paragraph(patient.family.addresses[-1].city + " " +\
                patient.family.addresses[-1].zip_code, styles['patient']))
    Story.append(Spacer(1, 5 * mm))
    for drug in sorted(prescription_form.drugs, key=lambda x: x.position.data):
        if not drug.position.data:
            continue
        t = Table( [ [drug.molecule.data, drug.packaging.data ] ], 
                    colWidths=( (WIDTH_PAPER - L_MARG - R_MARG) / 2) )
        t.setStyle(TableStyle( [ 
                            ('FONTSIZE', (0,0), (1,0), 11),
                            ('FONTNAME', (0,0), (0,0), 'Times-Bold' ),
                            ('FONTNAME', (1,0), (1,0), 'Times-Roman'),
                            ('ALIGN', (1,0), (1,0), 'RIGHT'),
                            ] )
        )
        Story.append(t)
        
        ptext = 'Tomar ' + drug.posologia.data + ' durante ' +\
            str(drug.dayssupply.data) + " dias ; " + drug.comments.data
        Story.append(Paragraph(ptext, styles['posologia']))

        Story.append(Spacer(1, 10 * mm))

    Story.append(Spacer(1, 30 * mm))
    prescriptor = 'Dr ' + dentist.firstname + " " + dentist.lastname + " - " +\
                                                        dentist.registration
    Story.append(Paragraph(prescriptor, styles['prescriptor']))
    Story.append(Paragraph(appointment.agenda.endtime.date().isoformat(), 
                                                        styles['prescriptor']))

    if any( [drug.special.data for drug in prescription_form.drugs ]):
        
        t = Table ( [
                    [ 'IDENTIFICAÇÃO DO COMPRADOR', 
                                            'IDENTIFICAÇÃO DO FORNECEDOR' ],
                    [ 'Nome:', '' ],
                    [ '', '' ],
                    [ 'Ident:                           Órg. Emissor:', '' ],
                    [ 'End.:', '' ],
                    [ '', ''],
                    [ 'Cidade:                                            UF:',
                                                                        '' ],
                    [ 'Telefone:', 'Assinatura do Farmacêutico  DATA:']
                    ], 
                    colWidths=( (WIDTH_PAPER - L_MARG - R_MARG - 10*mm) /2),
                    spaceBefore=(5 * mm)
                )
        t.setStyle(TableStyle( [
                        ('ALIGN', (0,0), (1,0), 'CENTER'),
                        ('GRID', (0,0), (1,0), .25, colors.black),
                        ('GRID', (0,0), (0,-1), .25, colors.black ),
                        ('BOX', (0,0), (-1,-1), .25, colors.black )
                        ] ) 
        )
        Story.append(t)

    doc.build(Story, onFirstPage=generate_dental_office_informations)
    pdf_out = output.getvalue()
    output.close()
    return pdf_out
