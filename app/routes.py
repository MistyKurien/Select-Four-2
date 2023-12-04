from flask import render_template, flash, redirect, url_for, request, jsonify
# from app import app, cursor, conn #README: cursor is what we will be using to execute stuff
#, db) '''included earlier in tutorial'''
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, RegisterAdminForm, SearchForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Users, Queries
#from app import db
from datetime import datetime
from werkzeug.urls import url_parse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import aliased
from werkzeug.security import generate_password_hash
from config import Config

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return redirect(url_for('search'))

@app.route('/details/<year>/<teamName>')
@login_required
#localhost:5000/2010/Chicago%20Cubs
#README: %20 to signify space in URL
def teams(year, teamName):
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

    #requirements
    query = text("SELECT CONCAT(nameFirst, ' ', nameLast), "
             "team_W, team_L, team_rank, playerid, divid "
             "FROM people p join managers m using (playerid)"
             "JOIN teams t using (teamid, yearid)"
             " WHERE yearid = :year AND team_name = :teamName")

    with engine.connect() as con:
        record = con.execute(query, {"year": year, "teamName": teamName}).fetchall()
        if record == []:
            flash('Search yielded no results')
            return redirect(url_for('search'))
        record = record[0]

    manager = record[0]
    teamW = record[1]
    teamL = record[2]
    teamRank = record[3]
    playerid = record[4]
    division = record[5]

    if division == "W":
        division = "West"
    elif division == "E":
        division = "East"
    elif division == "C":
        division = "Central"
    else:
        division = "Not Available"


    #calculate pythagorean winning percentage for a year
    query = text("SELECT ((team_R * 2) / ((team_R ^ 2) + (team_RA ^2))) * 100"
             " as perc from teams where yearid = :year and team_name = :teamName")

    with engine.connect() as con:
        projection = con.execute(query, {"year": year, "teamName": teamName}).fetchone()[0]

    #store the query ran into the queries table
    query = Queries(body="Search for team = " + teamName + ", year = " + year, user_id = current_user.id)
    db.session.add(query)
    db.session.commit()

    return render_template('team.html', teamName=teamName, year=year,
                           teamW = teamW, teamL=teamL, teamRank = teamRank, manager=manager,
                           playerid =playerid, projection=projection, division=division)

#TODO fix this
@app.route('/details/<playerid>')
@login_required
def manager(playerid):
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    query = text("select team_name, m.yearid "
             "from managers m JOIN teams USING (teamid, yearid) "
             "where playerid = :playerid")

    with engine.connect() as con:
        record = con.execute(query, {"playerid": playerid}).fetchall()
        # TODO: ERROR CHECKING REQUIRED
        query = text("select CONCAT(nameFirst, ' ', nameLast) "
                 "from people m  "
                 "where playerid = :playerid")
        manager = con.execute(query, {"playerid": playerid}).fetchall()[0][0]

    query = Queries(body="Search for manager = " + playerid, user_id=current_user.id)
    db.session.add(query)
    db.session.commit()

    #check if the manager is also a player
    query = text("select distinct playerid "
                 "from managers where plyrMgr = 'y' "
                 "and playerid = :playerid")

    with engine.connect() as con:
        result = con.execute(query, {"playerid": playerid}).fetchall()
        print(playerid)
        print("Hellow")
        print(result)
        record2 = []
        if(result):
            print(record)
            print("\n\n")

            query = text("select team_name, m.yearid, m.position "
                         "from fielding m JOIN teams USING (teamid, yearid) "
                         "where playerid = :playerid")

            with engine.connect() as con:
                record2 = con.execute(query, {"playerid": playerid}).fetchall()

                # TODO: ERROR CHECKING REQUIRED
                query = text("select CONCAT(nameFirst, ' ', nameLast) "
                             "from people m  "
                             "where playerid = :playerid")
                manager = con.execute(query, {"playerid": playerid}).fetchall()[0][0]

    return render_template('manager.html', record=record, record2=record2, manager = manager)

@app.route('/division/<year>/<division>')
@login_required
def division(year, division):
    divid = division[0]
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    query = text("select team_rank, team_name from teams "
             "where team_rank < 4 and "
             "divid = :divid and yearid = :year and lgid='AL' "
             "order by team_rank")

    with engine.connect() as con:
        ALrecord = con.execute(query, {"divid": divid, "year": year}).fetchall()

        query = text("select team_rank, team_name from teams "
                 "where team_rank < 4 and "
                 "divid = :divid and yearid = :year and lgid='NL' "
                 "order by team_rank")

        NLrecord = con.execute(query, {"divid": divid, "year": year}).fetchall()

    query = Queries(body="Search for division = " + divid + ", year = " + year, user_id=current_user.id)
    db.session.add(query)
    db.session.commit()

    return render_template('division.html',
                           year=year, division=division,
                           ALrecord=ALrecord, NLrecord=NLrecord)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
            return redirect(url_for('teams', year=form.year.data, teamName =form.teamName.data))

    return render_template('search.html', title='Home Page', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        user = Users.query.filter_by(username=username).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterAdminForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data, email=form.email.data, admin=1)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered admin!')
        return redirect(url_for('login'))
    return render_template('register_admin.html', title='Register Admin', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<username>')
@login_required
def user(username):
    user = Users.query.filter_by(username=username).first_or_404()
    print(user)
    return render_template('user.html', user=user)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/view_logs', methods = ['GET'])
@login_required
def view_logs():
    users = Users.query.all()
    user_queries = {}
    for user in users:
        queries = Queries.query.filter_by(user_id=user.id).all()
        user_queries[user.id] = {"user": user, "queries": queries}

    return render_template('view_logs.html', user_queries=user_queries)