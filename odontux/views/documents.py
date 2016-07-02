# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/06/23
# v0.5
# licence BSD
#

import pdb
import os

from odontux.models import meta, documents

from odontux.odonweb import app

from flask import ( session, render_template, request, redirect, url_for, 
                    abort, make_response, jsonify)

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
