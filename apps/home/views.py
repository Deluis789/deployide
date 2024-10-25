# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse
from .models import Usuarios, CalleAv, Urbanizaciones, SolicitudVecino, Solicitudes, FichaOperativa
from django.contrib.auth.models import Group, User

#pagina vistas--------------------->>>>>>>>>>>>>>>><
def inicio(request):
    return render(request, 'pagina/inicio.html', {})

def geoportal(request):
    return render(request, 'pagina/geoportal.html', {})


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

def listar(request):
    usuariosListados = Usuarios.objects.all()
    return render(request, "home/listarusuarios.html", {"usuarios": usuariosListados})

def registrarUsuarios(request):
    if request.method == 'POST':
        # Obtener campos del formulario
        nombres = request.POST.get('nombres')
        apellido_paterno = request.POST.get('apellido_paterno')
        apellido_materno = request.POST.get('apellido_materno')
        rol_id = request.POST.get('rol')  # ID del rol
        user_id = request.POST.get('user')  # ID del usuario
        ci = request.POST.get('ci')  # Cédula de identidad
        urbanizacion_id = request.POST.get('urbanizaciones')  # ID de urbanización
        calle_av_name = request.POST.get('calle_avenida')  # Nombre de la calle
        numero_vivienda = request.POST.get('numero_vivienda')  # Número de vivienda

        # Obtener el grupo (rol) desde la base de datos
        grupo = Group.objects.get(id=rol_id)

        # Obtener el usuario desde la base de datos
        user = User.objects.get(id=user_id)

        # Obtener la urbanización desde la base de datos usando el ID
        urbanizacion = Urbanizaciones.objects.get(gid=urbanizacion_id)

        # Crear o obtener la instancia de CalleAv
        calle_av, created = CalleAv.objects.get_or_create(
            nombre=calle_av_name,
            defaults={'descripcion': ''}
        )

        # Crear el registro de usuario en la base de datos
        usuario = Usuarios.objects.create(
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            user=user,
            ci=ci,
            calle_av=calle_av,
            urbanizaciones=urbanizacion,
            numero_vivienda=numero_vivienda
        )

        # Generar el código de usuario
        codigo_usuario = usuario._generate_unique_code()  # Llama al método del modelo
        usuario.codigo_usuario = codigo_usuario  # Asigna el código generado
        usuario.save()  # Guarda el usuario para que tenga un ID

        # Asigna el rol (grupo) al usuario
        usuario.rol.add(grupo)  

        # Aquí pasamos los grupos de todos los usuarios, no solo del recién creado
        grupos = Group.objects.all()  # Obtener todos los grupos (roles) disponibles
        users = User.objects.all()  # Obtener todos los usuarios disponibles

        return render(request, 'home/formusuarios.html', {
            'zonas_urb': Urbanizaciones.objects.all(),  # Obtener todas las urbanizaciones para el formulario
            'usuario': usuario,  # Pasar el usuario creado a la plantilla
            'grupos': grupos,  # Pasar todos los grupos disponibles
            'users': users,  # Pasar todos los usuarios disponibles
            'codigo_usuario': codigo_usuario,  # Pasar el código de usuario generado
        })
    else:
        # Si no es un POST, renderiza el formulario (opcional)
        zonas_urb = Urbanizaciones.objects.all()  # Obtén todas las urbanizaciones para el formulario
        grupos = Group.objects.all()  # Obtener todos los grupos
        users = User.objects.all()  # Obtener todos los usuarios
        return render(request, 'home/formusuarios.html', {
            'zonas_urb': zonas_urb,
            'grupos': grupos,
            'users': users,  # Asegúrate de pasar todos los usuarios
        })
from django.contrib import messages

def eliminarUsuarios(request, ci):
    try:
        # Obtener el usuario por su username (que es el CI)
        user = User.objects.get(username=ci)
        user.delete()
        messages.success(request, "Usuario eliminado con éxito.")
    except User.DoesNotExist:
        messages.error(request, "El usuario no existe.")
    except Exception as e:
        messages.error(request, f"Error al eliminar el usuario: {str(e)}")
    
    return redirect('listarUsuarios')  # Redirige a la lista de usuarios

