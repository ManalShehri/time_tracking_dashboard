from admin import db
from admin.models import *
import random
import datetime

###### this file is for creating RANDOM data in tables ######

def build_sample_db():
    import random
    db.drop_all()
    db.create_all()
    password_ = 'test'
    first_names = ['test','Randa', 'Nouf']
    first_names_ar = ['test','رندا', 'نوف']
    last_names = ['T','.', '.']

    # adding admin
    for i in range(len(first_names)):
        user = AdminModel()
        user.first_name = first_names_ar[i]
        user.last_name = last_names[i]
        user.login = first_names[i].lower()
        user.email = user.login + "@tera-cit.net"
        user.set_password(password_)
        db.session.add(user)
        db.session.commit()

    
    # adding users
    names = [
        'Manal', 'Esraa', 'Haneen', 'Sara', 'Ahlam', 'Mawadah', 'Randa', 'Salha', 'Maryam', 'Aisha',
        'Ayman', 'Khalid', 'Mohammed', 'Abdullah', 'Abdulrahman', 'Saad', 'Ali', 'Omar', 'Faisal', 'Fahad'
    ]

    names_ar = [
        'منال', 'إسراء', 'حنين', 'سارة', 'أحلام', 'مودة', 'رندا', 'صالحة', 'مريم', 'عائشة',
         'أيمن', 'خالد', 'محمد', 'عبدالله', 'عبدالرحمن', 'سعد', 'علي', 'عمر', 'فيصل', 'فهد'
    ]

    user_list = []
    password_ = '123'
    timezones = ['Asia/Riyadh','Africa/Cairo']
    for i in range(len(names)):
        chosen_time = random.choice(timezones)
        if chosen_time == 'Asia/Riyadh':
            chosen_dialling_code = 966
        else: 
            chosen_dialling_code = 20
        user = UserModel(
            id = None,
            name = names_ar[i],
            email = names[i].lower() + "@tera-cit.net",
            timezone = chosen_time,
            dialling_code = chosen_dialling_code,
            local_phone_number = '5' + ''.join(random.choices('123456789', k=8)),
            _password = password_,
            bio = 'هذا النص هو مثال لنص يمكن أن يستبدل في نفس المساحة، لقد تم توليد هذا النص من مولد النص العربى، حيث يمكنك أن تولد مثل هذا النص أو العديد من النصوص الأخرى إضافة إلى زيادة عدد الحروف التى يولدها التطبيق'
        )

        user_list.append(user)
        db.session.add(user)
        db.session.commit()


    # adding teams 
    teams_names = ['t3-team','rx-box-team','dalala-team','tera-cit-team','asdaa-team']
    new_teams = []
    for team in teams_names:
        new_team = TeamModel(id = None, name = team, description = 'هذا النص هو مثال لنص يمكن أن يستبدل في نفس المساحة، لقد تم توليد هذا النص من مولد النص العربى، حيث يمكنك أن تولد مثل هذا النص أو العديد من النصوص الأخرى إضافة إلى زيادة عدد الحروف التى يولدها التطبيق'
        )
        db.session.add(new_team)
        db.session.commit()

        new_teams.append(new_team)
        

    number_of_members_in_team = [2,3,4,5]
    roles = ['قائد','عضو']
    # adding random members to the teams
    users_in_team_dic = {}
    for team in new_teams:
        users_in_team =  []
        # choose a  random user 
        random_users = random.sample(user_list, random.choice(number_of_members_in_team ))

        for random_user in random_users:
            members =  TeamMemberModel(
                role = random.choice(roles),
                team = team,
                team_id = team.id
            )
            members.user_id = random_user.id
            db.session.add(members)
            db.session.commit()

        users_in_team_dic[team.name] = random_users
 
    projects_names = ['t3-project','rx-box-project','dalala-project','tera-cit-project','asdaa-project']
    new_projects = []
    status = ['نشط','معلق','مؤرشف']
    for i in range(len(projects_names)) :
        new_project = ProjectModel(
            id = None,
            title = projects_names[i],
            description = 'هذا النص هو مثال لنص يمكن أن يستبدل في نفس المساحة، لقد تم توليد هذا النص من مولد النص العربى، حيث يمكنك أن تولد مثل هذا النص أو العديد من النصوص الأخرى إضافة إلى زيادة عدد الحروف التى يولدها التطبيق',
            status = random.choice(status)
        )
        new_project.team = new_teams[i]
        new_project.team_id = new_teams[i].id
        new_projects.append(new_project)

    # adding tags
    tag_list = []
    project_tag_list = []
    for tmp in ["تعديلات", "يوجد اخطاء", "للمستقبل", "تم", "مؤجل", "مؤرشف"]:
        project = random.choice(new_projects)
        tag = TagModel(name = tmp, project = project )
        user = random.choice(user_list)
        tag.user = user
        tag_list.append(tag)
        db.session.add(tag)
        db.session.commit()


    x = datetime.datetime.now()
    sample_text = [
        {
            'title': "تصحيح الأخطاء",
            'description': "وصف المهمة يكتب هنا في هذه الخانة",
            'start': datetime.datetime(2020, 6, 1, hour=10,minute=16),
            'end': datetime.datetime(2020, 6, 1, hour=11,minute=31)
        },
        {
            'title': "تصميم الواجهات",
            'description': "وصف المهمة يكتب هنا في هذه الخانة",
            'start': datetime.datetime(2020, 6, 1, hour=8,minute=8),
            'end': datetime.datetime(2020, 6, 1, hour=9,minute=28)
        },
        {
            'title': "تكويد الواجهات",
            'description': "وصف المهمة يكتب هنا في هذه الخانة",
            'start': datetime.datetime(2020, 6, 1, hour=12,minute=45),
            'end': datetime.datetime(2020, 6, 1, hour=15,minute=00)
        },
        {
            'title': "وضع أساسيات المشروع",
            'description': "وصف المهمة يكتب هنا في هذه الخانة",
            'start': datetime.datetime(2020, 6, 1, hour=14,minute=2),
            'end': datetime.datetime(2020, 6, 1, hour=15,minute=35)
        },
        {
            'title': "تكويد الخلفية",
            'description': "وصف المهمة يكتب هنا في هذه الخانة",
            'start': datetime.datetime(2020, 6, 1, hour=7,minute=55),
            'end': datetime.datetime(2020, 6, 1, hour=13,minute=0)
        },
        {
            'title': "اختبار الموقع",
            'description': "وصف المهمة يكتب هنا في هذه الخانة",
            'start': datetime.datetime(2020, 6, 1, hour=9,minute=42),
            'end': datetime.datetime(2020, 6, 1, hour=14,minute=15)
        },
        {
            'title': "تصميم واجهة الجوال",
            'description': "وصف المهمة يكتب هنا في هذه الخانة",
            'start': datetime.datetime(2020, 6, 1, hour=10,minute=24),
            'end': datetime.datetime(2020, 6, 1, hour=12,minute=51)
        },
        {
            'title': "2 تصحيح الأخطاء",
            'description': "وصف المهمة يكتب هنا في هذه الخانة",
            'start': datetime.datetime(x.year, x.month , x.day, hour=10,minute=16),
            'end': None 
        },
        {
            'title': "تصميم الواجهات 2",
            'description': "وصف المهمة يكتب هنا في هذه الخانة",
            'start': datetime.datetime(x.year, x.month , x.day, hour=8,minute=8),
            'end': None
        },
        {
            'title': "2 تكويد الواجهات",
            'description': "وصف المهمة يكتب هنا في هذه الخانة",
            'start': datetime.datetime(x.year, x.month , x.day, hour=12,minute=45),
            'end': None
        },
        {
            'title': "2 وضع أساسيات المشروع",
            'description': "وصف المهمة يكتب هنا في هذه الخانة",
            'start': datetime.datetime(x.year, x.month , x.day, hour=14,minute=2),
            'end': None
        }
    ]

    # adding tasks
    task_list = []
    for i in range(len(sample_text)):
        test_team = random.choice(list(users_in_team_dic.values()))
        user_ = random.choice(user_list)
        entry = random.choice(sample_text)  # select text at random
        task = TaskModel(
            id = None,
            user = user_,
            title = entry['title'],
            description = entry['description'],
            start_at = entry['start'],
            end_at = entry['end'],
            tag = random.sample(tag_list, 2),
            project = random.choice(new_projects)
        )
        task_list.append(task)
        db.session.add(task)
        db.session.commit()


    # adding attachment
    ext = ['.jpg','.pdf','.png','.xls']
    for i in range(len(task_list)):
        attatchment = AttachmentModel(
            title = task_list[i].title + random.choice(ext),
            task = task_list[i]
        )
        db.session.add(attatchment)

    return

