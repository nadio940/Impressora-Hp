from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from printers.models import Printer
from users.models import User


class PrinterStatus(models.Model):
    """Modelo para status detalhado das impressoras"""
    
    printer = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='Impressora'
    )
    
    # Status geral
    is_online = models.BooleanField(
        verbose_name='Online'
    )
    
    # Status do papel
    paper_status = models.CharField(
        max_length=20,
        choices=[
            ('ok', 'Normal'),
            ('low', 'Baixo'),
            ('empty', 'Vazio'),
            ('jam', 'Atolamento'),
            ('unknown', 'Desconhecido'),
        ],
        default='ok',
        verbose_name='Status do Papel'
    )
    
    paper_level = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=100,
        verbose_name='Nível de Papel (%)'
    )
    
    # Fila de impressão
    queue_size = models.PositiveIntegerField(
        default=0,
        verbose_name='Tamanho da Fila'
    )
    
    # Contadores
    total_pages_printed = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Páginas Impressas'
    )
    
    color_pages_printed = models.PositiveIntegerField(
        default=0,
        verbose_name='Páginas Coloridas Impressas'
    )
    
    # Temperatura e outros sensores
    temperature = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Temperatura (°C)'
    )
    
    humidity = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Umidade (%)'
    )
    
    # Erros e avisos
    error_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Código de Erro'
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensagem de Erro'
    )
    
    warning_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensagem de Aviso'
    )
    
    # Metadados
    recorded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Registrado em'
    )
    
    response_time = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Tempo de Resposta (ms)'
    )
    
    class Meta:
        verbose_name = 'Status da Impressora'
        verbose_name_plural = 'Status das Impressoras'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['printer', '-recorded_at']),
            models.Index(fields=['-recorded_at']),
        ]
    
    def __str__(self):
        status = "Online" if self.is_online else "Offline"
        return f"{self.printer.name} - {status} - {self.recorded_at}"


class MaintenanceRecord(models.Model):
    """Modelo para registros de manutenção"""
    
    MAINTENANCE_TYPES = [
        ('preventive', 'Preventiva'),
        ('corrective', 'Corretiva'),
        ('cleaning', 'Limpeza'),
        ('calibration', 'Calibração'),
        ('repair', 'Reparo'),
        ('upgrade', 'Atualização'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Agendada'),
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
        ('postponed', 'Adiada'),
    ]
    
    printer = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE,
        related_name='maintenance_records',
        verbose_name='Impressora'
    )
    
    technician = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='maintenance_performed',
        verbose_name='Técnico'
    )
    
    maintenance_type = models.CharField(
        max_length=20,
        choices=MAINTENANCE_TYPES,
        verbose_name='Tipo de Manutenção'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Status'
    )
    
    scheduled_date = models.DateTimeField(
        verbose_name='Data Agendada'
    )
    
    started_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Iniciada em'
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Concluída em'
    )
    
    description = models.TextField(
        verbose_name='Descrição'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    parts_replaced = models.TextField(
        blank=True,
        null=True,
        verbose_name='Peças Substituídas'
    )
    
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Custo'
    )
    
    next_maintenance_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Próxima Manutenção'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    class Meta:
        verbose_name = 'Registro de Manutenção'
        verbose_name_plural = 'Registros de Manutenção'
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.printer.name} - {self.get_maintenance_type_display()} - {self.scheduled_date}"


class PerformanceMetric(models.Model):
    """Modelo para métricas de performance das impressoras"""
    
    printer = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE,
        related_name='performance_metrics',
        verbose_name='Impressora'
    )
    
    # Métricas de uso
    pages_per_minute = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Páginas por Minuto'
    )
    
    uptime_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Tempo de Atividade (%)'
    )
    
    error_rate = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        verbose_name='Taxa de Erro (%)'
    )
    
    # Métricas de qualidade
    print_quality_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        blank=True,
        null=True,
        verbose_name='Pontuação de Qualidade'
    )
    
    # Métricas de consumo
    toner_efficiency = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Eficiência do Toner'
    )
    
    paper_jam_rate = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        verbose_name='Taxa de Atolamento (%)'
    )
    
    # Período de medição
    measurement_period_start = models.DateTimeField(
        verbose_name='Início do Período'
    )
    
    measurement_period_end = models.DateTimeField(
        verbose_name='Fim do Período'
    )
    
    recorded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Registrado em'
    )
    
    class Meta:
        verbose_name = 'Métrica de Performance'
        verbose_name_plural = 'Métricas de Performance'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['printer', '-recorded_at']),
        ]
    
    def __str__(self):
        return f"{self.printer.name} - {self.measurement_period_start} to {self.measurement_period_end}"


class MonitoringTask(models.Model):
    """Modelo para tarefas de monitoramento agendadas"""
    
    TASK_TYPES = [
        ('status_check', 'Verificação de Status'),
        ('supply_check', 'Verificação de Suprimentos'),
        ('performance_analysis', 'Análise de Performance'),
        ('maintenance_reminder', 'Lembrete de Manutenção'),
        ('health_check', 'Verificação de Saúde'),
    ]
    
    printer = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE,
        related_name='monitoring_tasks',
        verbose_name='Impressora'
    )
    
    task_type = models.CharField(
        max_length=30,
        choices=TASK_TYPES,
        verbose_name='Tipo de Tarefa'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativa'
    )
    
    interval_minutes = models.PositiveIntegerField(
        verbose_name='Intervalo (minutos)'
    )
    
    last_run = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Última Execução'
    )
    
    next_run = models.DateTimeField(
        verbose_name='Próxima Execução'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em'
    )
    
    class Meta:
        verbose_name = 'Tarefa de Monitoramento'
        verbose_name_plural = 'Tarefas de Monitoramento'
        ordering = ['next_run']
    
    def __str__(self):
        return f"{self.printer.name} - {self.get_task_type_display()}"
