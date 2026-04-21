from django.db import models
from usuarios.models import Usuario
from escolas.models import Escola


class Grupo(models.Model):
    STATUS_CHOICES = (
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('multiplicado', 'Multiplicado'),
    )

    nome = models.CharField(max_length=150)
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name='grupos')
    lider = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='grupos_liderados',
        limit_choices_to={'tipo_usuario': 'lider'}
    )
    supervisor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='grupos_supervisionados',
        limit_choices_to={'tipo_usuario': 'supervisor'}
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')
    descricao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome