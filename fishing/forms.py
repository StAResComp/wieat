from django import forms

class DataSearchForm(forms.Form):
    datatypes = (('tracks','Tracks'),('tows','Tows'),('catch','Catch'))
    datatype = forms.ChoiceField(choices = datatypes)
    user = forms.CharField(label='Username', max_length=20, required=False)
    datefrom = forms.DateField(label='From Date (YYYY-MM-DD)', required=False)
    dateto = forms.DateField(label='To Date (YYYY-MM-DD)', required=False)

class MyDataSearchForm(forms.Form):
    datatypes = (('tracks','Tracks'),('tows','Tows'),('catch','Catch'))
    datatype = forms.ChoiceField(choices = datatypes)
    datefrom = forms.DateField(label='From Date (YYYY-MM-DD)', required=False)
    dateto = forms.DateField(label='To Date (YYYY-MM-DD)', required=False)
