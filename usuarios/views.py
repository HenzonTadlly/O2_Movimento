from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Usuario
from .forms import (
    CriarUsuarioForm,
    EditarUsuarioForm,
    MeuPerfilForm,
    MinhaSenhaForm,
)
from grupos.models import Grupo
from membros.models import Membro


@login_required
def painel_redirect(request):
    usuario = request.user

    if usuario.tipo_usuario == 'admin':
        return redirect('dashboard_admin')
    elif usuario.tipo_usuario == 'coordenador':
        return redirect('dashboard_coordenador')
    elif usuario.tipo_usuario == 'supervisor':
        return redirect('dashboard_supervisor')
    elif usuario.tipo_usuario == 'lider':
        return redirect('dashboard_lider')

    return redirect('login')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def lista_coordenadores(request):
    if request.user.tipo_usuario != 'admin':
        messages.error(request, 'Sem permissão para acessar coordenadores.')
        return render(request, 'core/sem_permissao.html')

    coordenadores = Usuario.objects.filter(
        tipo_usuario='coordenador'
    ).order_by('first_name', 'username')

    busca = request.GET.get('busca', '').strip()
    status = request.GET.get('status', '').strip()

    if busca:
        coordenadores = coordenadores.filter(first_name__icontains=busca) | Usuario.objects.filter(
            tipo_usuario='coordenador',
            username__icontains=busca
        )

    if status == 'ativos':
        coordenadores = coordenadores.filter(ativo=True)
    elif status == 'inativos':
        coordenadores = coordenadores.filter(ativo=False)

    coordenadores = coordenadores.distinct().order_by('first_name', 'username')

    paginator = Paginator(coordenadores, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    context = {
        'coordenadores': page_obj,
        'page_obj': page_obj,
        'querystring': querystring,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Coordenadores', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Cadastrar usuário', 'url': reverse('criar_usuario'), 'variant': 'primary'},
        ],
        'filtros': {
            'busca': busca,
            'status': status,
        }
    }
    return render(request, 'usuarios/lista_coordenadores.html', context)


@login_required
def detalhe_coordenador(request, coordenador_id):
    if request.user.tipo_usuario != 'admin':
        messages.error(request, 'Sem permissão para acessar este coordenador.')
        return render(request, 'core/sem_permissao.html')

    coordenador = get_object_or_404(
        Usuario,
        id=coordenador_id,
        tipo_usuario='coordenador'
    )

    supervisores = Usuario.objects.filter(
        tipo_usuario='supervisor',
        coordenador_responsavel=coordenador
    ).order_by('first_name', 'username')

    lideres = Usuario.objects.filter(
        tipo_usuario='lider',
        supervisor_responsavel__coordenador_responsavel=coordenador
    ).distinct().order_by('first_name', 'username')

    grupos = Grupo.objects.filter(
        supervisor__coordenador_responsavel=coordenador,
        lider__supervisor_responsavel__coordenador_responsavel=coordenador
    ).distinct()

    context = {
        'coordenador': coordenador,
        'supervisores': supervisores,
        'lideres': lideres,
        'total_supervisores': supervisores.count(),
        'total_lideres': lideres.count(),
        'total_grupos': grupos.count(),
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Coordenadores', 'url': reverse('lista_coordenadores')},
            {'label': coordenador.get_full_name() or coordenador.username, 'url': ''},
        ],
        'page_actions': [
            {'label': 'Editar coordenador', 'url': reverse('editar_usuario', args=[coordenador.id]), 'variant': 'primary'},
            {'label': 'Voltar à lista', 'url': reverse('lista_coordenadores'), 'variant': 'secondary'},
        ]
    }
    return render(request, 'usuarios/detalhe_coordenador.html', context)


