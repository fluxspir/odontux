# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/06/23
# v0.5
# licence BSD
#

import pdb
import os

import md5
import magic
import cStringIO
from PIL import Image

from odontux.models import meta, documents

from odontux.odonweb import app

from flask import ( session, render_template, request, redirect, url_for, 
                    abort, make_response, jsonify)

def create_thumbnail_img(file_id, size=(128, 128)):
    document_in_db = ( meta.session.query(documents.Files)
                    .filter(documents.Files.id == file_id)
                    .one_or_none()
    )
    if not document_in_db:
        return None
    with open(os.path.join(app.config['DOCUMENT_FOLDER'], document_in_db.md5), 
                                                                    'rb') as f:
        try:
            img = Image.open(f)
        except IOError:
            return None
       
        else:
            img.thumbnail(size)
            img_io = cStringIO.StringIO()
            img.save(img_io, 'PNG')
            filename = md5.new(img_io.getvalue()).hexdigest()
            file_exists = ( meta.session.query(documents.Thumbnail)
                                .filter(documents.Thumbnail.md5 == filename)
                                .one_or_none()
            )
            if not file_exists:
                with open(os.path.join(
                            app.config['THUMBNAIL_FOLDER'], filename), 'w') as f:
                    f.write(img_io.getvalue())
                thumbnail_values = {
                    'md5': filename,
        #            'size': size,
                    'mimetype': 'image/png',
                    'file_id': file_id,
                }
                new_thumbnail = documents.Thumbnail(**thumbnail_values)
                meta.session.add(new_thumbnail)
                meta.session.commit()
            else:
                new_thumbnail = file_exists
    return new_thumbnail

def insert_document_in_db(document_data, file_type, appointment):
    filename = md5.new(document_data).hexdigest()
    file_exists = ( meta.session.query(documents.Files)
                        .filter(documents.Files.md5 == filename)
                        .one_or_none()
    )
    if not file_exists:
        with open(os.path.join(
                app.config['DOCUMENT_FOLDER'], filename), 'w') as f:
            f.write(document_data)
        m = magic.open(magic.MAGIC_MIME)
        m.load()
        mimetype = m.file(os.path.join(
                            app.config['DOCUMENT_FOLDER'], filename))
        file_values = {
            'md5': filename,
            'file_type': file_type,
            'mimetype': mimetype,
            'timestamp': appointment.agenda.endtime
        }
        new_file = documents.Files(**file_values)
        meta.session.add(new_file)
        meta.session.commit()
    else:
        new_file = file_exists

    thumbnail = create_thumbnail_img(new_file.id)
    
    return new_file

@app.route('/display_file&fid=<int:file_id>')
def display_file(file_id):
    my_file = ( meta.session.query(documents.Files)
                    .filter(documents.Files.id == file_id)
                    .one_or_none()
    )
    with open(os.path.join(
                        app.config['DOCUMENT_FOLDER'], my_file.md5), 'r') as f:
        file_out = f.read()

    response = make_response(file_out)
    response.mimetype = my_file.mimetype
    return response

@app.route('/display_thumbnail&tid=<int:thumbnail_id>')
def display_thumbnail(thumbnail_id):
    my_thumbnail = ( meta.session.query(documents.Thumbnail)
                    .filter(documents.Thumbnail.id == thumbnail_id)
                    .one_or_none()
    )
    with open(os.path.join(
                        app.config['THUMBNAIL_FOLDER'], my_thumbnail.md5), 
                                                                    'r') as f:
        file_out = f.read()

    response = make_response(file_out)
    response.mimetype = my_thumbnail.mimetype
    return response

