# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/06/19
# Licence BSD
#

import pdb

import checks
import constants

from odontux.models import meta, users, anamnesis

from odontux.odonweb import app

from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, 
                                Spacer, Table, TableStyle, Flowable )
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, LineStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

from gettext import gettext as _
import os
import cStringIO
import datetime
from decimal import Decimal

L_MARG = R_MARG = 20 * mm
T_MARG = 20 * mm
B_MARG = 20 * mm
WIDTH_PAPER = 210 * mm
HEIGHT_PAPER = 297 * mm

hori_start = L_MARG
hori_stop = WIDTH_PAPER - R_MARG
vert_start = T_MARG
vert_stop = HEIGHT_PAPER - B_MARG

def date_to_readable(date=datetime.date.today().isoformat()):
    date = date.split("-")
    return date[2] + "/" + date[1] + "/" + date[0]

def format_zip_code(zip_code):
    if ( constants.LOCALE == 'br' and zip_code.isdigit() and 
                                                        len(zip_code) == 8 ):
        return zip_code[:5] + "-" + zip_code[5:]
    else:
        return zip_code

def format_identity_2(id_2):
    if ( constants.LOCALE == 'br' and id_2.isdigit() and
                                                        len(id_2) == 11 ):
        return id_2[:3] + "." + id_2[3:6] + "." + id_2[6:9] + "-" + id_2[9:]
    else:
        return id_2

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
            + " - " +\
            format_zip_code(
                    doc.dental_info['dental_office'].addresses[-1].zip_code)
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
        #add_line(font, fontsize, text, doc.last_height)
        add_line(font, fontsize, text, align='left')

        if idx == 0:
            font = 'Times-Roman'
            fontsize = 11
            city = doc.dental_info['dental_office'].addresses[-1].city
            day = date_to_readable(doc.dental_info['appointment'].agenda.\
                                                    endtime.date().isoformat())
            text = city + ", o " + day
            add_line(font, fontsize, text, align='right')
        
        doc.last_height = doc.last_height + 5 * mm

    if hasattr(doc, 'patient_info'):
        def _new_height(patient_info_height):
            return patient_info_height - 5 * mm

        patient = doc.patient_info
        patient_info_width = WIDTH_PAPER / 2 + 20 * mm
        patient_info_height = HEIGHT_PAPER - T_MARG - doc.last_height

        canvas.drawString( patient_info_width, patient_info_height,
                            patient.firstname + " " + patient.lastname)
        patient_info_height = _new_height(patient_info_height)
        if patient.address_id:
            canvas.drawString( patient_info_width, patient_info_height,
                                patient.address.street + ", " + 
                                patient.address.street_number + " ; "+
                                patient.address.complement )
            patient_info_height = _new_height(patient_info_height)
            canvas.drawString( patient_info_width, patient_info_height,
                                patient.address.district + " - " +
                                format_zip_code(patient.address.zip_code))
            patient_info_height = _new_height(patient_info_height)
            canvas.drawString( patient_info_width, patient_info_height,
                                patient.address.city )

    canvas.restoreState()

def generate_base_survey_info(canvas, doc):
    canvas.saveState()
    logo_url = get_logo()
    if logo_url:
        logo = ImageReader(logo_url)
        width_logo = 45 * mm
        height_logo = 45 * mm
        canvas.drawImage(logo,
                        R_MARG/2, 
                        HEIGHT_PAPER - T_MARG/2 - height_logo, 
                        width_logo, height_logo
                        )
    canvas.restoreState()

