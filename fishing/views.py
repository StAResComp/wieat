# from django.shortcuts import render
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from datetime import datetime
from dateutil.parser import parse
from django.shortcuts import render
import psycopg2
import django_tables2 as tables
import csv
import sys
from . import forms
from .forms import DataSearchForm
from .forms import MyDataSearchForm

@login_required()
def index(request):
    return render(request, 'index.html')

@login_required()
def search_data(request):
    if request.user.is_authenticated and request.user.groups.filter(name='Researchers').exists():
        if request.GET.get('datatype') is None:
            return render(request, 'search-data.html', {'form': DataSearchForm()})
        else:
            __do_data_response(request, True)
    else:
        return HttpResponse('Permission denied for user {}'.format(request.user.username), status=403)

@login_required()
def search_my_data(request):
    if request.user.is_authenticated:
        if request.GET.get('datatype') is None:
            return render(request, 'search-my-data.html', {'form': MyDataSearchForm()})
        else:
            __do_data_response(request)
    else:
        return HttpResponse('Permission denied for user {}'.format(request.user.username), status=403)

def __do_data_response(request, other_user = False):

    form = None
    return_template = 'search-my-data.html'
    if other_user:
        form = DataSearchForm(request.GET)
        return_template = 'search-data.html'
    else:
        form = MyDataSearchForm(request.GET)

    if form.is_valid():

        datatype = request.GET.get('datatype','tracks')
        date_from_str = request.GET.get('datefrom','')
        date_to_str = request.GET.get('dateto','')
        user = request.user.username
        if other_user:
            user = request.GET.get('user','')

        if request.GET.get('download') is None:
            table = __get_table(__get_data(datatype, user, date_from_str, date_to_str), datatype, request.GET.get("page", 1))
            return render(request, return_template, locals())
        else:
            return __get_csv_response(__get_data(datatype, user, date_from_str, date_to_str), datatype)

    else:
        return render(request, return_template)

def __get_table(cursor, datatype, page):
    records = cursor.fetchall()
    if datatype == 'tracks':
        table = TracksTable(records, template_name="django_tables2/bootstrap4.html")
    elif datatype == 'tows' or datatype == 'tow':
        table = TowsTable(records, template_name="django_tables2/bootstrap4.html")
    elif datatype == 'catch':
        table = CatchTable(records, template_name="django_tables2/bootstrap4.html")
    table.paginate(page=page, per_page=50)
    return table

def __get_csv_response(cursor, datatype):
    records = cursor.fetchall()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(datatype)
    writer = csv.writer(response)
    writer.writerow([i[0] for i in cursor.description])
    writer.writerows(records)
    return response

def __get_data(datatype = 'tracks', username = None, date_from_str = '', date_to_str = ''):
    date_from = None
    if date_from_str != '':
        date_from = parse(date_from_str, dayfirst=False)
    date_to = None
    if date_to_str != '':
        date_to = parse(date_to_str, dayfirst=False)

    table_name = 'tracks'
    if datatype == 'tows' or datatype == 'tow':
        table_name = 'tows'
    elif datatype == 'catch':
        table_name = 'catch'

    query_str = 'SELECT * FROM {}'.format(table_name)
    query_vals = []
    needs_where = True

    if username != '':
        if needs_where:
            query_str += " WHERE"
        query_str += " username LIKE %s"
        query_vals.append(username)
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

    conn = connections['data']
    conn.ensure_connection()
    cursor = conn.connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    cursor.execute(query_str, tuple(query_vals))

    return cursor

class TracksTable(tables.Table):
    username = tables.Column(orderable=False)
    trip = tables.Column(orderable=False)
    latitude = tables.Column(orderable=False)
    longitude = tables.Column(orderable=False)
    accuracy = tables.Column(orderable=False)
    timestamp = tables.DateTimeColumn(orderable=False)

class TowsTable(tables.Table):
    username = tables.Column(orderable=False)
    trip = tables.Column(orderable=False)
    local_id = tables.Column(orderable=False)
    weight = tables.Column(orderable=False)
    timestamp = tables.Column(orderable=False)

class CatchTable(tables.Table):
    username = tables.Column(orderable=False)
    trip = tables.Column(orderable=False)
    species = tables.Column(orderable=False)
    weight = tables.Column(orderable=False)
    timestamp = tables.Column(orderable=False)

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

