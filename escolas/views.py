from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Escola
from .forms import EscolaForm
from grupos.models import Grupo
from membros.models import Membro


@login_required
def lista_escolas(request):
    if request.user.tipo_usuario not in ['admin', 'coordenador', 'supervisor']:
        return render(request, 'core/sem_permissao.html')

    escolas = Escola.objects.all().order_by('nome')

    busca = request.GET.get('busca', '').strip()
    status = request.GET.get('status', '').strip()

    if busca:
        escolas = escolas.filter(nome__icontains=busca)

    if status == 'ativas':
        escolas = escolas.filter(ativa=True)
    elif status == 'inativas':
        escolas = escolas.filter(ativa=False)

    paginator = Paginator(escolas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    page_actions = []
    if request.user.tipo_usuario in ['admin', 'coordenador', 'supervisor']:
        page_actions.append({
            'label': 'Cadastrar escola',
            'url': reverse('criar_escola'),
            'variant': 'primary'
        })

    context = {
        'escolas': page_obj,
        'page_obj': page_obj,
        'querystring': querystring,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Escolas', 'url': ''},
        ],
        'page_actions': page_actions,
        'filtros': {
            'busca': busca,
            'status': status,
        }
    }
    return render(request, 'escolas/lista.html', context)


@login_required
def detalhe_escola(request, escola_id):
    if request.user.tipo_usuario not in ['admin', 'coordenador', 'supervisor']:
        return render(request, 'core/sem_permissao.html')

    escola = get_object_or_404(Escola, id=escola_id)
    grupos = Grupo.objects.filter(escola=escola).select_related('lider', 'supervisor').order_by('nome')
    total_membros = Membro.objects.filter(escola=escola).count()

    if request.user.tipo_usuario == 'coordenador':
        grupos = grupos.filter(
            supervisor__coordenador_responsavel=request.user,
            lider__supervisor_responsavel__coordenador_responsavel=request.user
        ).distinct()
        total_membros = Membro.objects.filter(
            escola=escola,
            grupo__supervisor__coordenador_responsavel=request.user,
            grupo__lider__supervisor_responsavel__coordenador_responsavel=request.user
        ).distinct().count()

    if request.user.tipo_usuario == 'supervisor':
        grupos = grupos.filter(
            supervisor=request.user,
            lider__supervisor_responsavel=request.user
        ).distinct()
        total_membros = Membro.objects.filter(
            escola=escola,
            grupo__supervisor=request.user,
            grupo__lider__supervisor_responsavel=request.user
        ).distinct().count()

    page_actions = []
    if request.user.tipo_usuario in ['admin', 'coordenador', 'supervisor']:
        page_actions.append({
            'label': 'Editar escola',
            'url': reverse('editar_escola', args=[escola.id]),
            'variant': 'primary'
        })

    context = {
        'escola': escola,
        'grupos': grupos,
        'total_grupos': grupos.count(),
        'total_membros': total_membros,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Escolas', 'url': reverse('lista_escolas')},
            {'label': escola.nome, 'url': ''},
        ],
        'page_actions': page_actions,
    }
    return render(request, 'escolas/detalhe.html', context)


@login_required
def criar_escola(request):
    if request.user.tipo_usuario not in ['admin', 'coordenador', 'supervisor']:
        return render(request, 'core/sem_permissao.html')

    if request.method == 'POST':
        form = EscolaForm(request.POST)
        if form.is_valid():
            escola = form.save()
            return redirect('detalhe_escola', escola_id=escola.id)
    else:
        form = EscolaForm()

    context = {
        'form': form,
        'titulo': 'Cadastrar escola',
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Escolas', 'url': reverse('lista_escolas')},
            {'label': 'Cadastrar escola', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Voltar às escolas', 'url': reverse('lista_escolas'), 'variant': 'secondary'},
        ]
    }
    return render(request, 'escolas/form.html', context)


@login_required
def editar_escola(request, escola_id):
    if request.user.tipo_usuario not in ['admin', 'coordenador', 'supervisor']:
        return render(request, 'core/sem_permissao.html')

    escola = get_object_or_404(Escola, id=escola_id)

    if request.method == 'POST':
        form = EscolaForm(request.POST, instance=escola)
        if form.is_valid():
            escola = form.save()
            return redirect('detalhe_escola', escola_id=escola.id)
    else:
        form = EscolaForm(instance=escola)

    context = {
        'form': form,
        'titulo': 'Editar escola',
        'escola': escola,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Escolas', 'url': reverse('lista_escolas')},
            {'label': escola.nome, 'url': reverse('detalhe_escola', args=[escola.id])},
            {'label': 'Editar escola', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Voltar à escola', 'url': reverse('detalhe_escola', args=[escola.id]), 'variant': 'secondary'},
        ]
    }
    return render(request, 'escolas/form.html', context)