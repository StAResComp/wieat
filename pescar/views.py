# from django.shortcuts import render
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from datetime import datetime
from dateutil.parser import parse
from django.shortcuts import render
import csv
import sys
from . import forms
from .forms import DataSearchForm

def index(request):
    return HttpResponse("Hello world")

def search(request):
    if request.user.is_authenticated and request.user.groups.filter(name='Researchers').exists():
        return render(request, 'search.html', {'form': DataSearchForm().as_p()})
    else:
        return HttpResponse('Permission denied for user {}'.format(request.user.username), status=403)

def data(request):
    if request.user.is_authenticated and request.user.groups.filter(name='Researchers').exists():
        form = DataSearchForm(request.GET)
        if form.is_valid():
            datatype = request.GET.get('datatype','tracks')
            user = request.GET.get('user','')
            date_from_str = request.GET.get('datefrom','')
            date_from = None
            if date_from_str != '':
                date_from = parse(date_from_str, dayfirst=True)
            date_to_str = request.GET.get('dateto','')
            date_to = None
            if date_to_str != '':
                date_to = parse(date_to_str, dayfirst=True)

            table_name = 'tracks'
            if datatype == 'tows' or datatype == 'tow':
                table_name = 'tows'
            elif datatype == 'hauls' or datatype == 'haul':
                table_name = 'hauls'

            query_str = 'SELECT * FROM {}'.format(table_name)
            query_vals = []
            needs_where = True

            if user != '':
                if needs_where:
                    query_str += " WHERE"
                query_str += " username LIKE %s"
                query_vals.append(user)
                needs_where = False

            if date_from != None:
                if needs_where:
                    query_str += " WHERE"
                else:
                    query_str += " AND"
                query_str += " timestamp >= %s"
                query_vals.append(date_from)
                needs_where = False

            if date_to != None:
                if needs_where:
                    query_str += " WHERE"
                else:
                    query_str += " AND"
                query_str += " timestamp < %s"
                query_vals.append(date_to)
                needs_where = False

            cursor = connections['data'].cursor()
            cursor.execute(query_str, tuple(query_vals))
            records = cursor.fetchall()

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(table_name)

            writer = csv.writer(response)
            writer.writerow([i[0] for i in cursor.description])
            writer.writerows(records)

            return response

        else:
            return HttpResponse('Permission denied for user {}'.format(request.user.username), status=403)

    else:
        return HttpResponse('Permission denied for user {}'.format(request.user.username), status=403)

def search_my_data(request):
    if request.user.is_authenticated:
        return render(request, 'search-my-data.html', {'form': MyDataSearchForm().as_p()})
    else:
        return HttpResponse('Permission denied for user {}. Authenticated: {}'.format(request.user.username, request.user.is_authenticated), status=403)

def my_data(request):
    if request.user.is_authenticated:
        form = DataSearchForm(request.GET)
        if form.is_valid():
            datatype = request.GET.get('datatype','tracks')
            # Get username from session info
            user = request.user.username
            date_from_str = request.GET.get('datefrom','')
            date_from = None
            if date_from_str != '':
                date_from = parse(date_from_str, dayfirst=True)
            date_to_str = request.GET.get('dateto','')
            date_to = None
            if date_to_str != '':
                date_to = parse(date_to_str, dayfirst=True)

            table_name = 'tracks'
            if datatype == 'tows' or datatype == 'tow':
                table_name = 'tows'
            elif datatype == 'hauls' or datatype == 'haul':
                table_name = 'hauls'

            query_str = 'SELECT * FROM {} WHERE username LIKE %s'.format(table_name)
            query_vals = []
            query_vals.append(user)

            if date_from != None:
                query_str += " AND timestamp >= %s"
                query_vals.append(date_from)

            if date_to != None:
                query_str += " AND timestamp < %s"
                query_vals.append(date_to)

            cursor = connections['data'].cursor()
            cursor.execute(query_str, tuple(query_vals))
            records = cursor.fetchall()

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(table_name)

            writer = csv.writer(response)
            writer.writerow([i[0] for i in cursor.description])
            writer.writerows(records)

            return response

        else:
            return HttpResponse('Permission denied for user {}'.format(request.user.username), status=403)

    else:
        return HttpResponse('Permission denied for user {}'.format(request.user.username), status=403)

class ApiEndpoint(ProtectedResourceView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            username = request.user.username
            cursor = connections['data'].cursor()
            cursor.execute("SELECT * FROM users WHERE username LIKE %s", (username,))
            users = cursor.fetchall()
            user_id = None
            if len(users) == 0:
                cursor.execute("INSERT INTO users (username) VALUES (%s) RETURNING id", (username,))
                user_id = cursor.fetchone()[0]
            else:
                user_id = users[0][0]
            body = request.body.decode('utf-8')
            cursor.execute("INSERT INTO trips (user_id, data) VALUES (%s, %s)", (user_id, body,))
            return HttpResponse("{'Success':'True'}", 200)