def edicionUsuarios(request, ci):
    # Obtener el usuario correspondiente al CI
    usuario = Usuarios.objects.get(ci=ci)
    
    # Obtener todos los grupos de roles disponibles
    grupos = Group.objects.all()
    
    # Obtener todos los usuarios
    users = User.objects.all()
    
    # Obtener todas las zonas urbanas
    urbanizaciones = Urbanizaciones.objects.all()
    
    # Pasar estos datos al contexto
    return render(request, "home/editarusuarios.html", {
        "usuario": usuario,
        "grupos": grupos,
        "users": users,
        "urbanizaciones": urbanizaciones
    })


from django.shortcuts import render, get_object_or_404, redirect
def editarUsuarios(request):
    # Obtener datos del formulario
    nombres = request.POST['nombres']
    apellido_paterno = request.POST['apellido_paterno']
    apellido_materno = request.POST['apellido_materno']
    rol_id = request.POST.get('rol')
    user_id = request.POST.get('user')  # ID del usuario a editar
    ci = request.POST['ci']
    urbanizacion_id = request.POST.get('urbanizaciones') 
    calle_av_name = request.POST['calle_avenida']
    numero_vivienda = request.POST['numero_vivienda']

    # Obtener el usuario existente
    user = get_object_or_404(User, id=user_id)
    
    # Actualizar datos del usuario
    user.first_name = nombres
    user.last_name = apellido_paterno + " " + apellido_materno
    user.username = ci  # Si quieres que el CI sea el username
    user.save()

    # Actualizar grupo (rol)
    grupo = get_object_or_404(Group, id=rol_id)
    user.groups.clear()  # Limpiar grupos antiguos
    user.groups.add(grupo)  # Agregar nuevo rol

    # Actualizar zona urbana
    urbanizacion = get_object_or_404(Urbanizaciones, gid=urbanizacion_id)

    # Actualizar o crear la calle
    calle_av, created = CalleAv.objects.get_or_create(
        nombre=calle_av_name,
        defaults={'descripcion': '',}
    )

    # Actualizar información del modelo Usuarios
    usuario = get_object_or_404(Usuarios, user=user)
    usuario.urbanizaciones = urbanizacion
    usuario.calle_av = calle_av
    usuario.numero_vivienda = numero_vivienda
    usuario.save()

    return redirect('listarUsuarios')  # Redirigir a la lista de usuarios

# SolicitudVecino vistas----------------------------------
def listarVecinos(request):
    vecinosListados = SolicitudVecino.objects.all()
    return render(request, "home/listarvecino.html", {"vecinos": vecinosListados})

def registrarVecinos(request):
    codigo_vecino = None  # Variable para almacenar el código generado

    if request.method == 'POST':
        urbanizacion_id = request.POST.get('urbanizacion')
        ubicacion_geografica = request.POST.get('ubicacion')
        foto = request.FILES.get('imagen')
        nombres = request.POST.get('nombres')
        apellido_paterno = request.POST.get('apellido_paterno')
        apellido_materno = request.POST.get('apellido_materno')
        cedula_identidad = request.POST.get('cedula_identidad')
        celular = request.POST.get('celular')

        # Obtener la urbanización desde la base de datos
        urbanizacion = Urbanizaciones.objects.get(gid=urbanizacion_id)

        # Generar un nuevo código de vecino
        codigo_vecino = SolicitudVecino()._generate_unique_code()  # Genera el código sin guardar el objeto

        # Crear el registro de solicitud en la base de datos
        solicitud = SolicitudVecino.objects.create(
            urbanizaciones=urbanizacion,
            codigo_vecino=codigo_vecino,  # Asigna el código generado
            ubicacion_geografica=ubicacion_geografica,
            foto=foto,
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            cedula_identidad=cedula_identidad,
            celular=celular
        )

        # Guarda la solicitud para ejecutar la lógica en el método save
        solicitud.save()

        # Redirigir o renderizar la respuesta
        return render(request, 'pagina/formvecino.html', {
            'solicitud': solicitud,
        })
    else:
        # Si no es un POST, generamos un nuevo código vecino
        codigo_vecino = SolicitudVecino()._generate_unique_code()  # Genera el código para mostrar en el formulario

        # Obtener todas las urbanizaciones para el formulario
        urbanizaciones = Urbanizaciones.objects.all()
        return render(request, 'pagina/formvecino.html', {
            'urbanizaciones': urbanizaciones,
            'codigo_vecino': codigo_vecino,  # Pasar el código generado a la plantilla
        })

