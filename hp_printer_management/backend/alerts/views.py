from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import (
    AlertRule, Alert, NotificationLog
)
from .serializers import (
    AlertRuleSerializer, AlertSerializer, NotificationLogSerializer
)
from users.permissions import IsAdminOrTechnician


class AlertRuleViewSet(viewsets.ModelViewSet):
    """ViewSet para regras de alertas"""
    
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAdminOrTechnician]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['trigger_type', 'severity', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'severity']
    ordering = ['name']
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Ativar/desativar regra"""
        rule = self.get_object()
        rule.is_active = not rule.is_active
        rule.save()
        
        status_text = "ativada" if rule.is_active else "desativada"
        return Response({
            'message': f'Regra {status_text} com sucesso.',
            'is_active': rule.is_active
        })
    
    @action(detail=True, methods=['post'])
    def test_rule(self, request, pk=None):
        """Testar regra de alerta"""
        rule = self.get_object()
        
        try:
            from .services import AlertService
            alert_service = AlertService()
            
            # Verificar condições da regra
            triggered_printers = alert_service.check_rule_conditions(rule)
            
            return Response({
                'rule_name': rule.name,
                'triggered_printers': len(triggered_printers),
                'printers': [{
                    'id': p.id,
                    'name': p.name,
                    'ip_address': p.ip_address
                } for p in triggered_printers]
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erro ao testar regra: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet para alertas"""
    
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'severity', 'printer', 'rule']
    search_fields = ['title', 'message', 'printer__name']
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Permissões diferentes para cada ação"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrTechnician]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Reconhecer alerta"""
        alert = self.get_object()
        
        if alert.status == 'acknowledged':
            return Response(
                {'error': 'Alerta já foi reconhecido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.status = 'acknowledged'
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.user
        alert.save()
        
        # Log da atividade
        from users.models import UserActivity
        UserActivity.objects.create(
            user=request.user,
            action='maintenance',
            description=f"Alerta '{alert.title}' reconhecido",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'message': 'Alerta reconhecido com sucesso'})
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolver alerta"""
        alert = self.get_object()
        
        if alert.status == 'resolved':
            return Response(
                {'error': 'Alerta já foi resolvido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resolution_notes = request.data.get('resolution_notes', '')
        
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.resolution_notes = resolution_notes
        alert.save()
        
        # Log da atividade
        from users.models import UserActivity
        UserActivity.objects.create(
            user=request.user,
            action='maintenance',
            description=f"Alerta '{alert.title}' resolvido",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'message': 'Alerta resolvido com sucesso'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estatísticas de alertas"""
        stats = {
            'total_alerts': Alert.objects.count(),
            'new_alerts': Alert.objects.filter(status='new').count(),
            'acknowledged_alerts': Alert.objects.filter(status='acknowledged').count(),
            'resolved_alerts': Alert.objects.filter(status='resolved').count(),
            'critical_alerts': Alert.objects.filter(severity='critical').count(),
            'high_alerts': Alert.objects.filter(severity='high').count(),
            'medium_alerts': Alert.objects.filter(severity='medium').count(),
            'low_alerts': Alert.objects.filter(severity='low').count(),
        }
        
        # Alertas por período
        from datetime import timedelta
        now = timezone.now()
        
        stats['alerts_last_24h'] = Alert.objects.filter(
            created_at__gte=now - timedelta(hours=24)
        ).count()
        
        stats['alerts_last_week'] = Alert.objects.filter(
            created_at__gte=now - timedelta(days=7)
        ).count()
        
        stats['alerts_last_month'] = Alert.objects.filter(
            created_at__gte=now - timedelta(days=30)
        ).count()
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def bulk_acknowledge(self, request):
        """Reconhecer múltiplos alertas"""
        if not request.user.is_technician:
            return Response(
                {'error': 'Permissão negada'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        alert_ids = request.data.get('alert_ids', [])
        if not alert_ids:
            return Response(
                {'error': 'Lista de IDs de alertas é obrigatória'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alerts = Alert.objects.filter(
            id__in=alert_ids,
            status='new'
        )
        
        acknowledged_count = alerts.update(
            status='acknowledged',
            acknowledged_at=timezone.now(),
            acknowledged_by=request.user
        )
        
        return Response({
            'message': f'{acknowledged_count} alertas reconhecidos com sucesso',
            'acknowledged_count': acknowledged_count
        })


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para logs de notificações (somente leitura)"""
    
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAdminOrTechnician]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'status', 'recipient']
    search_fields = ['subject', 'recipient__username', 'recipient_address']
    ordering_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estatísticas de notificações"""
        stats = {
            'total_notifications': NotificationLog.objects.count(),
            'sent_notifications': NotificationLog.objects.filter(status='sent').count(),
            'failed_notifications': NotificationLog.objects.filter(status='failed').count(),
            'pending_notifications': NotificationLog.objects.filter(status='pending').count(),
            'email_notifications': NotificationLog.objects.filter(notification_type='email').count(),
            'sms_notifications': NotificationLog.objects.filter(notification_type='sms').count(),
            'system_notifications': NotificationLog.objects.filter(notification_type='system').count(),
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Tentar reenviar notificação"""
        notification = self.get_object()
        
        if notification.status == 'sent':
            return Response(
                {'error': 'Notificação já foi enviada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if notification.attempts >= notification.max_attempts:
            return Response(
                {'error': 'Número máximo de tentativas excedido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from .services import NotificationService
            notification_service = NotificationService()
            
            success = notification_service.send_notification(notification)
            
            if success:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                message = 'Notificação reenviada com sucesso'
            else:
                notification.attempts += 1
                message = 'Falha ao reenviar notificação'
            
            notification.save()
            
            return Response({'message': message, 'success': success})
            
        except Exception as e:
            return Response(
                {'error': f'Erro ao reenviar notificação: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
