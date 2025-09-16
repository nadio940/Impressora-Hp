from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from printers.models import Printer
from users.models import User


class AlertRule(models.Model):
    """Modelo para regras de alertas automáticos"""
    
    TRIGGER_TYPES = [
        ('supply_low', 'Suprimento Baixo'),
        ('supply_empty', 'Suprimento Vazio'),
        ('paper_jam', 'Atolamento de Papel'),
        ('printer_offline', 'Impressora Offline'),
        ('error_code', 'Código de Erro'),
        ('maintenance_due', 'Manutenção Vencida'),
        ('high_temperature', 'Temperatura Alta'),
        ('queue_full', 'Fila Cheia'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nome da Regra'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    
    trigger_type = models.CharField(
        max_length=30,
        choices=TRIGGER_TYPES,
        verbose_name='Tipo de Gatilho'
    )
    
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        verbose_name='Severidade'
    )
    
    # Condições
    threshold_value = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Valor Limite'
    )
    
    condition_operator = models.CharField(
        max_length=10,
        choices=[
            ('lt', 'Menor que'),
            ('lte', 'Menor ou igual'),
            ('gt', 'Maior que'),
            ('gte', 'Maior ou igual'),
            ('eq', 'Igual'),
            ('ne', 'Diferente'),
        ],
        default='lt',
        verbose_name='Operador'
    )
    
    # Configurações de notificação
    send_email = models.BooleanField(
        default=True,
        verbose_name='Enviar Email'
    )
    
    send_sms = models.BooleanField(
        default=False,
        verbose_name='Enviar SMS'
    )
    
    send_system_notification = models.BooleanField(
        default=True,
        verbose_name='Notificação no Sistema'
    )
    
    # Filtros
    printers = models.ManyToManyField(
        Printer,
        blank=True,
        related_name='alert_rules',
        verbose_name='Impressoras'
    )
    
    users_to_notify = models.ManyToManyField(
        User,
        blank=True,
        related_name='alert_subscriptions',
        verbose_name='Usuários para Notificar'
    )
    
    # Controle
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativa'
    )
    
    cooldown_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name='Tempo de Espera (minutos)'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizada em'
    )
    
    class Meta:
        verbose_name = 'Regra de Alerta'
        verbose_name_plural = 'Regras de Alertas'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"


class Alert(models.Model):
    """Modelo para alertas gerados"""
    
    STATUS_CHOICES = [
        ('new', 'Novo'),
        ('acknowledged', 'Reconhecido'),
        ('resolved', 'Resolvido'),
        ('escalated', 'Escalado'),
        ('closed', 'Fechado'),
    ]
    
    rule = models.ForeignKey(
        AlertRule,
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name='Regra'
    )
    
    printer = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name='Impressora'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    
    message = models.TextField(
        verbose_name='Mensagem'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Status'
    )
    
    severity = models.CharField(
        max_length=20,
        choices=AlertRule.SEVERITY_LEVELS,
        verbose_name='Severidade'
    )
    
    # Dados do contexto
    context_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Dados do Contexto'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    acknowledged_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Reconhecido em'
    )
    
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='acknowledged_alerts',
        verbose_name='Reconhecido por'
    )
    
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Resolvido em'
    )
    
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='resolved_alerts',
        verbose_name='Resolvido por'
    )
    
    resolution_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas da Resolução'
    )
    
    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['printer', '-created_at']),
            models.Index(fields=['severity', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.printer.name} ({self.get_status_display()})"


class NotificationLog(models.Model):
    """Modelo para log de notificações enviadas"""
    
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('system', 'Sistema'),
        ('webhook', 'Webhook'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('sent', 'Enviada'),
        ('failed', 'Falhou'),
        ('delivered', 'Entregue'),
    ]
    
    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Alerta'
    )
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_notifications',
        verbose_name='Destinatário'
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name='Tipo de Notificação'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    
    recipient_address = models.CharField(
        max_length=200,
        verbose_name='Endereço do Destinatário'
    )
    
    subject = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Assunto'
    )
    
    content = models.TextField(
        verbose_name='Conteúdo'
    )
    
    sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Enviada em'
    )
    
    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Entregue em'
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensagem de Erro'
    )
    
    attempts = models.PositiveIntegerField(
        default=0,
        verbose_name='Tentativas'
    )
    
    max_attempts = models.PositiveIntegerField(
        default=3,
        verbose_name='Máximo de Tentativas'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em'
    )
    
    class Meta:
        verbose_name = 'Log de Notificação'
        verbose_name_plural = 'Logs de Notificações'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} para {self.recipient.username} - {self.get_status_display()}"
