from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Q
from django.urls import reverse
from grupos.models import Grupo
from membros.models import Membro
from frequencias.models import Encontro, Frequencia


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
def relatorio_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo.objects.select_related('escola', 'lider', 'supervisor'), id=grupo_id)

    if not grupo_permitido(request.user, grupo):
        return render(request, 'core/sem_permissao.html')

    encontros = Encontro.objects.filter(grupo=grupo).order_by('-data_encontro')
    membros = Membro.objects.filter(grupo=grupo).order_by('nome_completo')

    total_encontros = encontros.count()
    total_membros = membros.count()

    frequencias = Frequencia.objects.filter(encontro__grupo=grupo)

    total_presencas = frequencias.filter(presente=True).count()
    total_registros = frequencias.count()
    media_presenca = 0
    if total_registros > 0:
        media_presenca = round((total_presencas / total_registros) * 100, 1)

    membros_resumo = membros.annotate(
        total_presencas=Count('frequencias', filter=Q(frequencias__presente=True)),
        total_faltas=Count('frequencias', filter=Q(frequencias__presente=False)),
        total_registros=Count('frequencias')
    )

    membros_dados = []
    for membro in membros_resumo:
        percentual = 0
        if membro.total_registros > 0:
            percentual = round((membro.total_presencas / membro.total_registros) * 100, 1)

        membros_dados.append({
            'obj': membro,
            'total_presencas': membro.total_presencas,
            'total_faltas': membro.total_faltas,
            'total_registros': membro.total_registros,
            'percentual': percentual,
        })

    membros_dados = sorted(membros_dados, key=lambda x: (x['percentual'], -x['total_faltas']))

    context = {
        'grupo': grupo,
        'encontros': encontros[:10],
        'total_encontros': total_encontros,
        'total_membros': total_membros,
        'total_presencas': total_presencas,
        'media_presenca': media_presenca,
        'membros_dados': membros_dados,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': '/painel/'},
            {'label': 'Grupos', 'url': reverse('lista_grupos')},
            {'label': grupo.nome, 'url': reverse('detalhe_grupo', args=[grupo.id])},
            {'label': 'Relatório', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Voltar ao grupo', 'url': reverse('detalhe_grupo', args=[grupo.id]), 'variant': 'secondary'},
            {'label': 'Ver encontros', 'url': reverse('lista_encontros', args=[grupo.id]), 'variant': 'secondary'},
        ]
    }
    return render(request, 'relatorios/relatorio_grupo.html', context)