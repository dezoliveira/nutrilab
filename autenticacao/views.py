# Django
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages, auth
import os
from django.conf import settings
from .models import Ativacao
from hashlib import sha256

# Utils
from .utils import password_is_valid, email_html

# Cadastra um usuário
def cadastro(request):
    # GET:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')

        return render(request, 'cadastro.html')
    
    # POST:
    elif request.method == "POST":
        username = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # Verifica se password é válido
        if not password_is_valid(request, senha, confirmar_senha):
            return redirect('/auth/cadastro')
    
        # Tenta -> Cadastrar
        try:
            user = User.objects.create_user(
                username=username,
                password=senha,
                is_active=False
            )
            
            user.save()

            # Gera o token -> hash = username + email
            token = sha256(f"{username}{email}".encode()).hexdigest()

            # Registra no database
            ativacao = Ativacao(token=token, user=user)
            ativacao.save()

            # Seta o caminho do template do email
            path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')

            # Gera o email -> caminho do template, mensagem, email, username, link de ativação
            email_html(path_template, 'Cadastro confirmado', [email,], username=username, link_ativacao=f'127.0.0.1:8000/auth/ativar_conta/{token}')

            # Mensagem de cadastro
            messages.add_message(request, constants.SUCCESS, 'Usuário cadastrado com sucesso')
            return redirect('/auth/login')

        # Exceção -> Redireciona para cadastro
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('/auth/cadastro')
        

# Loga um usuário
def login(request):
    # GET
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')

        return render(request, 'login.html')
    
    # POST
    elif request.method == 'POST':
        username = request.POST.get('usuario')
        senha = request.POST.get('senha')

        # Busca o usuário
        usuario = auth.authenticate(username=username, password=senha)
        
        # Verifica seu usuário existe
        if not usuario:
            messages.add_message(request, constants.ERROR, 'Username ou senha inválidos')
            return redirect('/auth/login')
        else:
            auth.login(request, usuario)
            return redirect('/')

    return render(request, 'login.html')


# Desloga um usuário
def sair(request):
    auth.logout(request)
    return redirect('/auth/logar')


# Ativa a conta
def ativar_conta(request, token):
    token = get_object_or_404(Ativacao, token=token)

    # Verifica se token está ativo
    if token.ativo:
         messages.add_message(request, constants.WARNING, 'Esse token já foi usado')
         return redirect('/auth/logar')
    
    # Registra conta -> ativa token e usuário
    user = User.objects.get(username=token.user.username)
    user.is_active = True
    user.save()
    token.ativo = True
    token.save()
    messages.add_message(request, constants.SUCCESS, 'Conta ativada com sucesso')
    redirect('auth/logar')

