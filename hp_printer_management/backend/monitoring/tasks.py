from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def monitor_printer_status():
    """Tarefa para monitorar status de todas as impressoras"""
    from printers.models import Printer
    from printers.services import SNMPService
    from monitoring.models import PrinterStatus
    
    monitored_count = 0
    error_count = 0
    
    for printer in Printer.objects.filter(is_monitored=True):
        try:
            snmp_service = SNMPService(printer.ip_address, printer.snmp_community)
            
            # Testar conexão
            is_online = snmp_service.test_connection()
            
            # Obter status detalhado se online
            if is_online:
                printer_status = snmp_service.get_printer_status()
                paper_status = snmp_service.get_paper_status()
                
                # Criar registro de status
                PrinterStatus.objects.create(
                    printer=printer,
                    is_online=True,
                    paper_status=paper_status.get('status', 'unknown'),
                    paper_level=paper_status.get('percentage', 0),
                    queue_size=printer.print_jobs.filter(
                        status__in=['pending', 'printing']
                    ).count(),
                    total_pages_printed=printer.print_jobs.filter(
                        status='completed'
                    ).aggregate(total=models.Sum('pages'))['total'] or 0,
                )
                
                # Atualizar última conexão
                printer.last_seen = timezone.now()
                if printer.status == 'offline':
                    printer.status = 'active'
                printer.save()
                
            else:
                # Impressora offline
                PrinterStatus.objects.create(
                    printer=printer,
                    is_online=False,
                    paper_status='unknown',
                    paper_level=0,
                    queue_size=0
                )
                
                # Atualizar status se necessário
                if printer.status != 'offline':
                    printer.status = 'offline'
                    printer.save()
            
            monitored_count += 1
            
        except Exception as e:
            logger.error(f"Error monitoring printer {printer.name}: {e}")
            error_count += 1
    
    logger.info(f"Monitoring completed: {monitored_count} printers monitored, {error_count} errors")
    return {
        'monitored_count': monitored_count,
        'error_count': error_count
    }


@shared_task
def update_printer_supplies():
    """Tarefa para atualizar suprimentos das impressoras"""
    from printers.models import Printer, PrinterSupplies
    from printers.services import SNMPService
    
    updated_count = 0
    error_count = 0
    
    for printer in Printer.objects.filter(is_monitored=True, status='active'):
        try:
            snmp_service = SNMPService(printer.ip_address, printer.snmp_community)
            supplies_data = snmp_service.get_supplies_status()
            
            for supply_type, data in supplies_data.items():
                supply, created = PrinterSupplies.objects.get_or_create(
                    printer=printer,
                    supply_type=supply_type,
                    defaults={
                        'max_capacity': data.get('max_capacity', 100),
                        'level': data.get('level', 0),
                        'current_capacity': data.get('current_capacity', 0),
                        'status': data.get('status', 'unknown'),
                    }
                )
                
                if not created:
                    supply.level = data.get('level', supply.level)
                    supply.current_capacity = data.get('current_capacity', supply.current_capacity)
                    supply.status = data.get('status', supply.status)
                    supply.save()
            
            updated_count += 1
            
        except Exception as e:
            logger.error(f"Error updating supplies for {printer.name}: {e}")
            error_count += 1
    
    logger.info(f"Supplies update completed: {updated_count} printers updated, {error_count} errors")
    return {
        'updated_count': updated_count,
        'error_count': error_count
    }


@shared_task
def check_alert_rules():
    """Tarefa para verificar regras de alertas"""
    from alerts.models import AlertRule, Alert
    from alerts.services import AlertService
    
    alert_service = AlertService()
    alerts_generated = 0
    
    for rule in AlertRule.objects.filter(is_active=True):
        try:
            # Verificar se a regra foi disparada recentemente (cooldown)
            recent_alerts = Alert.objects.filter(
                rule=rule,
                created_at__gte=timezone.now() - timedelta(minutes=rule.cooldown_minutes)
            )
            
            if recent_alerts.exists():
                continue  # Skip se ainda em cooldown
            
            # Verificar condições da regra
            triggered_printers = alert_service.check_rule_conditions(rule)
            
            for printer in triggered_printers:
                alert = alert_service.create_alert(rule, printer)
                if alert:
                    alerts_generated += 1
        
        except Exception as e:
            logger.error(f"Error checking alert rule {rule.name}: {e}")
    
    logger.info(f"Alert check completed: {alerts_generated} alerts generated")
    return {
        'alerts_generated': alerts_generated
    }


@shared_task
def process_alert_notifications():
    """Tarefa para processar notificações de alertas pendentes"""
    from alerts.models import NotificationLog
    from alerts.services import NotificationService
    
    notification_service = NotificationService()
    processed_count = 0
    
    # Buscar notificações pendentes
    pending_notifications = NotificationLog.objects.filter(
        status='pending',
        attempts__lt=models.F('max_attempts')
    )
    
    for notification in pending_notifications:
        try:
            success = notification_service.send_notification(notification)
            if success:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
            else:
                notification.attempts += 1
                if notification.attempts >= notification.max_attempts:
                    notification.status = 'failed'
            
            notification.save()
            processed_count += 1
            
        except Exception as e:
            logger.error(f"Error processing notification {notification.id}: {e}")
            notification.attempts += 1
            notification.error_message = str(e)
            if notification.attempts >= notification.max_attempts:
                notification.status = 'failed'
            notification.save()
    
    logger.info(f"Notification processing completed: {processed_count} notifications processed")
    return {
        'processed_count': processed_count
    }