@login_required
def lista_supervisores(request):
    if request.user.tipo_usuario not in ['admin', 'coordenador']:
        messages.error(request, 'Sem permissão para acessar supervisores.')
        return render(request, 'core/sem_permissao.html')

    supervisores = Usuario.objects.filter(
        tipo_usuario='supervisor'
    ).order_by('first_name', 'username')

    if request.user.tipo_usuario == 'coordenador':
        supervisores = supervisores.filter(coordenador_responsavel=request.user)

    busca = request.GET.get('busca', '').strip()
    status = request.GET.get('status', '').strip()

    if busca:
        supervisores = supervisores.filter(first_name__icontains=busca) | supervisores.filter(username__icontains=busca)

    if status == 'ativos':
        supervisores = supervisores.filter(ativo=True)
    elif status == 'inativos':
        supervisores = supervisores.filter(ativo=False)

    supervisores = supervisores.distinct().order_by('first_name', 'username')

    paginator = Paginator(supervisores, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    context = {
        'supervisores': page_obj,
        'page_obj': page_obj,
        'querystring': querystring,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Supervisores', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Cadastrar usuário', 'url': reverse('criar_usuario'), 'variant': 'primary'},
        ],
        'filtros': {
            'busca': busca,
            'status': status,
        }
    }
    return render(request, 'usuarios/lista_supervisores.html', context)


@login_required
def detalhe_supervisor(request, supervisor_id):
    if request.user.tipo_usuario not in ['admin', 'coordenador']:
        messages.error(request, 'Sem permissão para acessar este supervisor.')
        return render(request, 'core/sem_permissao.html')

    supervisor = get_object_or_404(Usuario, id=supervisor_id, tipo_usuario='supervisor')

    if request.user.tipo_usuario == 'coordenador' and supervisor.coordenador_responsavel != request.user:
        messages.error(request, 'Sem permissão para acessar este supervisor.')
        return render(request, 'core/sem_permissao.html')

    lideres = Usuario.objects.filter(
        tipo_usuario='lider',
        supervisor_responsavel=supervisor
    ).order_by('first_name', 'username')

    grupos = Grupo.objects.filter(
        supervisor=supervisor
    ).select_related('escola', 'lider').order_by('nome')

    context = {
        'supervisor': supervisor,
        'lideres': lideres,
        'grupos': grupos,
        'total_lideres': lideres.count(),
        'total_grupos': grupos.count(),
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Supervisores', 'url': reverse('lista_supervisores')},
            {'label': supervisor.get_full_name() or supervisor.username, 'url': ''},
        ],
        'page_actions': [
            {'label': 'Editar supervisor', 'url': reverse('editar_usuario', args=[supervisor.id]), 'variant': 'primary'},
            {'label': 'Voltar à lista', 'url': reverse('lista_supervisores'), 'variant': 'secondary'},
        ]
    }
    return render(request, 'usuarios/detalhe_supervisor.html', context)


@login_required
def lista_lideres(request):
    if request.user.tipo_usuario not in ['admin', 'coordenador', 'supervisor']:
        messages.error(request, 'Sem permissão para acessar líderes.')
        return render(request, 'core/sem_permissao.html')

    lideres = Usuario.objects.filter(tipo_usuario='lider').order_by('first_name', 'username')

    if request.user.tipo_usuario == 'coordenador':
        lideres = lideres.filter(
            supervisor_responsavel__coordenador_responsavel=request.user
        ).distinct()

    if request.user.tipo_usuario == 'supervisor':
        lideres = lideres.filter(
            supervisor_responsavel=request.user
        ).distinct()

    busca = request.GET.get('busca', '').strip()
    status = request.GET.get('status', '').strip()

    if busca:
        lideres = lideres.filter(first_name__icontains=busca) | lideres.filter(username__icontains=busca)

    if status == 'ativos':
        lideres = lideres.filter(ativo=True)
    elif status == 'inativos':
        lideres = lideres.filter(ativo=False)

    lideres = lideres.distinct().order_by('first_name', 'username')

    paginator = Paginator(lideres, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    context = {
        'lideres': page_obj,
        'page_obj': page_obj,
        'querystring': querystring,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Líderes', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Cadastrar usuário', 'url': reverse('criar_usuario'), 'variant': 'primary'},
        ],
        'filtros': {
            'busca': busca,
            'status': status,
        }
    }
    return render(request, 'usuarios/lista_lideres.html', context)