def generate_patient_survey_info(canvas, doc):
    def add_line(font, fontsize, text, align='', varalign=0):
        canvas.setFont(font, fontsize)
        if align == 'centred' or align == 'center':
            canvas.drawCentredString( WIDTH_PAPER / 2 + varalign,
                                (HEIGHT_PAPER - T_MARG - doc.last_height),
                                text
                            )
        elif align == 'right':
            canvas.drawRightString( WIDTH_PAPER - R_MARG + varalign,
                            (HEIGHT_PAPER - T_MARG - doc.last_height),
                            text
                            )
        else:
            canvas.drawString( L_MARG + varalign, 
                        (HEIGHT_PAPER - T_MARG - doc.last_height),
                        text
                        )
        return True


    canvas.saveState()
    
    patient_name = doc.patient_info['patient'].firstname + " " +\
                    doc.patient_info['patient'].lastname
    patient_id_num = "CPF: " + doc.patient_info['patient'].identity_number_2
    patient_address_1 =  doc.patient_info['patient'].address.street +\
                    ", " + doc.patient_info['patient'].address.street_number +\
                    " ; " + doc.patient_info['patient'].address.complement
    patient_address_2 =  doc.patient_info['patient'].address.district +\
                    " " + doc.patient_info['patient'].address.zip_code +\
                    " - " + doc.patient_info['patient'].address.city
    patient_phone = doc.patient_info['patient'].phones[-1].indicatif +\
                    " " + doc.patient_info['patient'].phones[-1].area_code +\
                    " " + doc.patient_info['patient'].phones[-1].number
    patient_mail = doc.patient_info['patient'].mails[-1].email
                        
    patient_info = [
        ( patient_name, None ),
        ( patient_id_num, None ),
        ( patient_address_1, None ),
        ( patient_address_2, None ),
        ( patient_phone, None ),
        ( patient_mail, None ),
    ]

    font = 'Times-Roman'
    fontsize = 11
    for idx, text in enumerate(patient_info, start=0):
        # bold for Patient Name
        if not idx:
            font = 'Times-Bold'
        else:
            font = 'Times-Roman'
        if text[0]: 
            # varalign à cause logo
            varalign = 35 * mm
            add_line(font, fontsize, text[0], 'left', varalign)
        if text[1]:
            add_line(font, fontsize, text[1], 'right')

        doc.last_height = doc.last_height + 5 *mm

    doc.last_height = HEIGHT_PAPER - B_MARG - 20 * mm
    city = doc.patient_info['dental_office'].addresses[-1].city
    day = date_to_readable(doc.patient_info['appointment'].agenda.\
                                            endtime.date().isoformat())
    text = city + ", o " + day
    add_line( 'Times-Bold', 11, text, align='center')

    doc.last_height = doc.last_height + 5 *mm
    dentist_name = 'Dr ' + doc.patient_info['dentist'].firstname +\
                    " " + doc.patient_info['dentist'].lastname
    align_patient = - WIDTH_PAPER/4
    align_dentist = WIDTH_PAPER/4
    add_line( 'Times-Bold', 12, patient_name, 'center', align_patient )
    add_line( 'Times-Bold', 12, dentist_name, 'center', align_dentist )

    doc.last_height = doc.last_height + 5 * mm
    add_line( 'Times-Roman', 10, patient_id_num, 'center', align_patient )
    add_line( 'Times-Roman', 10, doc.patient_info['dentist'].registration,
                                                    'center', align_dentist)
#

    canvas.restoreState()

def make_patient_survey_info(patient_id, appointment_id):

    patient, appointment = checks.get_patient_appointment(patient_id,
                                                            appointment_id)
    dental_office = ( meta.session.query(users.DentalOffice)
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
    doc.patient_info = { 'dentist': dentist,
                        'patient': patient,
                        'appointment': appointment,
                        'dental_office': dental_office,
    }
    doc.last_height = 0
    Story.append(Spacer(1, 0 * mm))
    doc.build(Story, onFirstPage=generate_patient_survey_info)
    pdf_out = output.getvalue()
    output.close()
    return pdf_out

def make_base_survey(survey_id):
    survey = ( meta.session.query(anamnesis.Survey)
                .filter(anamnesis.Survey.id == survey_id)
                .one()
    )

    Story = []
    output = cStringIO.StringIO()
    doc = generate_doc_template(output)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='normal', fontName='Times-Roman',
                            fontSize=11, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='my_title', fontName='Times-Bold',
                            fontSize=16, alignment=TA_CENTER))

    Story.append(Spacer(1, 40 * mm))
    Story.append(Paragraph(_('Anamnesis'), styles['my_title']))
    Story.append(Spacer(1, 10 * mm))

    questions_list = []
    for question in sorted(survey.quests, 
                                    key=lambda question: question.position):

        questions_list.append( (
            str(question.position),
            Paragraph(question.question.question, styles['normal']),
            _('S') + "  " + _('N'),
            ""
            )
        )

    position_width = 5 * mm
    choices_width = 10 * mm
    question_width = 70 * mm
    comments_width = WIDTH_PAPER - L_MARG -R_MARG - choices_width -\
                                                question_width - position_width
    t = Table( questions_list, colWidths = ( position_width, question_width, 
                                            choices_width, comments_width )
    )

    t.setStyle(TableStyle( [
                    ('FONTSIZE', (0,0), (-1,-1), 11),
                    ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
                    ('FONTNAME', (2,0), (2,-1), 'Times-Bold'),
                    ('ALIGN', (1,0), (1, -1), 'LEFT'),
                    ('ALIGN', (1,0), (1, -1), 'LEFT'),
                    ('VALIGN', (0,0), (0, -1), 'MIDDLE'),
                    ('VALIGN', (2,0), (2, -1), 'MIDDLE'),
                    ])
    )
    Story.append(t)

    doc.build(Story, onFirstPage=generate_base_survey_info)
    pdf_out = output.getvalue()
    output.close()
    return pdf_out