def eliminarSolicitudVecino(request, codigo_vecino):
    try:
        # Obtener la solicitud vecino por su código único
        solicitud_vecino = get_object_or_404(SolicitudVecino, codigo_vecino=codigo_vecino)
        solicitud_vecino.delete()
        messages.success(request, "Solicitud de vecino eliminada con éxito.")
    except Exception as e:
        messages.error(request, f"Error al eliminar la solicitud de vecino: {str(e)}")
    
    return redirect('listarVecinos')

# Solicitudes ------->>>>>>>>>>>>>>


from django.http import JsonResponse
# Vista para manejar el formulario principal
def formulario_solicitud(request):
    vecinos = SolicitudVecino.objects.all()
    zonas_urb = Urbanizaciones.objects.all()
    designaciones = User.objects.all()

    estado_opciones = Solicitudes._meta.get_field('estado').choices
    
    if request.method == 'POST':
        # Aquí puedes procesar los datos y guardar la solicitud
        # Recoge los datos del formulario manualmente, por ejemplo:
        codigo_vecino_id = request.POST.get('codigo_vecino')
        distrito = request.POST.get('distrito')
        nombres = request.POST.get('nombres')
        ubicacion_geografica = request.POST.get('ubicacion_geografica') 
        apellido_paterno = request.POST.get('apellido_paterno')
        apellido_materno = request.POST.get('apellido_materno')
        estado = request.POST.get('estado')
        cedula_identidad = request.POST.get('cedula_identidad')
        designacion_id = request.POST.get('designacion')
        
                # Crea una nueva instancia de Solicitudes
        solicitud = Solicitudes(
            urbanizaciones_id=request.POST.get('urbanizaciones'),  # Asegúrate de que este campo esté en tu formulario
            codigo_vecino_id=codigo_vecino_id,
            distrito=distrito,
            ubicacion_geografica=ubicacion_geografica,  # Agregado
            nombres=nombres,  # No es necesario si se guarda desde 'codigo_vecino'
            apellido_paterno=apellido_paterno,  # No es necesario si se guarda desde 'codigo_vecino'
            apellido_materno=apellido_materno,  # No es necesario si se guarda desde 'codigo_vecino'
            cedula_identidad=cedula_identidad,  # Agregado
            designacion_id=designacion_id,  # Relación con el User
            estado=estado
        )
        solicitud.save()

        # Guardar en la base de datos si es necesario

    return render(request, 'home/formsolicitudes.html', {
        'vecinos': vecinos,
        'zonas_urb': zonas_urb,
        'designaciones': designaciones,
        'estado_opciones': estado_opciones,
    })

# Vista para manejar el AJAX que devuelve los datos del vecino
def obtener_datos_vecino(request, vecino_id):
    vecino = get_object_or_404(SolicitudVecino, id=vecino_id)
    data = {
        'nombres': vecino.nombres,
        'apellido_paterno': vecino.apellido_paterno,
        'apellido_materno': vecino.apellido_materno,
        'cedula_identidad': vecino.cedula_identidad,
        'ubicacion_geografica': vecino.ubicacion_geografica,
        'distrito': vecino.distrito,
    }
    return JsonResponse(data)

def listarSolicitudes(request):
    solicitudesListados = Solicitudes.objects.all()
    return render(request, "home/listarsolicitudes.html", {"solicitud": solicitudesListados})

def eliminarSolicitudes(request, codigo_vecino):
    try:
        # Obtener la solicitud vecino por su código único
        solicitudes = get_object_or_404(Solicitudes, codigo_vecino=codigo_vecino)
        solicitudes.delete()
        messages.success(request, "Solicitud de vecino eliminada con éxito.")
    except Exception as e:
        messages.error(request, f"Error al eliminar la solicitud de vecino: {str(e)}")
    
    return redirect('listarSolicitudes')


