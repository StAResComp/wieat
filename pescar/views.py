# from django.shortcuts import render
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
import sys

def index(request):
    return HttpResponse("Hello world")

class ApiEndpoint(ProtectedResourceView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            username = request.user.username
            cursor = connections['data'].cursor()
            cursor.execute("SELECT * FROM users WHERE username LIKE '{}'".format(username))
            users = cursor.fetchall()
            user_id = None
            if len(users) == 0:
                cursor.execute("INSERT INTO users (username) VALUES ('{}')".format(username))
                user_id = cursor.lastrowid
            else:
                user_id = users[0][0]
            sys.stderr.write('User ID: {}'.format(user_id))
            sys.stderr.write('Data: \n {}'.format(request.body))
            cursor.execute("INSERT INTO trips (user_id, data) VALUES ('{}', '{}')".format(user_id, request.body))
            return HttpResponse("Success!", 200)

