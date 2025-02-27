from pyexpat.errors import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from .form import TeacherForm
# from user.api_permissions import CustomTokenAuthentication
# from rest_framework import TokenAuthentication
from .models import *
# from project.utils import utc_today, validate_password
import json
from .serializers import *
from rest_framework import status
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('userid') is None:
            return redirect('login')  # Redirect to login page if not logged in
        return view_func(request, *args, **kwargs)
    return wrapper
class LoginPage(View):
    def get(self, request):
        return render(request, "administrator/login.html")
    def post(self,request):
        username=request.POST['username']
        password=request.POST['password']
        try:
            login_obj=Login.objects.get(username=username,password=password)
            request.session['userid']=login_obj.id
            print(request.session['login_obj'])
            if login_obj.usertype=="admin":
                return HttpResponse ('''<script>alert("welcome to adminhome");window.location="admindashboard"</script>''')
        except:
            return HttpResponse ('''<script>alert("invalid user");window.location="/"</script>''')

class LogoutView(View):
    def get(self, request):
        request.session.flush()  # Clears all session data
        return redirect('login') 
from django.shortcuts import render, redirect
from django.views import View
from .models import Teacher, Login
from django.http import JsonResponse

class AddTeacherView(View):
    def get(self, request):
        return render(request, 'administrator/add_teacher.html')

    def post(self, request):
        t_name = request.POST.get('t_name')
        email = request.POST.get('email')
        p_phno = request.POST.get('p_phno')
        qualification = request.POST.get('qualification')
        subject = request.POST.get('subject')
        experience = request.POST.get('experience')
        password = request.POST.get('password')

        if t_name and email:
            login_entry = Login.objects.create(username=email, password=password, usertype="mentor")
            teacher = Teacher.objects.create(
                t_name=t_name,
                email=email,
                p_phno=p_phno,
                qualification=qualification,
                subject=subject,
                experience=experience,
                t_LID=login_entry
            )
            return JsonResponse({'success': True, 'message': 'Teacher added successfully!'}, status=200)

        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)
def edit_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'edit_teacher.html', {'form': form, 'teacher': teacher})

def delete_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    if request.method == 'DELETE':  # If called via AJAX
        teacher.delete()
        return JsonResponse({'success': True})
    else:
        teacher.delete()
        return redirect('teacher_list')

class AdmindashboardPage(View):
    def get(self,request):
        st=Student.objects.all()
        pa=Parent.objects.all()
        te=Teacher.objects.all()
        return render(request,"administrator/admindashboard.html",{'st':st,'pa':pa,'te':te})
class ParentPage(View):
    def get(self,request):
        obj=Student.objects.all()
        return render(request,"administrator/parent.html",{'val':obj})
class StudentPage(View):
    def get(self,request):
        obj=Parent.objects.all()
        return render(request,"administrator/student.html",{'val':obj})
class TeachersPage(View):
    def get(self,request):
        obj=Teacher.objects.all()
        return render(request,"administrator/teachers.html",{'val':obj})
    

class LoginPageApi(APIView):
    def post(self, request):
        response_dict= {}
        password = request.data.get("password")
        print("Password ------------------> ",password)
        username = request.data.get("username")
        print("Username ------------------> ",username)
        try:
            user = Login.objects.filter(username=username, password=password).first()
            print("user_obj :-----------", user)
        except Login.DoesNotExist:
            response_dict["message"] = "No account found for this username. Please signup."
            return Response(response_dict, HTTP_200_OK)
      
        if user.usertype:
            response_dict = {
                "login_id": str(user.id),
                "user_type": user.usertype,
                "message": "success",
            }   
            print("User details :--------------> ",response_dict)
            return Response(response_dict, HTTP_200_OK)
        else:
            response_dict["message"] = "Your account has not been approved yet or you are a CLIENT user."
            return Response(response_dict, HTTP_200_OK)

class Logout(APIView):
    def get(self,request):
        request.session["token"]=None
        request.session.flush()
        return Response("loggedout sucessfully",HTTP_200_OK)
    

