from django.db import models


class Escola(models.Model):
    nome = models.CharField(max_length=150)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    ativa = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome