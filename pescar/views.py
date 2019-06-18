# from django.shortcuts import render
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello world")

class ApiEndpoint(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello, OAuth2!')

    def post(self, request, *args, **kwargs):
        return HttpResponse('Hello, OAuth2!')