@login_required
def detalhe_lider(request, lider_id):
    if request.user.tipo_usuario not in ['admin', 'coordenador', 'supervisor']:
        messages.error(request, 'Sem permissão para acessar este líder.')
        return render(request, 'core/sem_permissao.html')

    lider = get_object_or_404(Usuario, id=lider_id, tipo_usuario='lider')

    if request.user.tipo_usuario == 'coordenador':
        if not lider.supervisor_responsavel or lider.supervisor_responsavel.coordenador_responsavel != request.user:
            messages.error(request, 'Sem permissão para acessar este líder.')
            return render(request, 'core/sem_permissao.html')

    if request.user.tipo_usuario == 'supervisor':
        if lider.supervisor_responsavel != request.user:
            messages.error(request, 'Sem permissão para acessar este líder.')
            return render(request, 'core/sem_permissao.html')

    grupos = Grupo.objects.filter(lider=lider).select_related('escola', 'supervisor').order_by('nome')
    total_membros = Membro.objects.filter(grupo__lider=lider).count()

    context = {
        'lider': lider,
        'grupos': grupos,
        'total_grupos': grupos.count(),
        'total_membros': total_membros,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Líderes', 'url': reverse('lista_lideres')},
            {'label': lider.get_full_name() or lider.username, 'url': ''},
        ],
        'page_actions': [
            {'label': 'Editar líder', 'url': reverse('editar_usuario', args=[lider.id]), 'variant': 'primary'},
            {'label': 'Voltar à lista', 'url': reverse('lista_lideres'), 'variant': 'secondary'},
        ]
    }
    return render(request, 'usuarios/detalhe_lider.html', context)


@login_required
def criar_usuario(request):
    if request.user.tipo_usuario not in ['admin', 'coordenador', 'supervisor']:
        messages.error(request, 'Sem permissão para cadastrar usuário.')
        return render(request, 'core/sem_permissao.html')

    if request.method == 'POST':
        form = CriarUsuarioForm(
            request.POST,
            tipo_logado=request.user.tipo_usuario,
            usuario_logado=request.user
        )
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])

            if request.user.tipo_usuario == 'coordenador' and usuario.tipo_usuario == 'supervisor':
                usuario.coordenador_responsavel = request.user

            if request.user.tipo_usuario == 'supervisor' and usuario.tipo_usuario == 'lider':
                usuario.supervisor_responsavel = request.user

            usuario.save()
            messages.success(request, 'Usuário cadastrado com sucesso.')

            if usuario.tipo_usuario == 'coordenador':
                return redirect('lista_coordenadores')
            if usuario.tipo_usuario == 'supervisor':
                return redirect('lista_supervisores')
            if usuario.tipo_usuario == 'lider':
                return redirect('lista_lideres')

            return redirect('painel_redirect')
        else:
            messages.error(request, 'Não foi possível cadastrar o usuário.')
    else:
        form = CriarUsuarioForm(
            tipo_logado=request.user.tipo_usuario,
            usuario_logado=request.user
        )

    context = {
        'form': form,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Cadastrar usuário', 'url': ''},
        ],
        'page_actions': []
    }
    return render(request, 'usuarios/criar_usuario.html', context)


