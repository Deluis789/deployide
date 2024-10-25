# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
# from apps.home.views import ReportFichasView


urlpatterns = [
    #PAGINA
    path('', views.inicio, name='inicio'),
    path('geoportal/', views.geoportal, name='geoportal'),
    # The home page
    path('riesgo/', views.index, name='home'),
    path('listarUsuarios/', views.listar, name='listarUsuarios'),
    path('registrarUsuarios/', views.registrarUsuarios, name='registrarUsuarios'),
    path('eliminarUsuarios/<str:ci>/', views.eliminarUsuarios, name='eliminarUsuarios'),
    path('edicionUsuarios/<str:ci>', views.edicionUsuarios, name='edicionUsuarios'),
    path('editarUsuarios/', views.editarUsuarios, name='editarUsuarios'),
    
    path('listarVecinos/', views.listarVecinos, name='listarVecinos'),
    path('registrarVecinos/', views.registrarVecinos, name='registrarVecinos'),
    path('eliminarSolicitudVecino/<str:codigo_vecino>/', views.eliminarSolicitudVecino, name='eliminarSolicitudVecino'),
    
    path('solicitud/nueva/', views.formulario_solicitud, name='formulario_solicitud'),
    path('obtener-datos-vecino/<int:vecino_id>/', views.obtener_datos_vecino, name='obtener_datos_vecino'),
    path('listarSolicitudes/', views.listarSolicitudes, name='listarSolicitudes'),
    path('eliminarSolicitudes/<str:codigo_vecino>/', views.eliminarSolicitudes, name='eliminarSolicitudes'),
    
    path('ficha/', views.formulario_ficha, name='formulario_ficha'),
    path('obtener_datos/<int:codigo_id>/', views.obtener_datos_solicitudes, name='obtener_datos_solicitudes'),
    path('listarFichas/', views.listarFichas, name='listarFichas'),
    path('eliminarFichas/<int:codigo>/', views.eliminarFichas, name='eliminarFichas'),
    
    
    path('pdf/<int:ficha_id>/', views.render_pdf_view, name='render_pdf'),  # URL para generar PDF
    # Otras URLs de tu aplicación
    
    
    # path('reporteFichas/', ReportFichasView.as_view(), name='reporteFichas'),
    # Matches any html filer
    re_path(r'^.*\.*', views.pages, name='pages'),

]
