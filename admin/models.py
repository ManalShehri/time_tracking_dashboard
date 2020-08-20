from admin import db
from sqlalchemy_utils import  EmailType, UUIDType, TimezoneType
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import uuid

AVAILABLE_USER_TYPES = [
    (u'admin', u'Admin'),
    (u'regular-user', u'Regular user'),
]


TaskTagModel = db.Table('TaskTag', db.Model.metadata,
                           db.Column('task_id', db.Integer, db.ForeignKey('Task.id')),
                           db.Column('tag_id', db.Integer, db.ForeignKey('Tag.id'))
                           )


class UserModel(db.Model):
    __tablename__ = 'User'
    id = db.Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(EmailType, unique=True, nullable=False)
    bio = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    updated_at = db.Column(db.DateTime, onupdate = datetime.datetime.now)
    timezone = db.Column(TimezoneType(backend='pytz'))
    dialling_code = db.Column(db.Integer())
    local_phone_number = db.Column(db.String(10))
    _password = db.Column(db.String(255))

    team = db.relationship("TeamMemberModel", back_populates="member", cascade="all, delete-orphan")
    task = db.relationship("TaskModel", back_populates="user", cascade="all, delete-orphan")
    tag = db.relationship("TagModel", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, id, name, email, _password, bio, timezone, dialling_code, local_phone_number):
        self.id = id
        self.name = name
        self.email = email
        self._password = _password
        self.bio = bio
        self.timezone = timezone
        self.dialling_code = dialling_code
        self.local_phone_number = local_phone_number

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}".format(self.__str__())

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def set_password(self, pass_):
        self._password = generate_password_hash(pass_)
    
    def check_password(self, pass_):
        return check_password_hash(self._password, pass_)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'bio': self.bio,
            'created_at': str(self.created_at.strftime("%Y-%m-%d %H:%M:%S")),
            'updated_at': str(self.updated_at),
            'timezone': str(self.timezone),
            'dialling_code': self.dialling_code,
            'local_phone_number': self.local_phone_number,
            '_password': self._password
            }

    def names(self):
        return {
            'id': self.id,
            'name': self.name
            }
            
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        
    @classmethod
    def phone_number(self):
        if self.dialling_code and self.local_phone_number:
            number = str(self.local_phone_number)
            return "+{} ({}) {} {} {}".format(self.dialling_code, number[0], number[1:3], number[3:6], number[6::])


class TeamMemberModel(db.Model):
    __tablename__ = 'TeamMember'
    user_id = db.Column(UUIDType(binary=False), db.ForeignKey(UserModel.id), primary_key=True)
    role = db.Column(db.String(100)) #user type (admin or regular user)
    team_id = db.Column(db.Integer, db.ForeignKey('Team.id'), primary_key=True) 
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    team = db.relationship("TeamModel", back_populates="member")
    member = db.relationship("UserModel", back_populates="team")  

    def __str__(self):
        return "{}".format(self.member)

    def __repr__(self):
        return "{}".format(self.__str__())

    @classmethod
    def find_by_team_id(cls, team_id):
        return cls.query.filter_by(team_id=team_id).all() 

    @classmethod
    def find_by_member(cls, member):
        return cls.query.filter_by(member=member).all() 

    @classmethod
    def find_by_team(cls, team):
        return cls.query.filter_by(team=team).all() 


class TeamModel(db.Model):
    __tablename__ = 'Team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, onupdate = datetime.datetime.now)
    member = db.relationship("TeamMemberModel", back_populates="team", cascade="all, delete-orphan")
    project = db.relationship("ProjectModel", back_populates="team",cascade="all, delete-orphan")

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}".format(self.__str__())
        
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': str(self.created_at.strftime("%Y-%m-%d %H:%M:%S")),
            'updated_at': str(self.updated_at),
            'member': self.member,
            'project': self.project
            }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_project(cls, project):
        return cls.query.filter(project=project).all() 
 
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class TaskModel(db.Model):
    __tablename__ = 'Task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(255))
    start_at = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime)
    user_id = db.Column(UUIDType(binary=False), db.ForeignKey(UserModel.id))
    user = db.relationship("UserModel", back_populates="task")
    tag = db.relationship('TagModel', secondary=TaskTagModel, back_populates="task")

    project_id = db.Column(db.Integer, db.ForeignKey('Project.id'))
    project = db.relationship("ProjectModel", back_populates="task")
    attachment = db.relationship("AttachmentModel", back_populates="task")


    def __str__(self):
        return "{}".format(self.title)
 
    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_date': str(self.start_at.date()),
            'start_time': str(self.start_at.strftime("%I:%M %P")).upper(),
            'end_time': str(self.end_at.strftime("%I:%M %P")).upper() if self.end_at else 'still running',
            'user': self.user,
            'project': self.project,
            'attachment': self.attachment,
            'tag': self.tag
            }


class TagModel(db.Model):
    __tablename__ = 'Tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True)
    user_id = db.Column(UUIDType(binary=False), db.ForeignKey(UserModel.id))
    user = db.relationship("UserModel", back_populates="tag")
    task = db.relationship("TaskModel",secondary=TaskTagModel, back_populates="tag")
    project_id = db.Column(db.Integer, db.ForeignKey('Project.id'))
    project = db.relationship("ProjectModel", back_populates="tag")

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}".format(self.__str__())

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'task': self.task,
            'user': self.user,
            'project': self.project
            }
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class ProjectModel(db.Model):
    __tablename__ = 'Project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    updated_at = db.Column(db.DateTime, onupdate = datetime.datetime.now)
    status = db.Column(db.String(15))
    team_id = db.Column(db.Integer, db.ForeignKey('Team.id'))
    team = db.relationship("TeamModel", back_populates="project")
    task = db.relationship("TaskModel", back_populates="project")
    tag = db.relationship("TagModel", back_populates="project")

    def __init__(self, id, title, description, status):
        self.id = id
        self.title = title
        self.description = description
        self.status = status

    def __str__(self):
        return "{}".format(self.title)

    def __repr__(self):
        return "{}".format(self.__str__())

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': str(self.created_at.strftime("%Y-%m-%d %H:%M:%S")),
            'updated_at': str(self.updated_at)
            }
    def names(self):
        return {
            'id': self.id,
            'title': self.title
            }
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class AttachmentModel(db.Model):
    __tablename__ = 'Attachment'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    task_id = db.Column(db.Integer, db.ForeignKey('Task.id'))
    task = db.relationship("TaskModel", back_populates="attachment")

    def __str__(self):
        return "{}".format(self.title)

    def __repr__(self):
        return "{}".format(self.__str__())


class AdminModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(64))

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __unicode__(self):
        return self.username

    @classmethod
    def find_by_login(cls, login):
        return cls.query.filter_by(login=login).first()
    
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def set_password(self, pass_):
        self.password = generate_password_hash(pass_)
    
    def check_password(self, pass_):
        return check_password_hash(self.password, pass_)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
