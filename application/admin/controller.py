from application.db.model import *
import logging
import requests
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from application.db.model import *
from application.admin import INSTITUTION_LIST_ENDPOINT
import json

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.route('/', methods=['GET'])
def index():
    return render_template('admin/index.html',
    institutions=get_all_iav_supported_institutions())

@admin_bp.route('/get_institutions_list', methods=['POST'])
def get_institutions_list():
    print 'admin get institutions request ...'
    if request.method == 'POST':
        req = requests.get(INSTITUTION_LIST_ENDPOINT)
        res = req.text
        print 'response = '+res
        institutions = []
        for bank_info in json.loads(res):
            print 'bi =',bank_info['products']
            if 'auth' in bank_info['products']:
                institutions.append(
                    IAVInstitutions(
                        name = bank_info['name'],
                        plaid_id = bank_info['id']))
        clear_institutions_table()
        current_app.db_session.add_all(institutions)
        current_app.db_session.commit()

    return render_template('admin/index.html',
    institutions=get_all_iav_supported_institutions())