@shared_task
def generate_scheduled_reports():
    """Tarefa para gerar relatórios agendados"""
    from reports.models import Report
    from reports.services import ReportService
    
    report_service = ReportService()
    generated_count = 0
    
    # Buscar relatórios agendados para execução
    scheduled_reports = Report.objects.filter(
        is_scheduled=True,
        status='scheduled',
        next_run__lte=timezone.now()
    )
    
    for report in scheduled_reports:
        try:
            # Gerar relatório
            success = report_service.generate_report(report)
            
            if success:
                # Calcular próxima execução
                next_run = report_service.calculate_next_run(report)
                report.next_run = next_run
                report.save()
                generated_count += 1
            
        except Exception as e:
            logger.error(f"Error generating scheduled report {report.id}: {e}")
            report.status = 'failed'
            report.error_message = str(e)
            report.save()
    
    logger.info(f"Scheduled reports generation completed: {generated_count} reports generated")
    return {
        'generated_count': generated_count
    }


@shared_task
def cleanup_old_data():
    """Tarefa para limpeza de dados antigos"""
    from monitoring.models import PrinterStatus
    from users.models import UserActivity
    from alerts.models import Alert, NotificationLog
    
    cutoff_date = timezone.now() - timedelta(days=90)  # Manter 90 dias
    
    # Limpar status antigos
    old_status_count = PrinterStatus.objects.filter(
        recorded_at__lt=cutoff_date
    ).count()
    PrinterStatus.objects.filter(recorded_at__lt=cutoff_date).delete()
    
    # Limpar atividades antigas
    old_activities_count = UserActivity.objects.filter(
        timestamp__lt=cutoff_date
    ).count()
    UserActivity.objects.filter(timestamp__lt=cutoff_date).delete()
    
    # Limpar alertas resolvidos antigos
    old_alerts_count = Alert.objects.filter(
        status='resolved',
        resolved_at__lt=cutoff_date
    ).count()
    Alert.objects.filter(
        status='resolved',
        resolved_at__lt=cutoff_date
    ).delete()
    
    # Limpar logs de notificação antigos
    old_notifications_count = NotificationLog.objects.filter(
        created_at__lt=cutoff_date
    ).count()
    NotificationLog.objects.filter(created_at__lt=cutoff_date).delete()
    
    logger.info(f"Cleanup completed: {old_status_count} status, {old_activities_count} activities, "
                f"{old_alerts_count} alerts, {old_notifications_count} notifications removed")
    
    return {
        'status_cleaned': old_status_count,
        'activities_cleaned': old_activities_count,
        'alerts_cleaned': old_alerts_count,
        'notifications_cleaned': old_notifications_count
    }


@shared_task
def calculate_consumption_summaries():
    """Tarefa para calcular resumos de consumo periódicos"""
    from reports.models import ConsumptionSummary
    from reports.services import ConsumptionCalculator
    
    calculator = ConsumptionCalculator()
    
    # Calcular resumos diários, semanais e mensais
    periods = ['daily', 'weekly', 'monthly']
    calculated_count = 0
    
    for period in periods:
        try:
            count = calculator.calculate_period_summaries(period)
            calculated_count += count
        except Exception as e:
            logger.error(f"Error calculating {period} summaries: {e}")
    
    logger.info(f"Consumption summaries calculation completed: {calculated_count} summaries calculated")
    return {
        'calculated_count': calculated_count
    }


@shared_task
def perform_maintenance_checks():
    """Tarefa para verificar necessidade de manutenção preventiva"""
    from monitoring.models import MaintenanceRecord
    from printers.models import Printer
    from alerts.models import AlertRule, Alert
    
    maintenance_alerts = 0
    
    for printer in Printer.objects.filter(is_monitored=True):
        try:
            # Verificar última manutenção
            last_maintenance = MaintenanceRecord.objects.filter(
                printer=printer,
                maintenance_type='preventive',
                status='completed'
            ).order_by('-completed_at').first()
            
            if last_maintenance:
                # Verificar se precisa de manutenção (90 dias)
                if (timezone.now() - last_maintenance.completed_at).days > 90:
                    # Criar alerta de manutenção
                    rule = AlertRule.objects.filter(
                        trigger_type='maintenance_due',
                        is_active=True
                    ).first()
                    
                    if rule:
                        from alerts.services import AlertService
                        alert_service = AlertService()
                        alert = alert_service.create_alert(rule, printer)
                        if alert:
                            maintenance_alerts += 1
            
        except Exception as e:
            logger.error(f"Error checking maintenance for {printer.name}: {e}")
    
    logger.info(f"Maintenance checks completed: {maintenance_alerts} maintenance alerts created")
    return {
        'maintenance_alerts': maintenance_alerts
    }
