from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def cadastro(request):
    return HttpResponse('Você está na página de cadastro')

def logar(request):
    return HttpResponse('Você está na página de login')