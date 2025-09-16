from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    """Modelo de usuário personalizado"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('technician', 'Técnico'),
        ('user', 'Usuário Comum'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Perfil'
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Departamento'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Telefone'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    is_ldap_user = models.BooleanField(
        default=False,
        verbose_name='Usuário LDAP'
    )
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['username']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_technician(self):
        return self.role in ['admin', 'technician']


class UserActivity(models.Model):
    """Log de atividades dos usuários"""
    
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('print', 'Impressão'),
        ('scan', 'Digitalização'),
        ('config', 'Configuração'),
        ('maintenance', 'Manutenção'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name='Usuário'
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Ação'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='Endereço IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name='User Agent'
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora'
    )
    
    class Meta:
        verbose_name = 'Atividade do Usuário'
        verbose_name_plural = 'Atividades dos Usuários'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp}"
