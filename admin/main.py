from admin import app, db
from admin.models import *
from flask import Flask, url_for, redirect, render_template, request
from wtforms import form
import flask_login as login
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(AdminModel).get(user_id)

def is_accessible(self):
    return login.current_user.is_authenticated

# the dashboard contains 7 sections: Profile, Index, Accounts, Teams, Projects, Tags and Tasks 
#  ---------------- Profile section ---------------- 


#1. Login to the dashboard 
@app.route('/login/', methods=('GET', 'POST'))
def login_view():
    # handle user login
    if request.method == 'POST':
        email_ = request.form.get('email_')
        pass_ = request.form.get('pass_')

        if email_ == "" or pass_ == "":
            return {'message':'missing arguments'}

        user = AdminModel.find_by_email(email_)
        if not user or not user.check_password(pass_):
            return {'message':'entries are not corrcet! please check Email or password'}
        login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.statistics'))
    else:
        return render_template('login.html')

#2. Logout 
@app.route('/logout/')
def logout_view():
    login.logout_user()
    return redirect(url_for('.login_view'))

#3. Admin profile (show & update)
@app.route('/Profile/', methods=('GET', 'POST'))
@login.login_required
def show_profile():
    if request.method == 'POST':
        id = request.form.get('the_id')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        admin = AdminModel.find_by_id(id)
        if admin:
            admin.first_name = fname
            admin.last_name = lname
            admin.save_to_db()
    return render_template("profile.html")    


#  ---------------- Index section ---------------- 


#1. first page redirect 
@app.route('/')
def index():
    if not login.current_user.is_authenticated:
        return redirect(url_for('.login_view'))
    return redirect(url_for('.statistics'))

#2. index page
@app.route('/index/')
@login.login_required
def statistics():
    index_info = {}
    index_info['proects_number'] = db.session.query(ProjectModel).count()
    index_info['teams_number'] = db.session.query(TeamModel).count()
    index_info['users_number'] = db.session.query(UserModel).count()

    now = datetime.datetime.now()
    tasks_in_db = TaskModel.query.all()
    all_tasks = {}
    today_tasks = []
 
    for i in tasks_in_db:
        if i.start_at.date() == now.date():
            all_tasks['id'] = i.id
            all_tasks['title'] = i.title
            all_tasks['start_at'] = i.start_at.strftime("%I:%M %P").upper()
            all_tasks['user'] = i.user
            all_tasks['project'] = i.project

            today_tasks.append(all_tasks.copy())

    index_info['today_tasks'] = today_tasks

    if today_tasks:
        return render_template('index.html', **index_info)


#  ---------------- Accounts section ---------------- 


#1. Add a new user
@app.route('/New_acc', methods=('GET', 'POST'))
@login.login_required
def new_user():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('passowrd')
        bio = request.form.get('bio')
        local_phone_number = request.form.get('local_phone_number')
        dialling_code = request.form.get('dialling_code')
        timezone = request.form.get("timezone")
        if email == "" or password == "" or local_phone_number == None:
            return {'message':'missing arguments'}
        user = UserModel.find_by_email(email)
        if user:
            return {'message':'existing user'}

        user = UserModel(id = None, timezone=timezone, dialling_code= dialling_code, local_phone_number= local_phone_number, email = email, name = name, bio = bio, _password = password)
        user.set_password(password)
        user.save_to_db()
        return redirect(url_for('.show_userslist'))
    else:
        return render_template('user-add.html')

#2. update & show a user info 
@app.route('/Admin/Accounts/<uuid:uuid>/', methods=('GET', 'POST'))
@login.login_required
def update_user(uuid):
    if request.method == 'POST':
        user = UserModel.find_by_id(uuid)
        if user:
            user.name = request.form.get('name')
            user.bio = request.form.get('bio')
            user.local_phone_number = request.form.get('local_phone_number')
            user.dialling_code = request.form.get('dialling_code')
            user.timezone = request.form.get('timezone')

            user.save_to_db()
            return render_template('user-update.html', **user.json())
    if request.method == 'GET':
        user = UserModel.find_by_id(uuid)
        if user:
            return render_template('user-update.html', **user.json())    

#3. delete a user
@app.route('/Admin/Accounts/delete/<uuid:uuid>/', methods=['GET'])
@login.login_required
def delete_user(uuid):
    if request.method == 'GET':
        user = UserModel.find_by_id(uuid)
        if user:
            user.delete_from_db()
            return redirect(url_for('.show_userslist'))
        return render_template('secret.html')

#4. show the list of users
@app.route('/AccountsList/')
@login.login_required
def show_userslist():
    return render_template("users.html", **{'users': list(map(lambda x: x.json(), UserModel.query.all()))})    


#  ---------------- Project section ----------------


