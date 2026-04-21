from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from grupos.models import Grupo
from .forms import MembroForm
from .models import Membro


def usuario_pode_acessar_grupo(usuario, grupo):
    if usuario.tipo_usuario == 'admin':
        return True

    if usuario.tipo_usuario == 'coordenador':
        return (
            grupo.supervisor and
            grupo.supervisor.coordenador_responsavel == usuario and
            grupo.lider and
            grupo.lider.supervisor_responsavel == grupo.supervisor
        )

    if usuario.tipo_usuario == 'supervisor' and grupo.supervisor == usuario:
        return True

    if usuario.tipo_usuario == 'lider' and grupo.lider == usuario:
        return True

    return False


@login_required
def lista_membros(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)

    if not usuario_pode_acessar_grupo(request.user, grupo):
        return render(request, 'core/sem_permissao.html')

    membros = grupo.membros.all().order_by('nome_completo')

    busca = request.GET.get('busca', '').strip()
    status = request.GET.get('status', '').strip()

    if busca:
        membros = membros.filter(nome_completo__icontains=busca)

    if status == 'ativos':
        membros = membros.filter(ativo=True)
    elif status == 'inativos':
        membros = membros.filter(ativo=False)

    paginator = Paginator(membros, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    context = {
        'grupo': grupo,
        'membros': page_obj,
        'page_obj': page_obj,
        'querystring': querystring,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': grupo.nome, 'url': reverse('detalhe_grupo', args=[grupo.id])},
            {'label': 'Membros', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Cadastrar membro', 'url': reverse('cadastrar_membro', args=[grupo.id]), 'variant': 'primary'},
            {'label': 'Voltar ao grupo', 'url': reverse('detalhe_grupo', args=[grupo.id]), 'variant': 'secondary'},
        ],
        'filtros': {
            'busca': busca,
            'status': status,
        }
    }
    return render(request, 'membros/lista.html', context)


@login_required
def cadastrar_membro(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)

    if not usuario_pode_acessar_grupo(request.user, grupo):
        return render(request, 'core/sem_permissao.html')

    if request.method == 'POST':
        form = MembroForm(request.POST)
        if form.is_valid():
            membro = form.save(commit=False)
            membro.grupo = grupo

            if not membro.escola:
                membro.escola = grupo.escola

            membro.save()
            return redirect('lista_membros', grupo_id=grupo.id)
    else:
        form = MembroForm(initial={'escola': grupo.escola})

    context = {
        'grupo': grupo,
        'form': form,
        'titulo': 'Cadastrar membro',
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': grupo.nome, 'url': reverse('detalhe_grupo', args=[grupo.id])},
            {'label': 'Membros', 'url': reverse('lista_membros', args=[grupo.id])},
            {'label': 'Cadastrar membro', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Voltar aos membros', 'url': reverse('lista_membros', args=[grupo.id]), 'variant': 'secondary'},
        ]
    }
    return render(request, 'membros/form.html', context)


@login_required
def detalhe_membro(request, membro_id):
    membro = get_object_or_404(Membro, id=membro_id)
    grupo = membro.grupo

    if not usuario_pode_acessar_grupo(request.user, grupo):
        return render(request, 'core/sem_permissao.html')

    frequencias = membro.frequencias.select_related('encontro').order_by('-encontro__data_encontro')

    total_registros = frequencias.count()
    total_presencas = frequencias.filter(presente=True).count()
    total_faltas = frequencias.filter(presente=False).count()
    percentual_presenca = 0

    if total_registros > 0:
        percentual_presenca = round((total_presencas / total_registros) * 100, 1)

    context = {
        'membro': membro,
        'grupo': grupo,
        'frequencias': frequencias,
        'total_registros': total_registros,
        'total_presencas': total_presencas,
        'total_faltas': total_faltas,
        'percentual_presenca': percentual_presenca,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': grupo.nome, 'url': reverse('detalhe_grupo', args=[grupo.id])},
            {'label': 'Membros', 'url': reverse('lista_membros', args=[grupo.id])},
            {'label': membro.nome_completo, 'url': ''},
        ],
        'page_actions': [
            {'label': 'Editar membro', 'url': reverse('editar_membro', args=[membro.id]), 'variant': 'primary'},
            {'label': 'Voltar aos membros', 'url': reverse('lista_membros', args=[grupo.id]), 'variant': 'secondary'},
        ]
    }
    return render(request, 'membros/detalhe.html', context)


@login_required
def editar_membro(request, membro_id):
    membro = get_object_or_404(Membro, id=membro_id)
    grupo = membro.grupo

    if not usuario_pode_acessar_grupo(request.user, grupo):
        return render(request, 'core/sem_permissao.html')

    if request.method == 'POST':
        form = MembroForm(request.POST, instance=membro)
        if form.is_valid():
            form.save()
            return redirect('detalhe_membro', membro_id=membro.id)
    else:
        form = MembroForm(instance=membro)

    context = {
        'grupo': grupo,
        'form': form,
        'membro': membro,
        'titulo': 'Editar membro',
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': grupo.nome, 'url': reverse('detalhe_grupo', args=[grupo.id])},
            {'label': 'Membros', 'url': reverse('lista_membros', args=[grupo.id])},
            {'label': membro.nome_completo, 'url': reverse('detalhe_membro', args=[membro.id])},
            {'label': 'Editar', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Voltar ao perfil', 'url': reverse('detalhe_membro', args=[membro.id]), 'variant': 'secondary'},
        ]
    }
    return render(request, 'membros/form.html', context)