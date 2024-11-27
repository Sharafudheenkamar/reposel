from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
# from user.api_permissions import CustomTokenAuthentication
# from rest_framework import TokenAuthentication
from .models import Token, Userprofile,Journals
# from project.utils import utc_today, validate_password
import json
from .serializers import *
from rest_framework import status



class UserLoginapi(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = tuple()

    def get(self, request):
        response_dict = {"status": "failed"}
        response_dict["logged_in"] = bool(request.user.is_authenticated)
        response_dict["status"] = "failed"
        return Response(response_dict, HTTP_200_OK)

    def post(self, request):
        response_dict = {"status": False, "token": None, "redirect": False}
        password = request.data.get("password")
        username = request.data.get("username")
        print(username)
        print(password)
        try:
            t_user = Userprofile.objects.get(username=username)
        except Userprofile.DoesNotExist:
            response_dict["reason"] = "No account found for this username. Please signup."
            return Response(response_dict, HTTP_200_OK)

        # blocked_msg = "This account has been blocked. Please contact admin."
        # today = utc_today()
        authenticated = authenticate(username=t_user.username, password=password)
        if not authenticated:
            response_dict["reason"] = "Invalid credentials."
            return Response(response_dict, HTTP_200_OK)

        user = t_user
        print(user)
        # if user.is_active:
        #     response_dict["reason"] = "Your login is inactive! Please contact admin"
        #     return Response(response_dict, HTTP_200_OK)

        session_dict = {"real_user": authenticated.id}
        token, _ = Token.objects.get_or_create(
            user=user, defaults={"session_dict": json.dumps(session_dict)}
        )
        login(request, user, "django.contrib.auth.backends.ModelBackend")
        response_dict["session_data"] = {
            "user_id": user.id,
            "user_type": user.user_type,
            "token": token.key,
            "username": user.username,
            "name": user.first_name,
            "status": user.status,
        }
        response_dict["token"] = token.key
        response_dict["status"] = "success"
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
        username = request.data.get("username")
        print(username)
        if Userprofile.objects.filter(username=username).exists():
            return Response(
                {"error": f"The username '{username}' is already taken. Please choose another."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = UserprofileSerializer(data=request.data)
        if serializer.is_valid():
            userprofile = serializer.save()
            userprofile.user_type = 'STUDENT'
            userprofile.status='ACTIVE'
            userprofile.is_active=True # # Set the user_type
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


