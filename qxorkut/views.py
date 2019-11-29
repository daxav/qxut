from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import RegisterForm
from qxorkut.models import *
from django.contrib.auth import login, authenticate
import PIL
from PIL import Image
from datetime import datetime
import pytz
from .forms import *

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

def getTimedeltaString(t):
	strdelta = strfdelta(t, "{days}") + " dias"
	if strdelta == "0 dias":
		strdelta = strfdelta(t, "{hours}") + " horas"
		if strdelta == "0 horas":
			strdelta = strfdelta(t, "{minutes}") + " minutos"
			if strdelta == "0 minutos":
				strdelta = strfdelta(t, "{seconds}") + " segundos"
				return strdelta
			return strdelta
		return strdelta
	return strdelta

def preparePostsContext(request, perfil):
	postagens = perfil.postagens.all()
	for amigo in perfil.amigos.all():
		postagens |= amigo.postagens.all()

	postagens = postagens.order_by('data')
	for postagem in postagens:
		data = postagem.data.replace(tzinfo=pytz.utc)
		now = datetime.now(pytz.utc)
		diff = now - data
		postagem.ago = getTimedeltaString(diff)

		postagem.file_isimg = False
		try:
			if postagem.anexo:
				filetest = Image.open(postagem.anexo.path)
				postagem.file_isimg = True
				#if filetest.verify():
				#	postagem.file_isimg = True
		except Exception as e:
			postagem.file_isimg = False
			

	context = {
		'posts' : postagens
	}
	return context

def perfil(request, id):
	perfil = Perfil.objects.get(pk=id)
	perfiluser = request.user.perfil.first()

	posts = perfil.postagens.order_by('data')
	for postagem in posts:
		data = postagem.data.replace(tzinfo=pytz.utc)
		now = datetime.now(pytz.utc)
		diff = now - data
		postagem.ago = getTimedeltaString(diff)

		postagem.file_isimg = False
		try:
			if postagem.anexo:
				filetest = Image.open(postagem.anexo.path)
				postagem.file_isimg = True
				#if filetest.verify():
				#	postagem.file_isimg = True
		except Exception as e:
			postagem.file_isimg = False

	amigos = perfil.amigos.all()
	comunidades = perfil.comunidades.all()

	isamigo = False
	if perfiluser.amigos.filter(id=perfil.id).exists():
		isamigo = True

	context = {
		"perfilsolicitado" : perfil, 
		"perfil" : perfiluser,
		"posts" : posts, 
		"postquantidade" : posts.count,
		"amigos" : amigos,
		"comunidades" : comunidades,
		"isamigo" : isamigo,
	}

	return render(request, 'main/perfil.html', context)

