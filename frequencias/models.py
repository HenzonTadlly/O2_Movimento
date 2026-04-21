from django.db import models
from grupos.models import Grupo
from membros.models import Membro
from usuarios.models import Usuario


class Encontro(models.Model):
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name='encontros')
    data_encontro = models.DateField()
    observacao = models.TextField(blank=True, null=True)
    criado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('grupo', 'data_encontro')

    def __str__(self):
        return f"{self.grupo.nome} - {self.data_encontro}"


class Frequencia(models.Model):
    encontro = models.ForeignKey(Encontro, on_delete=models.CASCADE, related_name='frequencias')
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, related_name='frequencias')
    presente = models.BooleanField(default=False)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('encontro', 'membro')

    def __str__(self):
        return f"{self.membro.nome_completo} - {self.encontro.data_encontro}"