def get_document_base(patient_id, appointment_id):
    patient, appointment = checks.get_patient_appointment(patient_id, 
                                                                appointment_id)
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
    styles.add(ParagraphStyle(name='normal', fontName='Times-Roman',
                            fontSize=11, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='my_title', fontName='Times-Bold',
                            fontSize=16, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='patient_data', fontName='Times-Roman',
                            fontSize=11, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='signature', fontName='Times-Roman',
                            fontSize=11, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='description', fontName='Times-Bold',
                            fontSize=11, alignment=TA_LEFT))

    return ( output, doc, Story, styles, patient, appointment, dentist, 
            dental_office )
 
def make_payment_receipt(patient_id, appointment_id, payment_form, mean): 

    output, doc, Story, styles, patient, appointment, dentist, dental_office =\
                                get_document_base(patient_id, appointment_id)

    doc.patient_info = patient
    Story.append(Paragraph(u'Recibo odontológico', styles['my_title']))
    Story.append(Spacer(1, 30 * mm))
    text = ( u'Recibo neste dia {} o pagamento em {} de {} {}, CPF: {} de uma soma total de {} {} por serviços odontológicos que serão detalhados na fatura.'.format(
                                        appointment.agenda.starttime.date(),
                                        mean.odontux_name,
                                        patient.firstname, patient.lastname,
                                format_identity_2(patient.identity_number_2),
                                        payment_form.amount.data,
                                        constants.CURRENCY_SYMBOL)
    )
    Story.append(Paragraph(text, styles['normal']))
    Story.append(Spacer(1, 20 * mm))
    Story.append(Paragraph(u'Este recibo NÃO tem valor legal. Será emitida a nota fiscal quando os serviços forem realizados.',
                                                            styles['normal']))
    Story.append(Spacer(1, 40 * mm))
    Story.append(Paragraph('Dr ' + dentist.firstname + " " + dentist.lastname,
                                            styles['signature']))
    Story.append(Paragraph(u'Cirurgião-Dentista - ' + dentist.registration, 
                                                        styles['signature']))

    doc.build(Story, onFirstPage=generate_dental_office_informations)
    pdf_out = output.getvalue()
    output.close()
    return pdf_out

def make_cessation_certificate(patient_id, appointment_id, cessation_form):

    output, doc, Story, styles, patient, appointment, dentist, dental_office =\
                                get_document_base(patient_id, appointment_id)

    Story.append(Paragraph('Atestado odontológico', 
                                                styles['my_title']))
    Story.append(Spacer(1, 30 * mm))
    text = ( cessation_form.first_part.data + patient.firstname + " " +
        patient.lastname + cessation_form.second_part.data + 
        format_identity_2(cessation_form.identity_number.data) +
        cessation_form.third_part.data +
        date_to_readable(cessation_form.day.data.isoformat())
        + cessation_form.fourth_part.data +
        str(cessation_form.days_number.data) + u" dias.") 

    Story.append(Paragraph(text, styles['normal']))
    Story.append(Spacer(1, 20 * mm))
    Story.append(Paragraph('Atenciosamente,', styles['normal']))
    Story.append(Spacer(1, 40 * mm))
    Story.append(Paragraph('Dr ' + dentist.firstname + " " + dentist.lastname,
                                            styles['signature']))
    Story.append(Paragraph(u'Cirurgião-Dentista - ' + dentist.registration, 
                                                        styles['signature']))

    doc.build(Story, onFirstPage=generate_dental_office_informations)
    pdf_out = output.getvalue()
    output.close()
    return pdf_out