#1. Add a new project
@app.route('/New_project', methods=('GET', 'POST'))
@login.login_required
def New_project():
    if request.method == 'POST':

        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        new_project = ProjectModel(id = None, title = title, description = description, status = status)
        new_project.save_to_db()
        team_members = [] # for holding the ids of users
        members_roles = []
        self_ = request.form.get('self') # number of users 

        for i in range(int(self_)): 
            team_members.append('team-member' + str(i)) 
            members_roles.append('member-role' + str(i)) 

        team_name =  new_project.title + '-team'
        team = TeamModel(id = None, name = team_name, description = description) # add a new team without members
        quick_list = []
        quick_list.append(new_project)
        team.project = quick_list       
        new_project.team = team

        for i in range(len(team_members)):
            user_id = request.form.get(team_members[i])
            user = UserModel.find_by_id(user_id)
            role_ = request.form.get(members_roles[i])
            members = TeamMemberModel(user_id = user_id, role = role_, team_id = team.id)
            members.team = team
            members.member = user

        team.save_to_db()
        new_project.save_to_db()
        return redirect(url_for('.show_projectslist'))
        
    else:
        users = {'users': list(map(lambda x: x.json(), UserModel.query.all()))}
        return render_template('project-add.html',**users)

#2. update & show a project info 
@app.route('/Admin/Projects/<int:id>/', methods=('GET', 'POST'))
@login.login_required
def update_project(id):
    if request.method == 'POST':
        project = ProjectModel.find_by_id(id)

        if project:
            project.title = request.form.get('title')
            project.description = request.form.get('description')
            project.status = request.form.get('status')
            project.save_to_db()
            team_members = [] # for holding the ids of users
            members_roles = []
            self_ = request.form.get('self_') # number of users 

            for i in range(int(self_)): 
                # set the names of select tags in the form
                team_members.append('team-member' + str(i)) 
                members_roles.append('member-role' + str(i)) 

            team = TeamModel.find_by_id(project.team_id)
            if team:
                team.name = request.form.get('name')
                team.description = request.form.get('description')
                members_model = TeamMemberModel.find_by_team_id(id)

                for i in range(len(team_members)):
                    user_id = request.form.get(team_members[i])
                    user = UserModel.find_by_id(user_id)
                    role = request.form.get(members_roles[i])
                    members_model[i].user_id = user_id
                    members_model[i].role = role
                    members_model[i].member = user

                team.save_to_db()

            return redirect(url_for('.show_ProjectsList'))

    if request.method == 'GET':
        project = ProjectModel.find_by_id(id)
        if project:
            team = TeamModel.find_by_id(project.team_id)
            team_info = {}

            if team:
                # create a list for holding all the members in the team with roles and so on
                members_list = []
                # a dic for member info including the name, id and role
                member = {}
                # the retrived data model to compare with and store from
                members_model = []
                members_model = TeamMemberModel.find_by_team_id(id)
            
            for member_model in members_model:
                member['id'] = member_model.user_id
                member['role'] = member_model.role
                members_list.append(member.copy())

            team_info['id'] = team.id
            team_info['name'] = team.name
            team_info['description'] = team.description
            team_info['created_at'] = team.created_at
            team_info['updated_at'] = team.updated_at
            team_info['project_'] = project.json()
            team_info['members'] = members_list
            team_info['users'] = list(map(lambda x: x.names(), UserModel.query.all()))

        return render_template('project-update.html', **team_info)   

#3. delete a project
@app.route('/Admin/Projects/delete/<int:id>/', methods=['GET'])
@login.login_required
def delete_project(id):
    if request.method == 'GET':
        project = ProjectModel.find_by_id(id)
        if project:
            team = project.team 
            actual_team = TeamModel.find_by_id(team.id)
            if actual_team :
                actual_team.delete_from_db()
            return redirect(url_for('.show_projectslist'))

#4. show the list of projects
@app.route('/ProjectsList/')
@login.login_required
def show_ProjectsList():
    project_number = db.session.query(ProjectModel).count()
    projects_in_db = ProjectModel.query.all()
    all_projects = {}
    projects_names = []
 
    for i in projects_in_db:
        all_projects['id'] = i.id
        all_projects['title'] = i.title
        all_projects['status'] = i.status
        team = i.team
        team_info = {}
        members_list = []
        member = {}
        members_model = []
        members_model = TeamMemberModel.find_by_team(team)
 
        for member_model in members_model:
            member['id'] = member_model.user_id
            user_name = UserModel.find_by_id(member_model.user_id)
            member['name'] = user_name.name
            member['role'] = member_model.role
            members_list.append(member.copy())
        all_projects['members'] = members_list
        projects_names.append(all_projects.copy())

    return render_template("projects.html", **{'projects':projects_names} ) 


#  ---------------- Tag section ---------------- 

#1. Add a new tag
@app.route('/New_tag', methods=('GET', 'POST'))
@login.login_required
def New_tag():
    if request.method == 'POST':
        name = request.form.get('name')
        tag = TagModel(id= None, name=name)

        tag.save_to_db()
    return redirect(url_for('.show_tagslist'))

