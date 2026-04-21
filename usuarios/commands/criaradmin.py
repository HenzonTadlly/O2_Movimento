from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Cria um superusuário inicial se ele ainda não existir"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        username = os.environ.get("ADMIN_USERNAME", "admin")
        email = os.environ.get("ADMIN_EMAIL", "admin@admin.com")
        password = os.environ.get("ADMIN_PASSWORD", "Admin123456!")
        tipo_usuario = "admin"

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING("Superusuário já existe."))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            tipo_usuario=tipo_usuario,
            ativo=True,
        )

        self.stdout.write(self.style.SUCCESS("Superusuário criado com sucesso."))