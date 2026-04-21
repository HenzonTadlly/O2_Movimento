from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from .models import Grupo
from .forms import GrupoForm
from escolas.models import Escola
from django.urls import reverse

def grupo_permitido(usuario, grupo):
    if usuario.tipo_usuario == 'admin':
        return True

    if usuario.tipo_usuario == 'coordenador':
        return (
            grupo.supervisor and
            grupo.supervisor.coordenador_responsavel == usuario and
            grupo.lider and
            grupo.lider.supervisor_responsavel == grupo.supervisor
        )

    if usuario.tipo_usuario == 'supervisor':
        return (
            grupo.supervisor == usuario and
            grupo.lider and
            grupo.lider.supervisor_responsavel == usuario
        )

    if usuario.tipo_usuario == 'lider':
        return grupo.lider == usuario

    return False


@login_required
def lista_grupos(request):
    usuario = request.user

    if usuario.tipo_usuario == 'admin':
        grupos = Grupo.objects.all().select_related('escola', 'lider', 'supervisor')

    elif usuario.tipo_usuario == 'coordenador':
        grupos = Grupo.objects.filter(
            supervisor__coordenador_responsavel=usuario,
            lider__supervisor_responsavel__coordenador_responsavel=usuario
        ).select_related('escola', 'lider', 'supervisor').distinct()

    elif usuario.tipo_usuario == 'supervisor':
        grupos = Grupo.objects.filter(
            supervisor=usuario,
            lider__supervisor_responsavel=usuario
        ).select_related('escola', 'lider', 'supervisor').distinct()

    elif usuario.tipo_usuario == 'lider':
        grupos = Grupo.objects.filter(
            lider=usuario
        ).select_related('escola', 'lider', 'supervisor')

    else:
        grupos = Grupo.objects.none()

    busca = request.GET.get('busca', '').strip()
    status = request.GET.get('status', '').strip()
    escola_id = request.GET.get('escola', '').strip()

    if busca:
        grupos = grupos.filter(nome__icontains=busca)

    if status:
        grupos = grupos.filter(status=status)

    if escola_id:
        grupos = grupos.filter(escola_id=escola_id)

    grupos = grupos.order_by('nome')
    paginator = Paginator(grupos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    escolas = Escola.objects.filter(ativa=True).order_by('nome')

    page_actions = []
    if request.user.tipo_usuario in ['admin', 'coordenador', 'supervisor']:
        page_actions.append({
    'label': 'Criar grupo',
    'url': reverse('criar_grupo'),
    'variant': 'primary'
})

    context = {
        'grupos': page_obj,
        'page_obj': page_obj,
        'querystring': querystring,
        'escolas': escolas,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': ''},
        ],
        'page_actions': page_actions,
        'filtros': {
            'busca': busca,
            'status': status,
            'escola': escola_id,
        }
    }
    return render(request, 'grupos/lista.html', context)


@login_required
def detalhe_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)

    if not grupo_permitido(request.user, grupo):
        return render(request, 'core/sem_permissao.html')

    membros = grupo.membros.filter(ativo=True)
    encontros = grupo.encontros.all().order_by('-data_encontro')[:10]

    page_actions = [
        {'label': 'Ver membros', 'url': reverse('lista_membros', args=[grupo.id]), 'variant': 'secondary'},
        {'label': 'Cadastrar membro', 'url': reverse('cadastrar_membro', args=[grupo.id]), 'variant': 'primary'},
        {'label': 'Lançar frequência', 'url': reverse('lancar_frequencia', args=[grupo.id]), 'variant': 'primary'},
        {'label': 'Histórico', 'url': reverse('lista_encontros', args=[grupo.id]), 'variant': 'secondary'},
        {'label': 'Relatório', 'url': reverse('relatorio_grupo', args=[grupo.id]), 'variant': 'secondary'},
    ]

    if request.user.tipo_usuario in ['admin', 'coordenador', 'supervisor']:
        page_actions.append({
            'label': 'Editar grupo',
            'url': reverse('editar_grupo', args=[grupo.id]),
            'variant': 'secondary'
        })

    context = {
        'grupo': grupo,
        'membros': membros,
        'encontros': encontros,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': grupo.nome, 'url': ''},
        ],
        'page_actions': page_actions,
    }
    return render(request, 'grupos/detalhe.html', context)