def index(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect("/qxut/login")

	perfil = request.user.perfil.first()

	comunidades = perfil.comunidades.all()
	amigos = perfil.amigos.all()

	form = PostarForm()

	context = {
		"perfil" : perfil,
		"username" : (perfil.nome + " " + perfil.sobrenome),
		"userimage" : perfil.foto,
		"comunidades" : comunidades,
		"amigos" : amigos,
		"form" : form
	}
	context.update(preparePostsContext(request, perfil))

	return render(request, "main/index.html", context)

def atualizarPosts(request):
	user = request.user
	if not user.is_authenticated:
		return redirect("/qxut/login")

	perfil = user.perfil.first()

	form = PostarForm(request.POST, request.FILES)
	if form.is_valid():
		newpostagem = Postagem()
		newpostagem.idperfil = perfil
		newpostagem.texto = form.cleaned_data.get("text")
		newpostagem.anexo = form.cleaned_data.get("anexo")
		newpostagem.data = datetime.now(pytz.utc)
			
		newpostagem.save()

	context = preparePostsContext(request, perfil)

	rendered = render(request, "main/posts.html", context).content.decode()

	response = {"response" : rendered}
	return JsonResponse(response)

def register(request):
	if request.method == "POST":
		form = RegisterForm(request.POST, request.FILES)

		if form.is_valid():
			user = form.save()

			username = form.cleaned_data.get("username")
			password = form.cleaned_data.get("password1")

			perfil = Perfil()
			perfil.iduser = user
			perfil.nome = form.cleaned_data.get("firstname")
			perfil.sobrenome = form.cleaned_data.get("lastname")
			perfil.foto = form.cleaned_data.get("image")
			perfil.save()

			user.perfil.add(perfil)

			user = authenticate(username=username, password=password)
			login(request, user)
			return HttpResponseRedirect("/qxut/")

	else:
		form = RegisterForm()

	return render(request, "registration/register.html", {"form" : form})

def busca_amigos(request):
	if not request.user.is_authenticated:
		return redirect("/qxut/login")

	text = request.POST.get('nome', '')
	
	vazio = False
	if text == '':
		perfil = request.user.perfil.first()
		amigos = perfil.amigos.all()
		vazio = True
	else:
		amigos = Perfil.objects.filter(nome__contains=text)
		amigos |= Perfil.objects.filter(sobrenome__contains=text)

	context = {
		'amigos' : amigos,
	}

	rendered = render(request, "main/amigos.html", context).content.decode()

	response = {"response" : rendered, 'vazio' : vazio,}
	return JsonResponse(response)

def add_amigo(request):
	if not request.user.is_authenticated:
		return redirect("/qxut/login")

	perfil = request.user.perfil.first()
	idamigo = request.POST.get("id")
	amigo_passado = Perfil.objects.get(pk = idamigo)
	amigo = Amigo()
	amigo.idperfil = perfil
	amigo.amigo = amigo_passado
	amigo.save()

	return HttpResponse("200")

def rem_amigo(request):
	if not request.user.is_authenticated:
		return redirect("/qxut/login")

	idamigo = request.POST.get("id")
	Amigo.objects.filter(amigo = idamigo).delete()

	return HttpResponse("200")

def busca_comunidades(request):
	if not request.user.is_authenticated:
		return redirect("/qxut/login")

	text = request.POST.get('nome', '')
	
	vazio = False
	if text == '':
		perfil = request.user.perfil.first()
		comunidades = perfil.comunidades.all()
		vazio = True
	else:
		comunidades = Comunidade.objects.filter(nome__contains=text)

	context = {
		'comunidades' : comunidades,
	}

	rendered = render(request, "main/comunidades.html", context).content.decode()

	response = {"response" : rendered, 'vazio' : vazio,}
	return JsonResponse(response)

def nova_comunidade(request):
	if not request.user.is_authenticated:
		return redirect("/qxut/login")

	if request.method == "POST":
		form = ComunidadeForm(request.POST, request.FILES)

		if form.is_valid():
			comunidade = Comunidade()
			comunidade.nome = form.cleaned_data.get("nome")
			comunidade.descricao = form.cleaned_data.get("descricao")
			comunidade.foto = form.cleaned_data.get("foto")
			print(form.cleaned_data.get("foto"))

			perfil = Perfil()
			perfil.iduser = request.user
			perfil.nome = comunidade.nome
			perfil.sobrenome = comunidade.descricao
			perfil.foto = form.cleaned_data.get("foto")
			perfil.save()

			comunidade.idadmin = request.user.perfil.first()
			comunidade.comunidade_perfil = perfil
			comunidade.save()

			request.user.perfil.first().comunidades.add(comunidade)

			return redirect("/qxut/")
	else:
		form = ComunidadeForm()
	
	context = {
		"form" : form,
	}

	return render(request, "main/novacomunidade.html", context)

def comunidade(request, id):
	if not request.user.is_authenticated:
		return redirect("/qxut/login")

	comunidade = Comunidade.objects.get(pk=id)

	perfil = comunidade.comunidade_perfil
	perfiluser = request.user.perfil.first()

	form = None
	if perfiluser.id == comunidade.idadmin.id:
		if request.method == "POST":
			form = PostarForm(request.POST, request.FILES)
			if form.is_valid():
				newpostagem = Postagem()
				newpostagem.idperfil = perfil
				newpostagem.texto = form.cleaned_data.get("text")
				newpostagem.anexo = form.cleaned_data.get("anexo")
				newpostagem.data = datetime.now(pytz.utc)
					
				newpostagem.save()

				context = preparePostsContext(request, perfil)
				count = context.get('posts').count()
				rendered = render(request, "main/posts.html", context).content.decode()

				response = {"response" : rendered, "count" : count}
				return JsonResponse(response)
		else:
			form = PostarForm()

	context = {
		"comunidade" : comunidade,
		"perfilsolicitado" : perfil, 
		"perfil" : perfiluser,
		"form": form
	}
	context.update(preparePostsContext(request, perfil))
	context.update({"postquantidade" : context.get('posts').count,})

	return render(request, 'main/comunidade.html', context)

def editar_perfil(request):

	form = RegisterForm()
	return render(request, 'main/editarperfil.html', {"form" : form})