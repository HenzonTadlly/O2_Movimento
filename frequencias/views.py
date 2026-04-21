from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from grupos.models import Grupo
from .forms import LancarFrequenciaForm
from .models import Encontro, Frequencia


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
def lancar_frequencia(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    usuario = request.user

    if not usuario_pode_acessar_grupo(usuario, grupo):
        messages.error(request, 'Sem permissão para lançar frequência neste grupo.')
        return render(request, 'core/sem_permissao.html')

    membros = grupo.membros.filter(ativo=True).order_by('nome_completo')
    erro = None

    if request.method == 'POST':
        form = LancarFrequenciaForm(request.POST)
        if form.is_valid():
            data_encontro = form.cleaned_data['data_encontro']
            observacao = form.cleaned_data['observacao']

            encontro_existente = Encontro.objects.filter(
                grupo=grupo,
                data_encontro=data_encontro
            ).first()

            if encontro_existente:
                erro = 'Já existe uma frequência lançada para este grupo nessa data.'
                messages.error(request, erro)
            else:
                encontro = Encontro.objects.create(
                    grupo=grupo,
                    data_encontro=data_encontro,
                    observacao=observacao,
                    criado_por=usuario
                )

                presentes_ids = request.POST.getlist('presentes')

                for membro in membros:
                    Frequencia.objects.create(
                        encontro=encontro,
                        membro=membro,
                        presente=str(membro.id) in presentes_ids
                    )

                messages.success(request, 'Frequência lançada com sucesso.')
                return redirect('detalhe_encontro', encontro_id=encontro.id)
        else:
            messages.error(request, 'Não foi possível lançar a frequência. Verifique os campos.')
    else:
        form = LancarFrequenciaForm()

    context = {
        'grupo': grupo,
        'membros': membros,
        'form': form,
        'erro': erro,
        'modo_edicao': False,
        'presentes_marcados': [],
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': grupo.nome, 'url': reverse('detalhe_grupo', args=[grupo.id])},
            {'label': 'Nova frequência', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Voltar ao grupo', 'url': reverse('detalhe_grupo', args=[grupo.id]), 'variant': 'secondary'},
        ]
    }
    return render(request, 'frequencias/form.html', context)


@login_required
def editar_frequencia(request, encontro_id):
    encontro = get_object_or_404(Encontro, id=encontro_id)
    grupo = encontro.grupo
    usuario = request.user

    if not usuario_pode_acessar_grupo(usuario, grupo):
        messages.error(request, 'Sem permissão para editar esta frequência.')
        return render(request, 'core/sem_permissao.html')

    membros = grupo.membros.filter(ativo=True).order_by('nome_completo')
    erro = None

    if request.method == 'POST':
        form = LancarFrequenciaForm(request.POST)
        if form.is_valid():
            data_encontro = form.cleaned_data['data_encontro']
            observacao = form.cleaned_data['observacao']

            encontro_com_mesma_data = Encontro.objects.filter(
                grupo=grupo,
                data_encontro=data_encontro
            ).exclude(id=encontro.id).first()

            if encontro_com_mesma_data:
                erro = 'Já existe outra frequência lançada para este grupo nessa data.'
                messages.error(request, erro)
            else:
                encontro.data_encontro = data_encontro
                encontro.observacao = observacao
                encontro.save()

                presentes_ids = request.POST.getlist('presentes')

                for membro in membros:
                    freq, _ = Frequencia.objects.get_or_create(
                        encontro=encontro,
                        membro=membro,
                        defaults={'presente': False}
                    )
                    freq.presente = str(membro.id) in presentes_ids
                    freq.save()

                messages.success(request, 'Frequência editada com sucesso.')
                return redirect('detalhe_encontro', encontro_id=encontro.id)
        else:
            messages.error(request, 'Não foi possível editar a frequência. Verifique os campos.')
    else:
        form = LancarFrequenciaForm(initial={
            'data_encontro': encontro.data_encontro,
            'observacao': encontro.observacao,
        })

    presentes_marcados = list(
        encontro.frequencias.filter(presente=True).values_list('membro_id', flat=True)
    )

    context = {
        'grupo': grupo,
        'encontro': encontro,
        'membros': membros,
        'form': form,
        'erro': erro,
        'modo_edicao': True,
        'presentes_marcados': presentes_marcados,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': grupo.nome, 'url': reverse('detalhe_grupo', args=[grupo.id])},
            {'label': 'Encontros', 'url': reverse('lista_encontros', args=[grupo.id])},
            {'label': f'Editar {encontro.data_encontro}', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Voltar ao encontro', 'url': reverse('detalhe_encontro', args=[encontro.id]), 'variant': 'secondary'},
        ]
    }
    return render(request, 'frequencias/form.html', context)


@login_required
def excluir_frequencia(request, encontro_id):
    encontro = get_object_or_404(Encontro, id=encontro_id)
    grupo = encontro.grupo

    if not usuario_pode_acessar_grupo(request.user, grupo):
        messages.error(request, 'Sem permissão para excluir esta frequência.')
        return render(request, 'core/sem_permissao.html')

    total_frequencias = encontro.frequencias.count()

    if request.method == 'POST':
        grupo_id = grupo.id
        encontro.delete()
        messages.success(request, 'Frequência excluída com sucesso.')
        return redirect('lista_encontros', grupo_id=grupo_id)

    context = {
        'encontro': encontro,
        'grupo': grupo,
        'total_frequencias': total_frequencias,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': grupo.nome, 'url': reverse('detalhe_grupo', args=[grupo.id])},
            {'label': 'Encontros', 'url': reverse('lista_encontros', args=[grupo.id])},
            {'label': str(encontro.data_encontro), 'url': reverse('detalhe_encontro', args=[encontro.id])},
            {'label': 'Excluir frequência', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Cancelar', 'url': reverse('detalhe_encontro', args=[encontro.id]), 'variant': 'secondary'},
        ]
    }
    return render(request, 'frequencias/confirmar_exclusao.html', context)


@login_required
def lista_encontros(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)

    if not usuario_pode_acessar_grupo(request.user, grupo):
        messages.error(request, 'Sem permissão para acessar os encontros deste grupo.')
        return render(request, 'core/sem_permissao.html')

    encontros = grupo.encontros.all().order_by('-data_encontro')

    context = {
        'grupo': grupo,
        'encontros': encontros,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': grupo.nome, 'url': reverse('detalhe_grupo', args=[grupo.id])},
            {'label': 'Encontros', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Lançar nova frequência', 'url': reverse('lancar_frequencia', args=[grupo.id]), 'variant': 'primary'},
            {'label': 'Voltar ao grupo', 'url': reverse('detalhe_grupo', args=[grupo.id]), 'variant': 'secondary'},
        ]
    }
    return render(request, 'frequencias/lista_encontros.html', context)


@login_required
def detalhe_encontro(request, encontro_id):
    encontro = get_object_or_404(Encontro, id=encontro_id)
    grupo = encontro.grupo

    if not usuario_pode_acessar_grupo(request.user, grupo):
        messages.error(request, 'Sem permissão para acessar este encontro.')
        return render(request, 'core/sem_permissao.html')

    frequencias = encontro.frequencias.select_related('membro').order_by('membro__nome_completo')
    total_presentes = frequencias.filter(presente=True).count()
    total_ausentes = frequencias.filter(presente=False).count()

    page_actions = [
        {'label': 'Editar frequência', 'url': reverse('editar_frequencia', args=[encontro.id]), 'variant': 'primary'},
        {'label': 'Excluir frequência', 'url': reverse('excluir_frequencia', args=[encontro.id]), 'variant': 'secondary'},
        {'label': 'Voltar para encontros', 'url': reverse('lista_encontros', args=[grupo.id]), 'variant': 'secondary'},
    ]

    context = {
        'encontro': encontro,
        'grupo': grupo,
        'frequencias': frequencias,
        'total_presentes': total_presentes,
        'total_ausentes': total_ausentes,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': grupo.nome, 'url': reverse('detalhe_grupo', args=[grupo.id])},
            {'label': 'Encontros', 'url': reverse('lista_encontros', args=[grupo.id])},
            {'label': str(encontro.data_encontro), 'url': ''},
        ],
        'page_actions': page_actions,
    }
    return render(request, 'frequencias/detalhe_encontro.html', context)