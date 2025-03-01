from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'base/home.html')

def classroom(request):
    return HttpResponse('Filler for Classroom page')