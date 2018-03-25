from flask import render_template, redirect, request, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from flask_admin.contrib.sqla import ModelView
from . import adminis
from .. import db
from ..email import send_email
from ..models import User, Role, Permission
from .forms import AddUser
from ..decorators import permission_required


@adminis.route('/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.KELOLA)
def index():
	add_form = AddUser()
	if add_form.validate_on_submit():
		email = request.form['email']
		username = request.form['username']
		password = request.form['password']
		role_id = int(request.form['role_id'])
		query = User(email=email, username=username, 
					password=password, role_id=role_id)
		db.session.add(query)
		db.session.commit()
	user_role = User.query.join(
		Role, User.role_id == Role.id).add_columns(
		User.id, User.email, User.username, 
		Role.name, Role.id).all()
	get_role = Role.query.with_entities(Role.id, Role.name).all()
	return render_template('admin/admin/index.html',
							user_role = user_role,
							form = add_form,
							role = get_role)

@adminis.route('/delete', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.KELOLA)
def delete():
	if request.method == 'GET':
		user_del = User.query.filter_by(
							id=request.args.get('id')).first()
		db.session.delete(user_del)
		db.session.commit()
	return redirect(url_for('adminis.index'))