#2. update & show a tag info 
@app.route('/udate_tag/', methods=('GET', 'POST'))
@login.login_required
def update_tag():
    if request.method == 'POST':
        id = request.form.get('new_tag_id')
        tag = TagModel.find_by_id(id)
        if tag:
            name = request.form.get('new_tag_name')
            tag.name = name
            tag.save_to_db()
            return redirect(url_for('.show_tagslist'))

#3. delete a tag
@app.route('/Admin/Tags/delete/<int:id>/', methods=['GET'])
@login.login_required
def delete_tag(id):
    if request.method == 'GET':
        tag = TagModel.find_by_id(id)
        if tag:
            tag.delete_from_db()
            return redirect(url_for('.show_tagslist'))
        return render_template('secret.html')

#4. show the list of tags
@app.route('/TagsList/')
@login.login_required
def show_tagslist():
    return render_template("tags.html", **{'tags': list(map(lambda x: x.json(), TagModel.query.all()))})    


#  ---------------- Team section ----------------


#1. Add a new team
@app.route('/New_team', methods=('GET', 'POST'))
@login.login_required
def New_team():
    if request.method == 'POST':

        team_members = [] # for holding the ids of users
        members_roles = []
        self_ = request.form.get('self') # number of users 

        for i in range(int(self_)): 
            # set the names of select tags in the form
            team_members.append('team-member' + str(i)) 
            members_roles.append('member-role' + str(i)) 
            
        name = request.form.get('name')
        description = request.form.get('description')
        team = TeamModel(id = None, name = name, description = description) # add a new team without members

        # add members 
        for i in range(len(team_members)):
            user_id = request.form.get(team_members[i])
            user = UserModel.find_by_id(user_id)
            role = request.form.get(members_roles[i])
            members = TeamMemberModel(user_id = user_id, role = role, team_id = team.id)
            members.team = team
            members.member = user
        team.save_to_db()
        return redirect(url_for('.show_teamslist'))
    else:
        users = {'users': list(map(lambda x: x.json(), UserModel.query.all()))}
        return render_template('team-add.html', **users)

#2. update & show a team info 
@app.route('/Admin/Teams/<int:id>/', methods=('GET', 'POST'))
@login.login_required
def update_team(id):
    if request.method == 'POST':

        team_members = [] # for holding the ids of users
        members_roles = []
        self_ = request.form.get('self_') # number of users 
      
        for i in range(int(self_)): 
            # set the names of select tags in the form
            team_members.append('team-member' + str(i)) 
            members_roles.append('member-role' + str(i)) 
       
        team = TeamModel.find_by_id(id)
        if team:
            team.name = request.form.get('name')
            team.description = request.form.get('description')
            members_model = TeamMemberModel.find_by_team_id(id)
            for i in range(len(team_members)):
                user_id = request.form.get(team_members[i])
                user = UserModel.find_by_id(user_id)
                role = request.form.get(members_roles[i])
                members_model[i].user_id = user_id
                members_model[i].role = role
                members_model[i].member = user

            team.save_to_db()
            return redirect(url_for('.show_teamslist'))
    if request.method == 'GET':
        # get the team info
        team = TeamModel.find_by_id(id)
        # dic for team info with users and roles 
        team_info = {}

        if team:
            # create a list for holding all the members in the team with roles and so on
            members_list = []
            # a dic for member info including the name, id and role
            member = {}
            # the retrived data model to compare with and store from
            members_model = []
            members_model = TeamMemberModel.find_by_team_id(id)
        
        for member_model in members_model:
            member['id'] = member_model.user_id
            # member['name'] = ''
            member['role'] = member_model.role
            members_list.append(member.copy())
            # user = UserModel.find_by_id(i.user_id)

        team_info['id'] = team.id
        team_info['name'] = team.name
        team_info['description'] = team.description
        team_info['created_at'] = team.created_at
        team_info['updated_at'] = team.updated_at
        team_info['project_'] = team.project 
        team_info['members'] = members_list
        team_info['users'] = list(map(lambda x: x.names(), UserModel.query.all()))

        # if team:
        return render_template('team-update.html', **team_info)   
        # return team_info 

#3. delete a team
@app.route('/Admin/Teams/delete/<int:id>/', methods=['GET'])
@login.login_required
def delete_team(id):
    if request.method == 'GET':
        team = TeamModel.find_by_id(id)
        if team:
            team.delete_from_db()
            return redirect(url_for('.show_teamslist'))
        return render_template('secret.html')

#4. show the list of teams
@app.route('/TeamsList/')
@login.login_required
def show_teamslist():
    return render_template("teams.html", **{'teams': list(map(lambda x: x.json(), TeamModel.query.all()))})    


#  ---------------- task section ----------------

#1. show the list of tasks
@app.route('/TasksList/')
@login.login_required
def show_taskslist():
    return render_template("tasks.html", **{'tasks': list(map(lambda x: x.json(), TaskModel.query.all()))})    


# Initialize flask-login
init_login()