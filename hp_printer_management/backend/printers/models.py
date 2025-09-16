from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User


class Printer(models.Model):
    """Modelo para impressoras HP"""
    
    STATUS_CHOICES = [
        ('active', 'Ativa'),
        ('inactive', 'Inativa'),
        ('maintenance', 'Em Manutenção'),
        ('error', 'Com Erro'),
        ('offline', 'Offline'),
    ]
    
    TYPE_CHOICES = [
        ('laser', 'Laser'),
        ('inkjet', 'Jato de Tinta'),
        ('multifunction', 'Multifuncional'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nome da Impressora'
    )
    
    model = models.CharField(
        max_length=100,
        verbose_name='Modelo'
    )
    
    serial_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Número de Série'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='Endereço IP'
    )
    
    mac_address = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        verbose_name='Endereço MAC'
    )
    
    printer_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Tipo'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Localização'
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Departamento'
    )
    
    snmp_community = models.CharField(
        max_length=50,
        default='public',
        verbose_name='SNMP Community'
    )
    
    snmp_port = models.PositiveIntegerField(
        default=161,
        verbose_name='Porta SNMP'
    )
    
    # Configurações de capacidade
    paper_capacity = models.PositiveIntegerField(
        default=250,
        verbose_name='Capacidade de Papel'
    )
    
    supports_duplex = models.BooleanField(
        default=False,
        verbose_name='Suporte a Duplex'
    )
    
    supports_color = models.BooleanField(
        default=False,
        verbose_name='Suporte a Cores'
    )
    
    # Metadados
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizada em'
    )
    
    last_seen = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Última Conexão'
    )
    
    firmware_version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Versão do Firmware'
    )
    
    is_monitored = models.BooleanField(
        default=True,
        verbose_name='Monitorada'
    )
    
    class Meta:
        verbose_name = 'Impressora'
        verbose_name_plural = 'Impressoras'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.model}) - {self.ip_address}"
    
    @property
    def is_online(self):
        return self.status not in ['offline', 'error']


class PrinterSupplies(models.Model):
    """Modelo para suprimentos da impressora (toner, papel, etc.)"""
    
    SUPPLY_TYPES = [
        ('toner_black', 'Toner Preto'),
        ('toner_cyan', 'Toner Ciano'),
        ('toner_magenta', 'Toner Magenta'),
        ('toner_yellow', 'Toner Amarelo'),
        ('ink_black', 'Tinta Preta'),
        ('ink_cyan', 'Tinta Ciano'),
        ('ink_magenta', 'Tinta Magenta'),
        ('ink_yellow', 'Tinta Amarelo'),
        ('paper', 'Papel'),
        ('drum', 'Cilindro'),
        ('fuser', 'Fusor'),
    ]
    
    printer = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE,
        related_name='supplies',
        verbose_name='Impressora'
    )
    
    supply_type = models.CharField(
        max_length=20,
        choices=SUPPLY_TYPES,
        verbose_name='Tipo de Suprimento'
    )
    
    level = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Nível (%)'
    )
    
    max_capacity = models.PositiveIntegerField(
        verbose_name='Capacidade Máxima'
    )
    
    current_capacity = models.PositiveIntegerField(
        verbose_name='Capacidade Atual'
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('ok', 'Normal'),
            ('low', 'Baixo'),
            ('very_low', 'Muito Baixo'),
            ('empty', 'Vazio'),
            ('unknown', 'Desconhecido'),
        ],
        default='ok',
        verbose_name='Status'
    )
    
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )
    
    class Meta:
        verbose_name = 'Suprimento'
        verbose_name_plural = 'Suprimentos'
        unique_together = ['printer', 'supply_type']
        ordering = ['printer', 'supply_type']
    
    def __str__(self):
        return f"{self.printer.name} - {self.get_supply_type_display()}: {self.level}%"


class PrintJob(models.Model):
    """Modelo para trabalhos de impressão"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('printing', 'Imprimindo'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
        ('error', 'Erro'),
    ]
    
    printer = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE,
        related_name='print_jobs',
        verbose_name='Impressora'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='print_jobs',
        verbose_name='Usuário'
    )
    
    job_name = models.CharField(
        max_length=200,
        verbose_name='Nome do Trabalho'
    )
    
    pages = models.PositiveIntegerField(
        verbose_name='Número de Páginas'
    )
    
    copies = models.PositiveIntegerField(
        default=1,
        verbose_name='Número de Cópias'
    )
    
    is_color = models.BooleanField(
        default=False,
        verbose_name='Impressão Colorida'
    )
    
    is_duplex = models.BooleanField(
        default=False,
        verbose_name='Impressão Duplex'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Enviado em'
    )
    
    started_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Iniciado em'
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Concluído em'
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensagem de Erro'
    )
    
    class Meta:
        verbose_name = 'Trabalho de Impressão'
        verbose_name_plural = 'Trabalhos de Impressão'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.job_name} - {self.user.username} - {self.printer.name}"
    
    @property
    def total_pages(self):
        return self.pages * self.copies


class PrinterPermission(models.Model):
    """Modelo para permissões de usuários em impressoras"""
    
    PERMISSION_CHOICES = [
        ('print', 'Imprimir'),
        ('scan', 'Digitalizar'),
        ('configure', 'Configurar'),
        ('maintain', 'Manter'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='printer_permissions',
        verbose_name='Usuário'
    )
    
    printer = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE,
        related_name='user_permissions',
        verbose_name='Impressora'
    )
    
    permission = models.CharField(
        max_length=20,
        choices=PERMISSION_CHOICES,
        verbose_name='Permissão'
    )
    
    granted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='granted_permissions',
        verbose_name='Concedida por'
    )
    
    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Concedida em'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativa'
    )
    
    class Meta:
        verbose_name = 'Permissão de Impressora'
        verbose_name_plural = 'Permissões de Impressoras'
        unique_together = ['user', 'printer', 'permission']
        ordering = ['user', 'printer']
    
    def __str__(self):
        return f"{self.user.username} - {self.printer.name} - {self.get_permission_display()}"
