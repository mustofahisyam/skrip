from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, request
from flask_login import login_user, login_required
from ..email import send_email
from ..import db
from . import hasil
from ..models import Klustermodel, Permission
from ..decorators import permission_required
from .. import auth
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.io import export_png
from bokeh.embed import components
import pickle, os, sys

@hasil.route('/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ANALISIS)
def index():

	model = Klustermodel.query.with_entities(Klustermodel.id, Klustermodel.nama, Klustermodel.active).all()

	if model:
		nama = model[0][1]
	else:
		nama = None


	if request.method == 'POST':
		nama = request.form['model']
		query = Klustermodel.query.filter(Klustermodel.active==1).first()
		if query:
			query.active = 0
			db.session.commit()

		query = Klustermodel.query.filter(Klustermodel.nama==nama).first()
		query.active = 1
		db.session.commit()

	return render_template('admin/hasil/index.html',
							model=model,
							nama=nama)