def make_invoice_payment_bill(patient_id, appointment_id, bill_form):
    output, doc, Story, styles, patient, appointment, dentist, dental_office =\
                                get_document_base(patient_id, appointment_id)

    doc.patient_info = patient
    Story.append(Spacer(1, -10 * mm))
    Story.append(Paragraph(u'Fatura detalhada', styles['my_title']))
    Story.append(Spacer(1, 10 * mm))
    date_width = 20 * mm
    location_width = 20 * mm
    price_width = 35 * mm
    technical_gesture_width = WIDTH_PAPER - L_MARG - R_MARG -\
                        date_width - location_width - price_width
    t = Table( [ 
                [ _(u'Data'), _(u'Loc.'), _('Gesto técnico'), _('Preço') ]
            ],
            colWidths=( date_width, location_width, 
                        technical_gesture_width, price_width)
    )
    t.setStyle(TableStyle( [
                    ('FONTSIZE', (0,0), (-1,-1), 11),
                    ('FONTNAME', (0,0), (-1,0), 'Times-Bold' ),
                    ('ALIGN', (0,0), (1, 0), 'LEFT'),
                    ('ALIGN', (2,0), (2, 0), 'CENTER'),
                    ('ALIGN', (-1,0), (-1,0), 'RIGHT'),
                    ('LINEABOVE', (0,0), (-1,0), 2, colors.black),
                    ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
                    ] )
    )
    Story.append(t)
    
    gestures_list = []
    total_price = 0
    for gesture in sorted(bill_form.gestures, key=lambda x: x.date.data):
        if not gesture.gesture_name.data:
            continue
        gestures_list.append( (
                date_to_readable(gesture.date.data),
                gesture.anatomic_location.data,
                Paragraph(gesture.gesture_name.data, styles['normal']),
                constants.CURRENCY_SYMBOL + " " +str(gesture.price.data) )
                )
        total_price += Decimal(gesture.price.data)

    t = Table( gestures_list, colWidths = (date_width,
            location_width, technical_gesture_width, price_width)
    )
    t.setStyle(TableStyle( [
                        ('FONTSIZE', (0,0), (-1,-1), 11),
                        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman' ),
                        ('ALIGN', (0,0), (-2,-1), 'LEFT'),
                        ('ALIGN', (-1,0), (-1,-1), 'CENTER'),
                        ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
                        ('VALIGN', (0,0), (-1, -1), 'MIDDLE'),
                        ('LINEBELOW', (0,-1), (-1, -1), 1, colors.black),
                        ] )
    )
    Story.append(t)
    Story.append(Spacer(1, 1 * mm))
    t = Table( [ [ u"Total", 
                    constants.CURRENCY_SYMBOL + " " + str(total_price) ] ],
                    colWidths = ( WIDTH_PAPER - L_MARG - R_MARG - price_width,
                                    price_width )
    )
    t.setStyle(TableStyle( [
                             ('FONTSIZE', (0,0), (-1,-1), 11),
                            ('FONTNAME', (0,0), (-1,-1), 'Times-Bold' ),
                            ('ALIGN', (0,0), (0,0), 'LEFT'),
                            ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
                            ('LINEABOVE', (0,-1), (-1, -1), 1, colors.black),
                            ('LINEBELOW', (0,-1), (-1, -1), 2, colors.black),
                            ] )
    )
    Story.append(t)

    Story.append(Spacer(1, 30 * mm))
    Story.append(Paragraph('Dr ' + dentist.firstname + " " + dentist.lastname,
                                            styles['signature']))
    Story.append(Paragraph(u'Cirurgião-Dentista - ' + dentist.registration, 
                                                        styles['signature']))


    doc.build(Story, onFirstPage=generate_dental_office_informations)
    pdf_out = output.getvalue()
    output.close()
    return pdf_out

