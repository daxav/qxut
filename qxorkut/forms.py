from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from .models import *

def usernameErrorMess():
	error_messages = {
		"unique" : "Já existe um usuário com esse nome no sistema.",
	}

	return error_messages

def emailErrorMess():
	error_messages = {
		"invalid" : "Insira um e-mail válido."
	}

	return error_messages

def imageErrorMess():
	error_messages = {
		"invalid_image" : "Imagem inválida.",
		"empty" : "Imagem vazia.",
		"missing" : "Imagem não encontrada.",
		"invalid" : "Imagem inválida.",
	}

	return error_messages

def passHelpText():
	return "<ul><li>Sua senha não deve ter menos que 8 caracteres.</li><li>Sua senha não pode ser muito parecida com suas outras informações pessoais.</li><li>Sua senha não deve ser muito comum.</li><li>Sua senha não pode ser totalmente numérica.</li></ul>"

def userHelpText():
	return "<ul><li>Máximo 150 caracteres. Somente permitido letras, digitos e os simbolos '@/./+/-/_'.</li></ul>"

class RegisterForm(UserCreationForm):
	error_css_class = "error"
	password2 = forms.CharField(label="Confirmar Senha", strip=False, widget= forms.PasswordInput)
	firstname = forms.CharField(label="Primeiro Nome", max_length = 200, min_length = 1)
	lastname = forms.CharField(label="Último Nome", max_length = 200, min_length = 1)
	username = forms.CharField(label="Nome de Usuário", max_length = 150, help_text=userHelpText(), error_messages=usernameErrorMess())
	email = forms.EmailField(label="Endereço de E-mail", error_messages=emailErrorMess())
	image = forms.ImageField(label="Foto do Perfil", required=False, error_messages=imageErrorMess())
	password1 = forms.CharField(label="Senha", strip=False,widget= forms.PasswordInput, help_text=passHelpText())
	class Meta:
		model = get_user_model()
		fields = [
			"firstname",
			"lastname",
			"username",
			"email",
			"password1",
			"password2",
			"image"
		]

class PostarForm(forms.models.ModelForm):
	text = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'id' : 'textoinput', 'placeholder': 'Escreva algo...', "class" : "commentinput"}))
	anexo = forms.FileField(label="Anexo", required=False, widget=forms.FileInput(attrs={"id" : 'postfileinput'}))
	class Meta:
		model = Postagem
		fields = [
			"text",
			"anexo"
		]

class ComunidadeForm(forms.models.ModelForm):
	nome = forms.CharField(label='Nome da Comunidade', max_length=150, widget=forms.TextInput(attrs={}), error_messages={"unique" : "Já existe uma comunidade com esse nome."})
	descricao = forms.CharField(label='Descrição da comunidade', max_length=500, widget=forms.TextInput(attrs={}))
	foto = forms.ImageField(label='Foto da comunidade', required=False, error_messages=imageErrorMess())
	class Meta:
		model = Comunidade
		fields = [
			"nome",
			"descricao",
			"foto"
		]