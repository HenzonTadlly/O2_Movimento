from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from grupos.models import Grupo
from escolas.models import Escola


telefone_validator = RegexValidator(
    regex=r'^\(\d{2}\)\s\d{4,5}-\d{4}$',
    message='Digite o telefone no formato (99) 99999-9999 ou (99) 9999-9999.'
)


class Membro(models.Model):
    nome_completo = models.CharField(max_length=150)
    telefone = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        validators=[telefone_validator]
    )
    idade = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)]
    )
    escola = models.ForeignKey(Escola, on_delete=models.SET_NULL, null=True, blank=True)
    ano_escolar = models.CharField(max_length=50)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name='membros')
    ativo = models.BooleanField(default=True)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome_completo