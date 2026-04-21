from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


telefone_validator = RegexValidator(
    regex=r'^\(\d{2}\)\s\d{4,5}-\d{4}$',
    message='Digite o telefone no formato (99) 99999-9999 ou (99) 9999-9999.'
)


class Usuario(AbstractUser):
    TIPOS_USUARIO = (
        ('admin', 'Admin'),
        ('coordenador', 'Coordenador'),
        ('supervisor', 'Supervisor'),
        ('lider', 'Líder'),
    )

    tipo_usuario = models.CharField(max_length=20, choices=TIPOS_USUARIO)
    telefone = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        validators=[telefone_validator]
    )
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    ativo = models.BooleanField(default=True)

    coordenador_responsavel = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervisores_vinculados',
        limit_choices_to={'tipo_usuario': 'coordenador'}
    )

    supervisor_responsavel = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lideres_vinculados',
        limit_choices_to={'tipo_usuario': 'supervisor'}
    )

    def __str__(self):
        return f"{self.get_full_name() or self.username} - {self.tipo_usuario}"