def formulario_ficha(request):
    solicitudes = Solicitudes.objects.all()
    estado_opciones = FichaOperativa._meta.get_field('estado').choices
    designaciones = Usuarios.objects.all()

    if request.method == 'POST':
        codigo_id = request.POST.get('codigo')
        solicitud = get_object_or_404(Solicitudes, id=codigo_id)

        # Obtén los datos del formulario
        fecha = request.POST.get('fecha')
        distrito = solicitud.distrito
        urbanizacion = solicitud.urbanizaciones.nombre
        ubicacion_direccion = request.POST.get('ubicacion_direccion')
        latitud_longitud = request.POST.get('latitud_longitud')  # Asegúrate de capturar esto
        tecnico_id = request.POST.get('designacion')  # Captura el id del técnico seleccionado
        cuadrilla = request.POST.get('cuadrilla')
        maquinaria = request.POST.get('maquinaria')
        operador = request.POST.get('operador')
        concepto = request.POST.get('concepto')
        volumen = request.POST.get('volumen')
        fotoInicio = request.FILES.get('imagenInicio')
        fotoDesarollo = request.FILES.get('imagenDesarollo')
        fotoCulminado = request.FILES.get('imagenCulminado')
        estado = request.POST.get('estado')

        try:
            # Crear una nueva instancia de FichaOperativa
            ficha = FichaOperativa(
                codigo=solicitud,
                fecha=fecha,
                distrito=distrito,
                urbanizacion=urbanizacion,
                ubicacion_direccion=ubicacion_direccion,
                latitud_longitud=latitud_longitud,  # Asegúrate de usar este valor
                tecnico=tecnico_id,  # Guarda el id del técnico o usa el nombre según lo necesites
                cuadrilla=cuadrilla,
                maquinaria=maquinaria,
                operador=operador,
                concepto=concepto,
                volumen=volumen,
                fotoInicio=fotoInicio,
                fotoDesarollo=fotoDesarollo,
                fotoCulminado=fotoCulminado,
                estado=estado
            )
            ficha.save()
        except Exception as e:
            print(f"Error al guardar FichaOperativa: {e}")

    return render(request, 'home/formfichas.html', {
        'solicitudes': solicitudes,
        'estado_opciones': estado_opciones,
        'designaciones': designaciones,
    })


# Vista para manejar el AJAX que devuelve los datos de solicitudes
def obtener_datos_solicitudes(request, codigo_id):
    solicitud = get_object_or_404(Solicitudes, id=codigo_id)
    data = {
        'distrito': solicitud.distrito,
        'urbanizacion': solicitud.urbanizaciones.nombre,
        'latitud_longitud': solicitud.ubicacion_geografica,  # Asegúrate de que esto esté disponible
        'tecnico': f"{solicitud.designacion.first_name} {solicitud.designacion.last_name}",
    }
    return JsonResponse(data)

def listarFichas(request):
    fichasListados = FichaOperativa.objects.all()
    return render(request, "home/listarfichas.html", {"fichas": fichasListados})

def eliminarFichas(request, codigo):
    try:
        # Obtener la solicitud vecino por su código único
        fichas = get_object_or_404(FichaOperativa, id=codigo)
        fichas.delete()
        messages.success(request, "Solicitud de vecino eliminada con éxito.")
    except Exception as e:
        messages.error(request, f"Error al eliminar la solicitud de vecino: {str(e)}")
    
    return redirect('listarSolicitudes')


import os
from django.template.loader import render_to_string
from xhtml2pdf import pisa
def render_pdf_view(request, ficha_id):
    # Obtiene la instancia de FichaOperativa según el ID proporcionado
    ficha = get_object_or_404(FichaOperativa, id=ficha_id)

    # Contexto para la plantilla
    context = {
        'ficha': ficha,
    }

    # Renderiza la plantilla en HTML
    template_path = 'home/rficha.html'
    html = render_to_string(template_path, context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ficha_operativa_{ficha.codigo}.pdf"'

    # Renderiza el HTML a PDF
    pisa_status = pisa.CreatePDF(html, dest=response, encoding='UTF-8', link_callback=fetch_resources)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)

    return response

def fetch_resources(uri, rel):
    """Función para obtener recursos como imágenes y CSS."""
    from django.conf import settings
    from django.core.files.storage import default_storage

    if uri.startswith(settings.MEDIA_URL):
        path = uri.replace(settings.MEDIA_URL, '')
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(full_path):
            return full_path
    return uri  # Deja que xhtml2pdf maneje cualquier otro URIa_status = pisa.CreatePDF(template.content, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)
    
    return response