@login_required
def criar_grupo(request):
    if request.user.tipo_usuario not in ['admin', 'coordenador', 'supervisor']:
        return render(request, 'core/sem_permissao.html')

    if request.method == 'POST':
        form = GrupoForm(request.POST, usuario_logado=request.user)
        if form.is_valid():
            grupo = form.save(commit=False)

            if request.user.tipo_usuario == 'supervisor':
                grupo.supervisor = request.user

            elif request.user.tipo_usuario == 'coordenador':
                if not grupo.supervisor:
                    return render(request, 'grupos/form.html', {
                        'form': form,
                        'titulo': 'Criar grupo',
                        'erro': 'Selecione um supervisor.',
                        'breadcrumbs': [
                            {'label': 'Dashboard', 'url': '/painel/'},
                            {'label': 'Grupos', 'url': reverse('lista_grupos')},
                            {'label': 'Criar grupo', 'url': ''},
                        ],
                        'page_actions': [
                            {'label': 'Voltar aos grupos', 'url': reverse('lista_grupos'), 'variant': 'secondary'},
                        ]
                    })

                if grupo.supervisor.coordenador_responsavel != request.user:
                    return render(request, 'core/sem_permissao.html')

            elif request.user.tipo_usuario == 'admin':
                if not grupo.supervisor:
                    return render(request, 'grupos/form.html', {
                        'form': form,
                        'titulo': 'Criar grupo',
                        'erro': 'Selecione um supervisor.',
                        'breadcrumbs': [
                            {'label': 'Dashboard', 'url': '/painel/'},
                            {'label': 'Grupos', 'url': reverse('lista_grupos')},
                            {'label': 'Criar grupo', 'url': ''},
                        ],
                        'page_actions': [
                            {'label': 'Voltar aos grupos', 'url': reverse('lista_grupos'), 'variant': 'secondary'},
                        ]
                    })

            if grupo.lider.supervisor_responsavel != grupo.supervisor:
                return render(request, 'grupos/form.html', {
                    'form': form,
                    'titulo': 'Criar grupo',
                    'erro': 'O líder selecionado não pertence ao supervisor escolhido.',
                    'breadcrumbs': [
                        {'label': 'Dashboard', 'url': '/painel/'},
                        {'label': 'Grupos', 'url': reverse('lista_grupos')},
                        {'label': 'Criar grupo', 'url': ''},
                    ],
                    'page_actions': [
                        {'label': 'Voltar aos grupos', 'url': reverse('lista_grupos'), 'variant': 'secondary'},
                    ]
                })

            grupo.save()
            return redirect('detalhe_grupo', grupo_id=grupo.id)
    else:
        form = GrupoForm(usuario_logado=request.user)

    context = {
        'form': form,
        'titulo': 'Criar grupo',
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': 'Criar grupo', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Voltar aos grupos', 'url': reverse('lista_grupos'), 'variant': 'secondary'},
        ]
    }
    return render(request, 'grupos/form.html', context)


@login_required
def editar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)

    if request.user.tipo_usuario not in ['admin', 'coordenador', 'supervisor']:
        return render(request, 'core/sem_permissao.html')

    if request.user.tipo_usuario == 'coordenador':
        if grupo.supervisor.coordenador_responsavel != request.user:
            return render(request, 'core/sem_permissao.html')

    if request.user.tipo_usuario == 'supervisor':
        if grupo.supervisor != request.user:
            return render(request, 'core/sem_permissao.html')

    if request.method == 'POST':
        form = GrupoForm(request.POST, instance=grupo, usuario_logado=request.user)
        if form.is_valid():
            grupo_editado = form.save(commit=False)

            if request.user.tipo_usuario == 'supervisor':
                grupo_editado.supervisor = request.user

            if grupo_editado.lider.supervisor_responsavel != grupo_editado.supervisor:
                return render(request, 'grupos/form.html', {
                    'form': form,
                    'grupo': grupo,
                    'titulo': 'Editar grupo',
                    'erro': 'O líder selecionado não pertence ao supervisor escolhido.',
                    'breadcrumbs': [
                        {'label': 'Dashboard', 'url': '/painel/'},
                        {'label': 'Grupos', 'url': reverse('lista_grupos')},
                        {'label': grupo.nome, 'url': reverse('detalhe_grupo', args=[grupo.id])},
                        {'label': 'Editar grupo', 'url': ''},
                    ],
                    'page_actions': [
                        {'label': 'Voltar ao grupo', 'url': reverse('detalhe_grupo', args=[grupo.id]), 'variant': 'secondary'},
                    ]
                })

            if request.user.tipo_usuario == 'coordenador':
                if grupo_editado.supervisor.coordenador_responsavel != request.user:
                    return render(request, 'core/sem_permissao.html')

            grupo_editado.save()
            return redirect('detalhe_grupo', grupo_id=grupo_editado.id)
    else:
        form = GrupoForm(instance=grupo, usuario_logado=request.user)

    context = {
        'form': form,
        'grupo': grupo,
        'titulo': 'Editar grupo',
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': grupo.nome, 'url': reverse('detalhe_grupo', args=[grupo.id])},
            {'label': 'Editar grupo', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Voltar ao grupo', 'url': reverse('detalhe_grupo', args=[grupo.id]), 'variant': 'secondary'},
        ]
    }
    return render(request, 'grupos/form.html', context)