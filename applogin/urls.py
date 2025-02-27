
from django.urls import path
from .views import *

urlpatterns = [
    path('', LoginPage.as_view(), name="login"),
    path('admindashboard',AdmindashboardPage.as_view(),name="admindashboard"),
    path('editteacher/<int:id>/', edit_teacher, name='edit_teacher'),
    path('deleteteacher/<int:id>/', delete_teacher, name='delete_teacher'),

   
    path('parent',ParentPage.as_view(),name="parent"),
    path('student',StudentPage.as_view(),name="student"),
    path('teachers',TeachersPage.as_view(),name="teachers"),
    path('addteacher/', AddTeacherView.as_view(), name='add_teacher'),
    path('loginapi', LoginPageApi.as_view(), name='loginapi'),
    path('logout/', Logout.as_view(), name='lgout'),
    path('register', UserprofileListCreateAPIView.as_view(), name='userprofile-list-create'),
    path('journals/', JournalsAPIView.as_view(), name='journals-list'),
    path('journals/<int:pk>/', JournalsAPIView.as_view(), name='journal-detail'),
    path('latest-images/', LatestImagesView.as_view(), name='latest-images'),
    path('classrooms/', ClassroomAPIView.as_view(), name='classroom-list'),
    path('classrooms/<int:pk>/', ClassroomDetailAPIView.as_view(), name='classroom-detail'),
    path('tasks/', TaskAPIView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', TaskDetailAPIView.as_view(), name='task-detail'),

    path('viewprofileapi/<int:id>',Viewprofileapi.as_view(),name='Viewprofile'),

    

    path('chatbotapi',chatbotapi.as_view(),name='chatbotapi'),
    path('ParentPageAPI',ParentPageAPI.as_view(),name='ParentPageAPI'),
    path('StudentPageAPI',StudentPageAPI.as_view(),name='StudentPageAPI'),

    
    # view classrooms student is member
    path('students/<int:student_id>/classrooms/', StudentClassroomsView.as_view(), name='student-classrooms'),

    #add students to each classroom
    path('classrooms/<int:classroom_id>/add-students/', AddStudentsToClassroomAPIView.as_view(), name='add-students'),
#     {
#     "student_ids": [1, 2, 3, 4]
# } 
    # view students in each classroom
    path('studentclassrooms/<student_id>',StudentClassroomsView.as_view(),name='StudentClassroomsView'),
    #view tasks added to each classroom
    path('classrooms/<classroom_id>/tasks/',ClassroomTasksView.as_view(),name='ClassroomTasksView'),
    #view tasks added to each classroom by teachers
    path('classrooms/<classroom_id>/<teacher_id>/tasks/',ClassroomteacherTasksView.as_view(),name='ClassroomTasksView'),
    #view tasks added by teachers 
    path('teachers/<int:teacher_id>/tasks/', TeacherTasksView.as_view(), name='teacher-tasks'),
    #view tasks added by students based on task id,submit tasks based on taskid,add marks for each task
    path('tasks/<int:task_id>/completed/', CompletedTaskListView.as_view(), name='completed-tasks'),

    #add students to parents
    path('parents/<int:parent_id>/add-students/', AddStudentsToParentView.as_view(), name='add-students-to-parent'),
    #{
#     "student_ids": [2, 3, 5]
# }
    #view students in each parent
    path('parents/<int:parent_id>/students/', ParentStudentsView.as_view(), name='parent-students'),
    
    path('chat/<int:sender_id>/<int:receiver_id>', ChatAPIView.as_view(), name='chat-api'),
    path('chatted-users/<int:userid>', ChattedUsersAPIView.as_view(), name='chatted-users'),
    path('viewallparents/', ParentListView.as_view(), name='parent-list'),

    path('students/mentors/<int:st_id>', StudentMentorListView.as_view(), name='student-mentors'),


]