def make_quote(patient_id, appointment_id, quotes):

    output, doc, Story, styles, patient, appointment, dentist, dental_office =\
                                get_document_base(patient_id, appointment_id)

    doc.patient_info = patient
    Story.append(Spacer(1, -10 * mm))
    Story.append(Paragraph('Orçamento odontológico', styles['my_title']))
    Story.append(Spacer(1, 10 * mm))
    for index, quote in enumerate(quotes, start = 1):
        t = Table( [ [str(index) + "a" + " " + "Proposta:", 
                        "(" + str(quote.id) + ")" ] ], 
                    colWidths=( (WIDTH_PAPER - L_MARG - R_MARG) / 2) 
        )
        t.setStyle(TableStyle( [ 
                            ('FONTSIZE', (0,0), (1,0), 11),
                            ('FONTNAME', (0,0), (0,0), 'Times-Bold' ),
                            ('FONTNAME', (1,0), (1,0), 'Times-Roman'),
                            ('ALIGN', (1,0), (1,0), 'RIGHT'),
                            ] )
        )
        Story.append(t)
        appointment_width = 20 * mm
        location_width = 20 * mm
        price_width = 35 * mm
        technical_gesture_width = WIDTH_PAPER - L_MARG - R_MARG -\
                            appointment_width - location_width - price_width
        t = Table( [ [ u'Atend.', u'Loc.', u'Gesto técnico', 
                        u'Preço' ] ],
                    colWidths=( appointment_width, location_width, 
                                technical_gesture_width, price_width )
        )
        t.setStyle(TableStyle( [
                            ('FONTSIZE', (0,0), (-1,-1), 11),
                            ('FONTNAME', (0,0), (-1,-1), 'Times-Bold' ),
                            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                            ('ALIGN', (-2,0), (-1,-1), 'CENTER'),
                            ('LINEABOVE', (0,0), (-1, 0), 2, colors.black),
                            ('LINEBELOW', (0,0), (-1, 0), 1, colors.black),
                            ])
        )
        Story.append(t)
        quote_gestures = []
        for gesture in sorted(quote.gestures, key=lambda 
                                    x: x.appointment_number):
            quote_gestures.append( (
                str(gesture.appointment_number),
                str(gesture.anatomic_location),
                gesture.gesture.name,
                str(gesture.price) )
            )

        t = Table( quote_gestures, colWidths = (appointment_width,
                location_width, technical_gesture_width, price_width)
        )
        t.setStyle(TableStyle( [
                            ('FONTSIZE', (0,0), (-1,-1), 11),
                            ('FONTNAME', (0,0), (-1,-1), 'Times-Roman' ),
                            ('ALIGN', (0,0), (-2,-1), 'LEFT'),
                            ('ALIGN', (-1,0), (-1,-1), 'CENTER'),
                            ('LINEBELOW', (0,-1), (-1, -1), 1, colors.black),
                            ] )
        )
        Story.append(t)
        t = Table( [ [ u"Total", str(quote.total_price() ) ] ],
                    colWidths = ( WIDTH_PAPER - L_MARG - R_MARG - price_width,
                                    price_width )
        )
        t.setStyle(TableStyle( [
                             ('FONTSIZE', (0,0), (-1,-1), 11),
                            ('FONTNAME', (0,0), (-1,-1), 'Times-Bold' ),
                            ('ALIGN', (0,0), (0,0), 'LEFT'),
                            ('ALIGN', (-1,0), (-1,-1), 'CENTER'),
                            ('LINEBELOW', (0,-1), (-1, -1), 2, colors.black),
                            ] )
        )
        Story.append(t)
        years = months = weeks = 0
        if quote.treatment_duration:
            years = quote.treatment_duration.days / 365
            # if treatment last for one year or more, we'll print the treatment
            # duration in years and months.
            if years:
                months = ( (quote.treatment_duration.days - 
                                                        years * 365 ) / 30 )
            else:
                months = quote.treatment_duration.days / 30
                # if treatment last for more than 3 months, print treatment 
                # duration in months; else, print in weeks.
                if months < 3:
                    months = 0
                    weeks = 52 / quote.treatment_duration.days
                    
