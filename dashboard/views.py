from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Q
from django.urls import reverse

from grupos.models import Grupo
from membros.models import Membro
from escolas.models import Escola
from usuarios.models import Usuario
from frequencias.models import Frequencia


@login_required
def dashboard_admin(request):
    total_coordenadores = Usuario.objects.filter(tipo_usuario='coordenador').count()
    total_supervisores = Usuario.objects.filter(tipo_usuario='supervisor').count()
    total_lideres = Usuario.objects.filter(tipo_usuario='lider').count()
    total_escolas = Escola.objects.count()
    total_grupos = Grupo.objects.count()
    total_membros = Membro.objects.count()

    total_frequencias = Frequencia.objects.count()
    total_presencas = Frequencia.objects.filter(presente=True).count()
    media_presenca = 0
    if total_frequencias > 0:
        media_presenca = round((total_presencas / total_frequencias) * 100, 1)

    grupos_baixa_presenca = (
        Grupo.objects.annotate(
            total_freq=Count('encontros__frequencias'),
            presencas=Count('encontros__frequencias', filter=Q(encontros__frequencias__presente=True))
        )
        .order_by('nome')
    )

    grupos_alerta = []
    for grupo in grupos_baixa_presenca:
        percentual = 0
        if grupo.total_freq > 0:
            percentual = round((grupo.presencas / grupo.total_freq) * 100, 1)
        if grupo.total_freq > 0 and percentual < 70:
            grupos_alerta.append({'grupo': grupo, 'percentual': percentual})

    context = {
        'total_coordenadores': total_coordenadores,
        'total_supervisores': total_supervisores,
        'total_lideres': total_lideres,
        'total_escolas': total_escolas,
        'total_grupos': total_grupos,
        'total_membros': total_membros,
        'media_presenca': media_presenca,
        'grupos_alerta': grupos_alerta[:5],
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Ver coordenadores', 'url': reverse('lista_coordenadores'), 'variant': 'secondary'},
            {'label': 'Ver escolas', 'url': reverse('lista_escolas'), 'variant': 'secondary'},
            {'label': 'Criar grupo', 'url': reverse('criar_grupo'), 'variant': 'primary'},
        ]
    }
    return render(request, 'dashboard/admin.html', context)


@login_required
def dashboard_coordenador(request):
    coordenador = request.user

    supervisores = Usuario.objects.filter(
        tipo_usuario='supervisor',
        coordenador_responsavel=coordenador
    )

    lideres = Usuario.objects.filter(
        tipo_usuario='lider',
        supervisor_responsavel__coordenador_responsavel=coordenador
    )

    grupos = Grupo.objects.filter(
        supervisor__coordenador_responsavel=coordenador,
        lider__supervisor_responsavel__coordenador_responsavel=coordenador
    ).select_related('escola', 'lider', 'supervisor').distinct()

    membros = Membro.objects.filter(
        grupo__in=grupos
    )

    frequencias = Frequencia.objects.filter(
        encontro__grupo__in=grupos
    )

    total_frequencias = frequencias.count()
    total_presencas = frequencias.filter(presente=True).count()
    media_presenca = 0
    if total_frequencias > 0:
        media_presenca = round((total_presencas / total_frequencias) * 100, 1)

    context = {
        'total_supervisores': supervisores.count(),
        'total_lideres': lideres.count(),
        'total_grupos': grupos.count(),
        'total_membros': membros.count(),
        'media_presenca': media_presenca,
        'grupos': grupos[:10],
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Ver supervisores', 'url': reverse('lista_supervisores'), 'variant': 'secondary'},
            {'label': 'Ver líderes', 'url': reverse('lista_lideres'), 'variant': 'secondary'},
            {'label': 'Criar grupo', 'url': reverse('criar_grupo'), 'variant': 'primary'},
        ]
    }
    return render(request, 'dashboard/coordenador.html', context)


@login_required
def dashboard_supervisor(request):
    supervisor = request.user

    grupos = Grupo.objects.filter(
        supervisor=supervisor,
        lider__supervisor_responsavel=supervisor
    ).select_related('escola', 'lider', 'supervisor').distinct()

    lideres_ids = grupos.values_list('lider_id', flat=True).distinct()
    membros = Membro.objects.filter(grupo__in=grupos)
    frequencias = Frequencia.objects.filter(encontro__grupo__in=grupos)

    total_frequencias = frequencias.count()
    total_presencas = frequencias.filter(presente=True).count()
    media_presenca = 0
    if total_frequencias > 0:
        media_presenca = round((total_presencas / total_frequencias) * 100, 1)

    context = {
        'total_lideres': Usuario.objects.filter(id__in=lideres_ids).count(),
        'total_grupos': grupos.count(),
        'total_membros': membros.count(),
        'media_presenca': media_presenca,
        'grupos': grupos,
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Ver grupos', 'url': reverse('lista_grupos'), 'variant': 'secondary'},
            {'label': 'Ver líderes', 'url': reverse('lista_lideres'), 'variant': 'secondary'},
            {'label': 'Criar grupo', 'url': reverse('criar_grupo'), 'variant': 'primary'},
        ]
    }
    return render(request, 'dashboard/supervisor.html', context)


@login_required
def dashboard_lider(request):
    lider = request.user
    grupos = Grupo.objects.filter(lider=lider).select_related('escola', 'supervisor')
    membros = Membro.objects.filter(grupo__lider=lider)
    frequencias = Frequencia.objects.filter(encontro__grupo__lider=lider)

    total_frequencias = frequencias.count()
    total_presencas = frequencias.filter(presente=True).count()
    media_presenca = 0
    if total_frequencias > 0:
        media_presenca = round((total_presencas / total_frequencias) * 100, 1)

    context = {
        'total_grupos': grupos.count(),
        'total_membros': membros.count(),
        'media_presenca': media_presenca,
        'grupos': grupos,
        'membros': membros[:10],
        'breadcrumbs': [
            {'label': 'Dashboard', 'url': ''},
        ],
        'page_actions': [
            {'label': 'Ver meus grupos', 'url': reverse('lista_grupos'), 'variant': 'secondary'},
            {'label': 'Meu perfil', 'url': reverse('meu_perfil'), 'variant': 'primary'},
        ]
    }
    return render(request, 'dashboard/lider.html', context)