@login_required
def editar_usuario(request, usuario_id):
    usuario_editado = get_object_or_404(Usuario, id=usuario_id)

    if request.user.tipo_usuario not in ['admin', 'coordenador', 'supervisor']:
        messages.error(request, 'Sem permissão para editar usuário.')
        return render(request, 'core/sem_permissao.html')

    if request.user.tipo_usuario == 'coordenador':
        if usuario_editado.tipo_usuario == 'supervisor':
            if usuario_editado.coordenador_responsavel != request.user:
                messages.error(request, 'Sem permissão para editar este supervisor.')
                return render(request, 'core/sem_permissao.html')

        elif usuario_editado.tipo_usuario == 'lider':
            if not usuario_editado.supervisor_responsavel:
                messages.error(request, 'Sem permissão para editar este líder.')
                return render(request, 'core/sem_permissao.html')
            if usuario_editado.supervisor_responsavel.coordenador_responsavel != request.user:
                messages.error(request, 'Sem permissão para editar este líder.')
                return render(request, 'core/sem_permissao.html')

        else:
            messages.error(request, 'Sem permissão para editar este usuário.')
            return render(request, 'core/sem_permissao.html')

    if request.user.tipo_usuario == 'supervisor':
        if usuario_editado.tipo_usuario != 'lider' or usuario_editado.supervisor_responsavel != request.user:
            messages.error(request, 'Sem permissão para editar este líder.')
            return render(request, 'core/sem_permissao.html')

    if request.method == 'POST':
        form = EditarUsuarioForm(
            request.POST,
            instance=usuario_editado,
            usuario_logado=request.user
        )
        if form.is_valid():
            usuario = form.save(commit=False)

            if request.user.tipo_usuario == 'coordenador' and usuario.tipo_usuario == 'supervisor':
                usuario.coordenador_responsavel = request.user

            if request.user.tipo_usuario == 'supervisor' and usuario.tipo_usuario == 'lider':
                usuario.supervisor_responsavel = request.user

            usuario.save()
            messages.success(request, 'Usuário editado com sucesso.')

            if usuario.tipo_usuario == 'coordenador':
                return redirect('detalhe_coordenador', coordenador_id=usuario.id)
            if usuario.tipo_usuario == 'supervisor':
                return redirect('detalhe_supervisor', supervisor_id=usuario.id)
            if usuario.tipo_usuario == 'lider':
                return redirect('detalhe_lider', lider_id=usuario.id)

            return redirect('painel_redirect')
        else:
            messages.error(request, 'Não foi possível salvar as alterações do usuário.')
    else:
        form = EditarUsuarioForm(
            instance=usuario_editado,
            usuario_logado=request.user
        )

    context = {
        'form': form,
        'usuario_editado': usuario_editado,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Editar usuário', 'url': ''},
        ],
        'page_actions': []
    }
    return render(request, 'usuarios/editar_usuario.html', context)


@login_required
def meu_perfil(request):
    context = {
        'usuario_perfil': request.user,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Meu perfil', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Editar meu perfil', 'url': reverse('editar_meu_perfil'), 'variant': 'primary'},
            {'label': 'Alterar senha', 'url': reverse('alterar_minha_senha'), 'variant': 'secondary'},
        ]
    }
    return render(request, 'usuarios/meu_perfil.html', context)


@login_required
def editar_meu_perfil(request):
    usuario = request.user

    if request.method == 'POST':
        form = MeuPerfilForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect('meu_perfil')
        else:
            messages.error(request, 'Não foi possível atualizar o perfil.')
    else:
        form = MeuPerfilForm(instance=usuario)

    context = {
        'form': form,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Meu perfil', 'url': reverse('meu_perfil')},
            {'label': 'Editar perfil', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Voltar ao perfil', 'url': reverse('meu_perfil'), 'variant': 'secondary'},
        ]
    }
    return render(request, 'usuarios/editar_meu_perfil.html', context)


@login_required
def alterar_minha_senha(request):
    usuario = request.user

    if request.method == 'POST':
        form = MinhaSenhaForm(usuario, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Senha alterada com sucesso.')
            return redirect('meu_perfil')
        else:
            messages.error(request, 'Não foi possível alterar a senha. Verifique os campos.')
    else:
        form = MinhaSenhaForm(usuario)

    context = {
        'form': form,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Meu perfil', 'url': reverse('meu_perfil')},
            {'label': 'Alterar senha', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Voltar ao perfil', 'url': reverse('meu_perfil'), 'variant': 'secondary'},
        ]
    }
    return render(request, 'usuarios/alterar_senha.html', context)