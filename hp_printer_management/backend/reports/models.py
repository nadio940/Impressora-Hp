from django.db import models
from django.contrib.auth import get_user_model
from printers.models import Printer
from django.core.validators import MinValueValidator

User = get_user_model()


class Report(models.Model):
    """Modelo para relatórios gerados"""
    
    REPORT_TYPES = [
        ('consumption', 'Consumo de Suprimentos'),
        ('usage', 'Uso por Impressora'),
        ('user_activity', 'Atividade por Usuário'),
        ('maintenance', 'Manutenção'),
        ('performance', 'Performance'),
        ('cost_analysis', 'Análise de Custos'),
        ('alert_summary', 'Resumo de Alertas'),
    ]
    
    STATUS_CHOICES = [
        ('generating', 'Gerando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
        ('scheduled', 'Agendado'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nome do Relatório'
    )
    
    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPES,
        verbose_name='Tipo de Relatório'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='generating',
        verbose_name='Status'
    )
    
    format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default='pdf',
        verbose_name='Formato'
    )
    
    # Filtros e parâmetros
    date_from = models.DateField(
        verbose_name='Data Início'
    )
    
    date_to = models.DateField(
        verbose_name='Data Fim'
    )
    
    printers = models.ManyToManyField(
        Printer,
        blank=True,
        verbose_name='Impressoras'
    )
    
    users = models.ManyToManyField(
        User,
        blank=True,
        related_name='reports_filtered',
        verbose_name='Usuários'
    )
    
    filters = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Filtros Adicionais'
    )
    
    # Metadados
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_reports',
        verbose_name='Criado por'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Concluído em'
    )
    
    # Arquivo gerado
    file_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Caminho do Arquivo'
    )
    
    file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Tamanho do Arquivo (bytes)'
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensagem de Erro'
    )
    
    # Agendamento
    is_scheduled = models.BooleanField(
        default=False,
        verbose_name='Agendado'
    )
    
    schedule_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Diário'),
            ('weekly', 'Semanal'),
            ('monthly', 'Mensal'),
            ('quarterly', 'Trimestral'),
        ],
        blank=True,
        null=True,
        verbose_name='Frequência'
    )
    
    next_run = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Próxima Execução'
    )
    
    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['report_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()}) - {self.get_status_display()}"


class ConsumptionSummary(models.Model):
    """Modelo para resumos de consumo agregados"""
    
    printer = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE,
        related_name='consumption_summaries',
        verbose_name='Impressora'
    )
    
    # Período
    period_start = models.DateField(
        verbose_name='Início do Período'
    )
    
    period_end = models.DateField(
        verbose_name='Fim do Período'
    )
    
    period_type = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Diário'),
            ('weekly', 'Semanal'),
            ('monthly', 'Mensal'),
            ('quarterly', 'Trimestral'),
            ('yearly', 'Anual'),
        ],
        verbose_name='Tipo de Período'
    )
    
    # Estatísticas de impressão
    total_pages_printed = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Páginas'
    )
    
    color_pages_printed = models.PositiveIntegerField(
        default=0,
        verbose_name='Páginas Coloridas'
    )
    
    bw_pages_printed = models.PositiveIntegerField(
        default=0,
        verbose_name='Páginas P&B'
    )
    
    duplex_pages_printed = models.PositiveIntegerField(
        default=0,
        verbose_name='Páginas Duplex'
    )
    
    # Consumo de suprimentos
    toner_black_consumed = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Toner Preto Consumido (%)'
    )
    
    toner_cyan_consumed = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Toner Ciano Consumido (%)'
    )
    
    toner_magenta_consumed = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Toner Magenta Consumido (%)'
    )
    
    toner_yellow_consumed = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Toner Amarelo Consumido (%)'
    )
    
    paper_consumed = models.PositiveIntegerField(
        default=0,
        verbose_name='Papel Consumido (folhas)'
    )
    
    # Custos estimados
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Custo Estimado'
    )
    
    # Métricas de qualidade
    average_print_time = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Tempo Médio de Impressão (s)'
    )
    
    error_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Número de Erros'
    )
    
    jam_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Número de Atolamentos'
    )
    
    # Metadados
    calculated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Calculado em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    class Meta:
        verbose_name = 'Resumo de Consumo'
        verbose_name_plural = 'Resumos de Consumo'
        unique_together = ['printer', 'period_start', 'period_end', 'period_type']
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['printer', '-period_start']),
            models.Index(fields=['period_type', '-period_start']),
        ]
    
    def __str__(self):
        return f"{self.printer.name} - {self.period_start} to {self.period_end} ({self.get_period_type_display()})"


class UserUsageSummary(models.Model):
    """Modelo para resumos de uso por usuário"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='usage_summaries',
        verbose_name='Usuário'
    )
    
    printer = models.ForeignKey(
        Printer,
        on_delete=models.CASCADE,
        related_name='user_summaries',
        verbose_name='Impressora'
    )
    
    # Período
    period_start = models.DateField(
        verbose_name='Início do Período'
    )
    
    period_end = models.DateField(
        verbose_name='Fim do Período'
    )
    
    # Estatísticas
    jobs_submitted = models.PositiveIntegerField(
        default=0,
        verbose_name='Trabalhos Enviados'
    )
    
    jobs_completed = models.PositiveIntegerField(
        default=0,
        verbose_name='Trabalhos Concluídos'
    )
    
    jobs_failed = models.PositiveIntegerField(
        default=0,
        verbose_name='Trabalhos Falhou'
    )
    
    total_pages = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Páginas'
    )
    
    color_pages = models.PositiveIntegerField(
        default=0,
        verbose_name='Páginas Coloridas'
    )
    
    duplex_pages = models.PositiveIntegerField(
        default=0,
        verbose_name='Páginas Duplex'
    )
    
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Custo Total'
    )
    
    calculated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Calculado em'
    )
    
    class Meta:
        verbose_name = 'Resumo de Uso por Usuário'
        verbose_name_plural = 'Resumos de Uso por Usuário'
        unique_together = ['user', 'printer', 'period_start', 'period_end']
        ordering = ['-period_start']
    
    def __str__(self):
        return f"{self.user.username} - {self.printer.name} - {self.period_start}"