#        if any(years, months, weeks):
        if years and months:   
            Story.append(Paragraph(
                u"Tempo de tratamento estimado: " + str(years) + u" anos e " +
                str(months) + " meses.", styles['normal'])
            )
        elif years and not months:
            Story.append(Paragraph(
                u"Tempo de tratamento estimado: " + str(years) + u" anos.", 
                                                            styles['normal'])
            )
        elif months:
            Story.append(Paragraph(
                u"Tempo de tratamento estimado: " + str(months) + u" meses",
                                                            styles['normal'])
            )
        elif weeks:
            Story.append(Paragraph(
                u"Tempo de tratamento estimado: " + str(weeks) + u" semanas",
                                                            styles['normal'])
            )
        Story.append(Spacer(1, 10 * mm))
    Story.append(Paragraph(u'Orçamento aplicável até dia ' + 
                        date_to_readable(str(quote.validity.isoformat())),
                                                            styles['normal'])
    )
    t = Table( [
            [ '', '', ],
            [ patient.firstname + " " + patient.lastname, 
            u"Dr " + dentist.firstname + " " + dentist.lastname ],
            [ u"CPF: " + 
            format_identity_2(patient.identity_number_2), dentist.registration 
            ],
        ], 
        colWidths=( ( WIDTH_PAPER - L_MARG - R_MARG ) / 2 ),
        rowHeights=( 30 * mm, 5 * mm, 5 * mm )
    )
    t.setStyle(TableStyle( [ 
                            ('FONTSIZE', (0,0), (-1,-1), 11),
                            ('BOTTOMPADDING', (0,0), (-1,0), 15),
                            ('FONTNAME', (0,-2), (-1,-2), 'Times-Bold' ),
                            ('FONTNAME', (0,-1), (-1,-1), 'Times-Roman'),
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ] )
    )
    Story.append(t)

    doc.build(Story, onFirstPage=generate_dental_office_informations)
    pdf_out = output.getvalue()
    output.close()
    return pdf_out

def make_presence_certificate(patient_id, appointment_id, presence_form):

    output, doc, Story, styles, patient, appointment, dentist, dental_office =\
                                get_document_base(patient_id, appointment_id)

    Story.append(Paragraph('Atestado odontológico', 
                                                styles['my_title']))
    Story.append(Spacer(1, 30 * mm))
    text = ( presence_form.first_part.data + patient.firstname + " " +
        patient.lastname + presence_form.second_part.data + 
        format_identity_2(presence_form.identity_number.data) + 
        presence_form.third_part.data +
        date_to_readable(presence_form.day.data.isoformat()) + " das " + 
        presence_form.starttime.data + u" às " + presence_form.endtime.data + 
        "." )

    Story.append(Paragraph(text, styles['normal']))
    Story.append(Spacer(1, 20 * mm))
    Story.append(Paragraph('Atenciosamente,', styles['normal']))
    Story.append(Spacer(1, 40 * mm))
    Story.append(Paragraph('Dr ' + dentist.firstname + " " + dentist.lastname,
                                            styles['signature']))
    Story.append(Paragraph(u'Cirurgião-Dentista - ' + dentist.registration, 
                                                        styles['signature']))

    doc.build(Story, onFirstPage=generate_dental_office_informations)
    pdf_out = output.getvalue()
    output.close()
    return pdf_out

def make_requisition_certificate(patient_id, appointment_id, requisition_form):

    output, doc, Story, styles, patient, appointment, dentist, dental_office =\
                                get_document_base(patient_id, appointment_id)

    doc.patient_info = patient
    if requisition_form.requisition_type.data == constants.REQUISITION_X_RAY:
        Story.append(Paragraph('Requisição radiográfica',
                                                styles['my_title']))
    elif requisition_form.requisition_type.data ==\
                                                constants.REQUISITION_BIOLOGIC:
        Story.append(Paragraph('Requisição exame biológico',
                                                styles['my_title']))
    Story.append(Spacer(1, 30 * mm))
#    text = ( presence_form.first_part.data + patient.firstname + " " +
#        patient.lastname + presence_form.second_part.data + 
#        presence_form.identity_number.data + presence_form.third_part.data +
#        date_to_readable(presence_form.day.data.isoformat()) + " das " + 
#        presence_form.starttime.data + u" às " + presence_form.endtime.data + 
#        "." )
#
    Story.append(Paragraph('Prezado colega,', styles['normal']))
    Story.append(Spacer(1, 10 * mm))
    text = ( requisition_form.first_part.data + patient.firstname + " " +
            patient.lastname + " portador do CPF: " +
            format_identity_2(patient.identity_number_2) +
            requisition_form.second_part.data )
    Story.append(Paragraph(text, styles['normal']))
    Story.append(Spacer(1, 20 * mm))
    Story.append(Paragraph('Atenciosamente,', styles['normal']))
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
    Story.append(Paragraph(patient.address.street + ", " +\
                patient.address.street_number + " " +\
                patient.address.complement, styles['patient']))
    Story.append(Paragraph(patient.address.district + " " +\
                format_zip_code(patient.address.zip_code) + " " +\
                patient.address.city, styles['patient']))
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
    Story.append(Paragraph(
            date_to_readable(appointment.agenda.endtime.date().isoformat()),
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
