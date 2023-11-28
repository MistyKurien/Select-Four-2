from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, cursor #README: cursor is what we will be using to execute stuff
#, db) '''included earlier in tutorial'''
from app.forms import SearchForm
#from flask_login import current_user, login_user, logout_user, login_required
#from app.models import User
from datetime import datetime
#from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
#@login_required
def index():
    #just testing
    # cursor.execute("SELECT * from managers LIMIT 10") #README: i just added this to test!
    # res = cursor.fetchall()
    # return jsonify(res) #README: notice how i am using cursor which is defined in __init__.py
    #return "hello world"
    #return "Connected to mariadb"
    # user = {'username' : 'Misty_Kurien1'}
    # posts = [
    #     {
    #         'author': {'username': 'Salma'},
    #         'body' : 'I love databases'
    #     },
    #     {
    #         'author' : {'username' : 'Ciara'},
    #         'body': 'Elmos world'
    #     }
    #
    # ]
    #return render_template('index.html')
    return render_template('index.html')

@app.route('/details/<year>/<teamName>')
#localhost:5000/2010/Chicago%20Cubs
#README: %20 to signify space in URL
def teams(year, teamName):
    query = "SELECT team_W, team_L, team_rank FROM teams WHERE yearid = %s AND team_name = %s"
    cursor.execute(query, (year, teamName))
    record = cursor.fetchall()[0]
    teamW = record[0]
    teamL = record[1]
    teamRank = record[2]
    #return jsonify(cursor.fetchall())
    return render_template('team.html', teamName=teamName,
                           teamW = teamW, teamL=teamL, teamRank = teamRank)

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
            return redirect(url_for('teams', year=form.year.data, teamName =form.teamName.data))

    return render_template('search.html', title='Search', form=form)


# @app.route('/login', methods=['GET','POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             flash('Invalid username or password')
#             return redirect(url_for('login'))
#         login_user(user, remember=form.remember_me.data)
#         next_page = request.args.get('next')
#         if not next_page:
#             #or url_parse(next_page).netloc != '':
#             next_page = url_for('index')
#         return redirect(next_page)
#     return render_template('login.html', title='Sign In', form=form)
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Registration Successful!')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)
#
# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('index'))
#
# @app.route('/user/<username>')
# @login_required
# def user(username):
#     user = User.query.filter_by(username=username).first_or_404()
#     posts = [
#         {'author': user, 'body': 'Test post #1'},
#         {'author': user, 'body': 'Test post #2'}
#     ]
#     return render_template('user.html', user=user, posts=posts)
#
# @app.before_request
# def before_request():
#     if current_user.is_authenticated:
#         current_user.last_seen = datetime.utcnow()
#         db.session.commit()
#
# @app.route('/edit_profile', methods=['GET', 'POST'])
# @login_required
# def edit_profile():
#     form = EditProfileForm()
#     if form.validate_on_submit():
#         current_user.username = form.username.data
#         current_user.about_me = form.about_me.data
#         db.session.commit()
#         flash('Your changes have been saved.')
#         return redirect(url_for('edit_profile'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.about_me.data = current_user.about_me
#     return render_template('edit_profile.html', title='Edit Profile',
#                            form=form)