class UserprofileListCreateAPIView(APIView):
    """
    API view for listing and creating Userprofile instances.
    """
    def get(self, request):
        userprofiles = Userprofile.objects.all()
        serializer = UserprofileSerializer(userprofiles, many=True)
        return Response(serializer.data)

    def post(self, request):
        print("ddd",request.data)
                # Check if username already exists
        username = request.data.get("name")
        print(username)
        if Login.objects.filter(username=username).exists():
            return Response(
                {"error": f"The username '{username}' is already taken. Please choose another."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = Loginserializer(data=request.data)
        if serializer.is_valid():
            userprofile = serializer.save()
            userprofile.user_type = 'STUDENT'
            # userprofile.status='ACTIVE'
            # userprofile.is_active=True # # Set the user_type
            userprofile.save() 
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class JournalsAPIView(APIView):
    permission_classes=[AllowAny]
    def get(self, request, pk=None):
        """
        Retrieve a single journal or a list of all journals.
        """
        if pk:
            try:
                journal = Journals.objects.filter(user__id=pk).all()
                serializer = JournalsSerializerview(journal,many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Journals.DoesNotExist:
                return Response({"error": "Journal not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            journals = Journals.objects.all()
            serializer = JournalsSerializerview(journals, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    @csrf_exempt 
    def post(self, request):
        """
        Create a new journal entry.
        """
        serializer = JournalsSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Update an existing journal entry.
        """
        try:
            journal = Journals.objects.get(pk=pk)
        except Journals.DoesNotExist:
            return Response({"error": "Journal not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = JournalsSerializer(journal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a journal entry.
        """
        try:
            journal = Journals.objects.get(pk=pk)
            journal.delete()
            return Response({"message": "Journal deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Journals.DoesNotExist:
            return Response({"error": "Journal not found"}, status=status.HTTP_404_NOT_FOUND)
        
class LatestImagesView(APIView):
    def get(self, request):
        # Fetch the latest 5 Journals with non-null images
        latest_journals = Journals.objects.filter(image__isnull=False,viewOption='Public').order_by('created_at')[:5]
        print(latest_journals)
        serializer = JournalsSerializerview(latest_journals, many=True)
        return Response(serializer.data)
    
# API Views
class ClassroomAPIView(APIView):
    def get(self, request):
        classrooms = Classroom.objects.all()
        serializer = ClassroomSerializer(classrooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClassroomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClassroomDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Classroom.objects.get(pk=pk)
        except Classroom.DoesNotExist:
            return None

    def get(self, request, pk):
        classroom = self.get_object(pk)
        if not classroom:
            return Response({'error': 'Classroom not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClassroomSerializer(classroom)
        return Response(serializer.data)

    def put(self, request, pk):
        classroom = self.get_object(pk)
        if not classroom:
            return Response({'error': 'Classroom not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClassroomSerializer(classroom, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        classroom = self.get_object(pk)
        if not classroom:
            return Response({'error': 'Classroom not found'}, status=status.HTTP_404_NOT_FOUND)
        classroom.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TaskAPIView(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Task.objects.get(classroom=pk)
        except Task.DoesNotExist:
            return None

    def get(self, request, pk):
        task = self.get_object(pk)
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        task = self.get_object(pk)
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = self.get_object(pk)
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


import google.generativeai as genai

# Configure the Gemini API
genai.configure(api_key='AIzaSyAKu81pUUT2WbxPnjQntvHHxiFwlhCCU-A')


class chatbotapi(APIView):
    def post(self, request):
        # Get query from the user input
        user_query = request.data.get('query', '')

        # Default response if no input
        response_data = {
            'chatbot_response': "",
            "chat_history": [],   # This will store the chatbot-like response
        }


        # Construct the prompt using the filtered data (ensure it's only from the models)
        print(user_query)
        prompt = (
            f"User Query: {user_query}. "
            f"Provide the response based on above data"
        )

        try:
            # Call Gemini API to generate the response
            gemini_response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
            gemini_chatbot_response = gemini_response.text.strip()
            print(user_query)
            ChatHistory.objects.create(
                user_query=user_query,
                chatbot_response=gemini_chatbot_response,
            )

            # Update response data with the chatbot response
            response_data['chatbot_response'] = gemini_chatbot_response
                        # Retrieve the chat history
            chat_history = ChatHistory.objects.order_by("-timestamp").values(
                "user_query", "chatbot_response", "timestamp"
            )
            response_data.update(
                {

                    "chatbot_response": gemini_chatbot_response,
                    "chat_history": list(chat_history),
                }
            )

            

            

            # Return the chatbot-like response with the itinerary data
            return Response(response_data, status=200)
        
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Classroom
from .serializers import ClassroomSerializer

class ClassroomAPI(APIView):
    # GET method to retrieve all classrooms
    def get(self, request):
        classrooms = Classroom.objects.all()
        serializer = ClassroomSerializer(classrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST method to create a new classroom
    def post(self, request):
        serializer = ClassroomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT method to update an existing classroom
    def put(self, request, pk):
        try:
            classroom = Classroom.objects.get(pk=pk)
        except Classroom.DoesNotExist:
            return Response({"error": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClassroomSerializer(classroom, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # Construct the prompt using the filtered data (ensure it's only from the models)
        print(user_query)
        prompt = (
            f"User Query: {user_query}. "
            f"Provide the response based on above data"
        )

        try:
            # Call Gemini API to generate the response
            gemini_response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
            gemini_chatbot_response = gemini_response.text.strip()
            print(user_query)
            ChatHistory.objects.create(
                user_query=user_query,
                chatbot_response=gemini_chatbot_response,
            )

            # Update response data with the chatbot response
            response_data['chatbot_response'] = gemini_chatbot_response
                        # Retrieve the chat history
            chat_history = ChatHistory.objects.order_by("-timestamp").values(
                "user_query", "chatbot_response", "timestamp"
            )
            response_data.update(
                {

                    "chatbot_response": gemini_chatbot_response,
                    "chat_history": list(chat_history),
                }
            )

            



            # Return the chatbot-like response with the itinerary data
            return Response(response_data, status=200)
        
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        

class Viewprofileapi(APIView):
    def get(self, request,id):
        try:
            user = Login.objects.get(id=id)
            if user.usertype=='student':
                student = Student.objects.get(st_LID=user)
                response_data = {
                    "username": student.st_LID.username,
                    "password": student.st_LID.password,
                    "type": student.st_LID.usertype,
                    "address": user.address,
                    "st_name": student.st_name ,
                    "classs": student.classs,
                    "stream": student.stream,
                    "email": student.email,
                    "st_phno": student.st_phno,
                    "st_LID": student.st_LID,
                    "selscore": student.selscore}
                return Response(response_data, status=status.HTTP_200_OK)
            elif user.usertype=='parent':
                student = Parent.objects.get(p_LID=user)
                response_data = {
                    "username": student.p_LID.username,
                    "password": student.p_LID.password,
                    "type": student.p_LID.usertype,

                    "p_name": student.p_name ,

                    "email": student.email,
                    "p_phno": student.p_phno,
                    "student_id": student.student_id,
                    }
                return Response(response_data, status=status.HTTP_200_OK)
            elif user.usertype=='mentor':
                student = Teacher.objects.get(t_LID=user)
                response_data = {
                    "username": student.t_LID.username,
                    "password": student.t_LID.password,
                    "type": student.t_LID.usertype,

                    "t_name": student.t_name ,

                    "email": student.email,
                    "p_phno": student.p_phno,
                    "qualification": student.qualification,
                    "subject": student.subject,
                    "experience": student.experience,
                    }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                return Response({"error": "User is not registered"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                

    def put(self, request, id):
        try:
            user = get_object_or_404(Login, id=id)
            data = request.data  # Get the data from request

            if user.usertype == 'student':
                student = get_object_or_404(Student, st_LID=user)
                student.st_name = data.get("st_name", student.st_name)
                student.classs = data.get("classs", student.classs)
                student.stream = data.get("stream", student.stream)
                student.email = data.get("email", student.email)
                student.st_phno = data.get("st_phno", student.st_phno)
                student.selscore = data.get("selscore", student.selscore)
                user.address = data.get("address", user.address)
                student.save()
                user.save()
            elif user.usertype == 'parent':
                parent = get_object_or_404(Parent, p_LID=user)
                parent.p_name = data.get("p_name", parent.p_name)
                parent.email = data.get("email", parent.email)
                parent.p_phno = data.get("p_phno", parent.p_phno)
                parent.student_id = data.get("student_id", parent.student_id)
                parent.save()
            elif user.usertype == 'mentor':
                teacher = get_object_or_404(Teacher, t_LID=user)
                teacher.t_name = data.get("t_name", teacher.t_name)
                teacher.email = data.get("email", teacher.email)
                teacher.p_phno = data.get("p_phno", teacher.p_phno)
                teacher.qualification = data.get("qualification", teacher.qualification)
                teacher.subject = data.get("subject", teacher.subject)
                teacher.experience = data.get("experience", teacher.experience)
                teacher.save()
            else:
                return Response({"error": "User type not recognized"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ParentPageAPI(APIView):
    def get(self, request):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentPageAPI(APIView):
    def get(self, request):
        parents = Parent.objects.all()
        serializer = ParentSerializer(parents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Classroom, Student
from .serializers import ClassroomSerializer

class StudentClassroomsView(APIView):
    """API to retrieve all classrooms a student is enrolled in"""

    def get(self, request, student_id):
        """Retrieve classrooms for a given student"""
        student = get_object_or_404(Student, id=student_id)  # Ensure student exists
        classrooms = Classroom.objects.filter(students=student)  # Filter classrooms where student is enrolled

        serializer = ClassroomSerializer(classrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddStudentsToClassroomAPIView(APIView):
    """
    API View to add multiple students to a classroom.
    """
    def post(self, request, classroom_id):
        classroom = get_object_or_404(Classroom, id=classroom_id)
        student_ids = request.data.get('student_ids', [])

        if not isinstance(student_ids, list):
            return Response({"error": "student_ids should be a list of student IDs."}, status=status.HTTP_400_BAD_REQUEST)

        students = Student.objects.filter(id__in=student_ids)
        
        if not students.exists():
            return Response({"error": "No valid students found with the provided IDs."}, status=status.HTTP_400_BAD_REQUEST)

        classroom.students.add(*students)  # Add multiple students to the classroom
        classroom.save()

        serializer = ClassroomSerializer(classroom)
        return Response(serializer.data, status=status.HTTP_200_OK)
# API View to get classrooms of a student
class StudentClassroomsView(APIView):
    def get(self, request, student_id):
        # Fetch the student object
        student = get_object_or_404(Student, st_LID__id=student_id)

        # Get all classrooms where this student is enrolled
        classrooms = Classroom.objects.filter(students=student)

        # Serialize the classrooms data
        serializer = ClassroomSerializer(classrooms, many=True)

        # Return response
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# API View to get tasks of a classroom
class ClassroomTasksView(APIView):
    def get(self, request, classroom_id):
        # Fetch the classroom object
        classroom = get_object_or_404(Classroom, id=classroom_id)

        # Get all tasks assigned to this classroom
        tasks = Task.objects.filter(classroom=classroom)

        # Serialize the tasks data
        serializer = TaskSerializer(tasks, many=True)

        # Return response
        return Response(serializer.data, status=status.HTTP_200_OK)
class ClassroomteacherTasksView(APIView):
    def get(self, request, classroom_id,teacher_id):
        # Fetch the classroom object
        classroom = get_object_or_404(Classroom, id=classroom_id)

        # Get all tasks assigned to this classroom
        tasks = Task.objects.filter(classroom=classroom,teacherid__t_LID__id=teacher_id)

        # Serialize the tasks data
        serializer = TaskSerializer(tasks, many=True)

        # Return response
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeacherTasksView(APIView):
    def get(self, request, teacher_id):
        # Fetch the teacher object
        teacher = get_object_or_404(Teacher, t_LID__id=teacher_id)

        # Get all tasks created by this teacher
        tasks = Task.objects.filter(teacherid=teacher)

        # Serialize the tasks data
        serializer = TaskSerializer(tasks, many=True)

        # Return response
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompletedTaskListView(APIView):
    def get(self, request, task_id):
        # Fetch all completed tasks for a given task_id
        completed_tasks = Studenttaskcompleted.objects.filter(taskid=task_id)

        # Serialize the completed task data
        serializer = StudentTaskCompletedSerializer(completed_tasks, many=True)

        # Return response
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request, task_id):
        """Allow students to submit a completed task"""
        # Ensure task exists
        task = get_object_or_404(Task, id=task_id)
        
        # Extract student ID from request data
        student_id = request.data.get('studentid')
        student = get_object_or_404(Student, id=student_id)

        # Create a new completed task entry
        data = request.data.copy()
        data['taskid'] = task_id  # Assign the task ID from the URL
        data['studentid'] = student_id  # Assign the student ID from the request

        serializer = StudentTaskCompletedSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, task_id):
        """Allow students to update their completed task submission"""
        student_id = request.data.get('studentid')

        # Ensure task and student exist
        task = get_object_or_404(Task, id=task_id)
        student = get_object_or_404(Student, id=student_id)

        # Fetch the existing completed task entry
        completed_task = get_object_or_404(Studenttaskcompleted, taskid=task, studentid=student)

        # Update the completed task with new data
        serializer = StudentTaskCompletedSerializer(completed_task, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        

class AddStudentsToParentView(APIView):
        def get(self, request, parent_id):
            """Retrieve students linked to a parent"""
            parent = get_object_or_404(Parent, id=parent_id)
            students = parent.student_id.all()  # Fetch related students
            student_data = [{"id": student.id, "name": student.name} for student in students]  # Assuming Student has a 'name' field
            return Response({"parent_id": parent.id, "students": student_data}, status=status.HTTP_200_OK)

        def post(self, request, parent_id):
            """Add students to a parent"""
            parent = get_object_or_404(Parent, id=parent_id)
            
            # Get list of student IDs from request data
            student_ids = request.data.get('student_ids', [])

            if not student_ids:
                return Response({"error": "No student IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch student objects and add them to the parent
            students = Student.objects.filter(id__in=student_ids)

            if not students.exists():
                return Response({"error": "No valid students found"}, status=status.HTTP_400_BAD_REQUEST)

            parent.student_id.add(*students)
            parent.save()

            serializer = ParentSerializer(parent)
            return Response(serializer.data, status=status.HTTP_200_OK)

        def put(self, request, parent_id):
            """Update the list of students for a parent (Replace existing students)"""
            parent = get_object_or_404(Parent, id=parent_id)

            # Get new student IDs from request
            student_ids = request.data.get('student_ids', [])

            if not student_ids:
                return Response({"error": "No student IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch student objects
            students = Student.objects.filter(id__in=student_ids)

            if not students.exists():
                return Response({"error": "No valid students found"}, status=status.HTTP_400_BAD_REQUEST)

            # Clear existing students and add new ones
            parent.student_id.set(students)  # `.set()` replaces existing relationships
            parent.save()

            serializer = ParentSerializer(parent)
            return Response(serializer.data, status=status.HTTP_200_OK)
        

class ParentStudentsView(APIView):
    """API to retrieve all students associated with a parent"""

    def get(self, request, parent_id):
        """Retrieve students for a given parent"""
        parent = get_object_or_404(Parent, id=parent_id)  # Ensure parent exists
        students = parent.student_id.all()  # Fetch students related to this parent

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ChatAPIView(APIView):

    def get(self, request,sender_id,receiver_id):
        user = request.user
        
        if not receiver_id:
            return Response({"error": "receiver_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = Login.objects.get(id=receiver_id)
        except Login.DoesNotExist:
            return Response({"error": "Receiver does not exist"}, status=status.HTTP_404_NOT_FOUND)

        chats = Chat.objects.filter(
            (models.Q(sender=sender_id) & models.Q(receiver=receiver_id)) |
            (models.Q(sender=receiver_id) & models.Q(receiver=sender_id))
        ).order_by('timestamp')

        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)

    def post(self, request,sender_id,receiver_id):
        """
        Send a chat message from the logged-in user to a specific receiver.
        """
        user = sender_id
        receiver_id=receiver_id
        data = request.data
        data['sender'] = user 
        data['receiver']= receiver_id# Set the sender to the logged-in user

        serializer = ChatSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ChattedUsersAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request,userid):
        """
        Get a list of users the logged-in user has chatted with.
        """
        user = userid  # Logged-in user
        print(user)
        
        # Fetch all users the logged-in user has sent or received messages with
        sent_chats = Chat.objects.filter(sender=user).values_list('receiver', flat=True)
        received_chats = Chat.objects.filter(receiver=user).values_list('sender', flat=True)
        
        # Combine and get unique user IDs
        chatted_user_ids = set(sent_chats) | set(received_chats)
        
        # Fetch user details for these IDs
        chatted_users = Login.objects.filter(id__in=chatted_user_ids)
        
        # Serialize the user details
        serializer = ChattedUsersSerializer1(chatted_users, many=True)
        print(serializer.data)
        
        return Response(serializer.data)
    

class ParentListView(APIView):
    """API to get all parents"""

    def get(self, request):
        parents = Parent.objects.all()
        serializer = ParentSerializer(parents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class StudentMentorListView(APIView):
    """API to get mentors for each student"""

    def get(self, request,st_id):
        students = Student.objects.filter(id=st_id).all()
        serializer = StudentMentorSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)