#from flask import render_template
#from flask import redirect
#from flask import flash
#from app import LoginForm
#from app import myapp_obj
# 
#@myapp_obj.route("/login", methods=['GET', 'POST'])
#def login():
#    form = LoginForm()
#    if form.validate_on_submit():
#        flash(f'Here are the input {form.username.data} and {form.password.data}')
#        return redirect('/')
#    return render_template('login.html', form=form)
#

from flask import render_template, request, flash, redirect, url_for
from . import bp
from app.forms import LoginForm




@bp.route("/login", methods=["GET", "POST"])
def login():

        # validate form here later; for now just demo the POST path
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Here are the input {form.username.data} and {form.password.data}')
        return redirect('/')
    
    # Because the file is at app/auth/templates/auth/login.html:
    return render_template("auth/login.html", form=form)
