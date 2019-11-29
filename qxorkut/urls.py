from django.urls import include,path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name = 'register'),
    path('add_post/', views.atualizarPosts, name = "add_post"),
    path('', include('django.contrib.auth.urls')),
    path('perfil/<int:id>', views.perfil, name = 'perfil'),
    path('busca_amigos/', views.busca_amigos, name = 'busca_amigos'),
    path('add_amigo/', views.add_amigo, name = 'add_amigo'),
    path('rem_amigo/', views.rem_amigo, name = 'rem_amigo'),
    path('busca_comunidades/', views.busca_comunidades, name = 'busca_comunidades'),
    path('nova_comunidade/', views.nova_comunidade, name = "nova_comunidade"),
    path('comunidade/<int:id>', views.comunidade, name = "comunidade"),
    path('editar_perfil', views.editar_perfil, name = "editar_perfil"),
]