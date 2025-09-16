from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from typing import List, Dict, Optional
import logging
import requests
import json

logger = logging.getLogger(__name__)


class AlertService:
    """Serviço para gerenciamento de alertas"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_rule_conditions(self, rule) -> List:
        """Verificar condições de uma regra e retornar impressoras que atendem os critérios"""
        from printers.models import Printer, PrinterSupplies
        from monitoring.models import PrinterStatus
        
        triggered_printers = []
        
        # Filtrar impressoras baseado na regra
        printers = rule.printers.all() if rule.printers.exists() else Printer.objects.filter(is_monitored=True)
        
        for printer in printers:
            try:
                if self._check_printer_against_rule(printer, rule):
                    triggered_printers.append(printer)
            except Exception as e:
                self.logger.error(f"Error checking printer {printer.name} against rule {rule.name}: {e}")
        
        return triggered_printers
    
    def _check_printer_against_rule(self, printer, rule) -> bool:
        """Verificar se uma impressora atende as condições de uma regra"""
        trigger_type = rule.trigger_type
        threshold = rule.threshold_value
        operator = rule.condition_operator
        
        if trigger_type == 'supply_low':
            # Verificar níveis de suprimentos
            low_supplies = printer.supplies.filter(
                level__lte=threshold or 25
            )
            return low_supplies.exists()
        
        elif trigger_type == 'supply_empty':
            # Verificar suprimentos vazios
            empty_supplies = printer.supplies.filter(
                level__lte=threshold or 5
            )
            return empty_supplies.exists()
        
        elif trigger_type == 'paper_jam':
            # Verificar atolamento de papel
            latest_status = printer.status_history.order_by('-recorded_at').first()
            if latest_status:
                return latest_status.paper_status == 'jam'
        
        elif trigger_type == 'printer_offline':
            # Verificar se impressora está offline
            return printer.status == 'offline'
        
        elif trigger_type == 'error_code':
            # Verificar códigos de erro
            latest_status = printer.status_history.order_by('-recorded_at').first()
            if latest_status:
                return latest_status.error_code is not None
        
        elif trigger_type == 'maintenance_due':
            # Verificar manutenção vencida
            from monitoring.models import MaintenanceRecord
            from datetime import timedelta
            
            last_maintenance = MaintenanceRecord.objects.filter(
                printer=printer,
                maintenance_type='preventive',
                status='completed'
            ).order_by('-completed_at').first()
            
            if last_maintenance:
                days_since = (timezone.now() - last_maintenance.completed_at).days
                return days_since > (threshold or 90)
            else:
                # Se nunca teve manutenção, verificar idade da impressora
                days_since_creation = (timezone.now() - printer.created_at).days
                return days_since_creation > (threshold or 30)
        
        elif trigger_type == 'high_temperature':
            # Verificar temperatura alta
            latest_status = printer.status_history.order_by('-recorded_at').first()
            if latest_status and latest_status.temperature:
                return latest_status.temperature > (threshold or 60)
        
        elif trigger_type == 'queue_full':
            # Verificar fila cheia
            queue_size = printer.print_jobs.filter(
                status__in=['pending', 'printing']
            ).count()
            return queue_size > (threshold or 10)
        
        return False
    
    def create_alert(self, rule, printer, context_data: Optional[Dict] = None):
        """Criar um novo alerta"""
        from alerts.models import Alert
        
        try:
            # Gerar título e mensagem baseados no tipo de trigger
            title, message = self._generate_alert_content(rule, printer, context_data)
            
            # Criar alerta
            alert = Alert.objects.create(
                rule=rule,
                printer=printer,
                title=title,
                message=message,
                severity=rule.severity,
                context_data=context_data or {}
            )
            
            # Enviar notificações
            self._schedule_notifications(alert)
            
            self.logger.info(f"Alert created: {alert.title} for printer {printer.name}")
            return alert
            
        except Exception as e:
            self.logger.error(f"Error creating alert for printer {printer.name}: {e}")
            return None
    
    def _generate_alert_content(self, rule, printer, context_data: Optional[Dict]) -> tuple:
        """Gerar título e mensagem do alerta"""
        trigger_type = rule.trigger_type
        
        title_templates = {
            'supply_low': f'Suprimento Baixo - {printer.name}',
            'supply_empty': f'Suprimento Vazio - {printer.name}',
            'paper_jam': f'Atolamento de Papel - {printer.name}',
            'printer_offline': f'Impressora Offline - {printer.name}',
            'error_code': f'Erro na Impressora - {printer.name}',
            'maintenance_due': f'Manutenção Vencida - {printer.name}',
            'high_temperature': f'Temperatura Alta - {printer.name}',
            'queue_full': f'Fila de Impressão Cheia - {printer.name}',
        }
        
        message_templates = {
            'supply_low': f'A impressora {printer.name} ({printer.ip_address}) está com níveis baixos de suprimentos.',
            'supply_empty': f'A impressora {printer.name} ({printer.ip_address}) está com suprimentos vazios.',
            'paper_jam': f'Detectado atolamento de papel na impressora {printer.name} ({printer.ip_address}).',
            'printer_offline': f'A impressora {printer.name} ({printer.ip_address}) está offline.',
            'error_code': f'A impressora {printer.name} ({printer.ip_address}) está reportando erros.',
            'maintenance_due': f'A impressora {printer.name} ({printer.ip_address}) precisa de manutenção preventiva.',
            'high_temperature': f'A impressora {printer.name} ({printer.ip_address}) está com temperatura elevada.',
            'queue_full': f'A fila de impressão da impressora {printer.name} ({printer.ip_address}) está cheia.',
        }
        
        title = title_templates.get(trigger_type, f'Alerta - {printer.name}')
        message = message_templates.get(trigger_type, f'Alerta gerado para a impressora {printer.name}.')
        
        # Adicionar informações do contexto à mensagem
        if context_data:
            if 'supply_levels' in context_data:
                message += f"\n\nNíveis de suprimentos:\n"
                for supply, level in context_data['supply_levels'].items():
                    message += f"- {supply}: {level}%\n"
            
            if 'error_details' in context_data:
                message += f"\n\nDetalhes do erro: {context_data['error_details']}"
        
        return title, message
    
    def _schedule_notifications(self, alert):
        """Agendar notificações para o alerta"""
        from alerts.models import NotificationLog
        
        rule = alert.rule
        
        # Obter usuários para notificar
        users_to_notify = rule.users_to_notify.filter(is_active=True)
        
        # Se não há usuários específicos, notificar admins e técnicos
        if not users_to_notify.exists():
            from users.models import User
            users_to_notify = User.objects.filter(
                is_active=True,
                role__in=['admin', 'technician']
            )
        
        for user in users_to_notify:
            # Email
            if rule.send_email and user.email:
                NotificationLog.objects.create(
                    alert=alert,
                    recipient=user,
                    notification_type='email',
                    recipient_address=user.email,
                    subject=alert.title,
                    content=alert.message
                )
            
            # SMS
            if rule.send_sms and user.phone:
                NotificationLog.objects.create(
                    alert=alert,
                    recipient=user,
                    notification_type='sms',
                    recipient_address=user.phone,
                    content=alert.title  # SMS com conteúdo mais curto
                )
            
            # Notificação no sistema
            if rule.send_system_notification:
                NotificationLog.objects.create(
                    alert=alert,
                    recipient=user,
                    notification_type='system',
                    recipient_address=user.username,
                    subject=alert.title,
                    content=alert.message
                )


class NotificationService:
    """Serviço para envio de notificações"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def send_notification(self, notification) -> bool:
        """Enviar notificação"""
        try:
            if notification.notification_type == 'email':
                return self._send_email(notification)
            elif notification.notification_type == 'sms':
                return self._send_sms(notification)
            elif notification.notification_type == 'system':
                return self._send_system_notification(notification)
            elif notification.notification_type == 'webhook':
                return self._send_webhook(notification)
            
        except Exception as e:
            self.logger.error(f"Error sending notification {notification.id}: {e}")
            notification.error_message = str(e)
            return False
        
        return False
    
    def _send_email(self, notification) -> bool:
        """Enviar email"""
        try:
            # Renderizar template HTML
            html_content = render_to_string('alerts/email_alert.html', {
                'alert': notification.alert,
                'printer': notification.alert.printer,
                'recipient': notification.recipient,
                'content': notification.content
            })
            
            send_mail(
                subject=notification.subject,
                message=notification.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient_address],
                html_message=html_content,
                fail_silently=False
            )
            
            self.logger.info(f"Email sent to {notification.recipient_address}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False
    
    def _send_sms(self, notification) -> bool:
        """Enviar SMS (implementação placeholder)"""
        try:
            # Implementar integração com provedor de SMS
            # Exemplo com Twilio, AWS SNS, etc.
            
            # Por enquanto, apenas log
            self.logger.info(f"SMS would be sent to {notification.recipient_address}: {notification.content}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending SMS: {e}")
            return False
    
    def _send_system_notification(self, notification) -> bool:
        """Criar notificação no sistema"""
        try:
            # Implementar sistema de notificações em tempo real
            # Pode usar WebSockets, Server-Sent Events, etc.
            
            # Por enquanto, marcar como enviada
            self.logger.info(f"System notification created for {notification.recipient.username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating system notification: {e}")
            return False
    
    def _send_webhook(self, notification) -> bool:
        """Enviar webhook"""
        try:
            webhook_url = getattr(settings, 'ALERT_WEBHOOK_URL', None)
            if not webhook_url:
                return False
            
            payload = {
                'alert_id': notification.alert.id,
                'title': notification.alert.title,
                'message': notification.alert.message,
                'severity': notification.alert.severity,
                'printer': {
                    'id': notification.alert.printer.id,
                    'name': notification.alert.printer.name,
                    'ip_address': notification.alert.printer.ip_address,
                },
                'timestamp': notification.alert.created_at.isoformat(),
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Webhook sent successfully")
                return True
            else:
                self.logger.error(f"Webhook failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending webhook: {e}")
            return False
