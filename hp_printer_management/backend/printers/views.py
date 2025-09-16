from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import (
    Printer, PrinterSupplies, PrintJob, PrinterPermission
)
from .serializers import (
    PrinterSerializer, PrinterListSerializer, PrintJobSerializer,
    PrinterPermissionSerializer, PrinterDiscoverySerializer,
    PrinterStatusUpdateSerializer
)
from .services import PrinterDiscoveryService, SNMPService
from users.permissions import IsAdminOrTechnician


class PrinterViewSet(viewsets.ModelViewSet):
    """ViewSet para gestão de impressoras"""
    
    queryset = Printer.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'printer_type', 'department', 'is_monitored']
    search_fields = ['name', 'model', 'serial_number', 'ip_address', 'location']
    ordering_fields = ['name', 'created_at', 'last_seen']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Usar serializer simplificado para lista"""
        if self.action == 'list':
            return PrinterListSerializer
        return PrinterSerializer
    
    def get_permissions(self):
        """Permissões diferentes para cada ação"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrTechnician]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Testar conexão com a impressora"""
        printer = self.get_object()
        
        try:
            snmp_service = SNMPService(printer.ip_address, printer.snmp_community)
            is_connected = snmp_service.test_connection()
            
            if is_connected:
                printer.last_seen = timezone.now()
                printer.status = 'active'
                printer.save()
                
                return Response({
                    'connected': True,
                    'message': 'Conexão bem-sucedida',
                    'last_seen': printer.last_seen
                })
            else:
                return Response({
                    'connected': False,
                    'message': 'Falha na conexão'
                })
        
        except Exception as e:
            return Response({
                'connected': False,
                'message': f'Erro: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Atualizar status manualmente"""
        if not request.user.is_technician:
            return Response(
                {'error': 'Permissão negada'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        printer = self.get_object()
        serializer = PrinterStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            printer.status = serializer.validated_data['status']
            printer.save()
            
            # Log da atividade
            from users.models import UserActivity
            UserActivity.objects.create(
                user=request.user,
                action='config',
                description=f"Status da impressora {printer.name} alterado para {printer.get_status_display()}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return Response({'message': 'Status atualizado com sucesso'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def supplies(self, request, pk=None):
        """Obter suprimentos da impressora"""
        printer = self.get_object()
        supplies = printer.supplies.all()
        
        from printers.serializers import PrinterSuppliesSerializer
        serializer = PrinterSuppliesSerializer(supplies, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def refresh_supplies(self, request, pk=None):
        """Atualizar suprimentos via SNMP"""
        printer = self.get_object()
        
        try:
            snmp_service = SNMPService(printer.ip_address, printer.snmp_community)
            supplies_data = snmp_service.get_supplies_status()
            
            # Atualizar suprimentos
            for supply_type, data in supplies_data.items():
                supply, created = PrinterSupplies.objects.get_or_create(
                    printer=printer,
                    supply_type=supply_type,
                    defaults={
                        'max_capacity': data.get('max_capacity', 100),
                        'level': data.get('level', 0),
                        'current_capacity': data.get('current_capacity', 0),
                    }
                )
                
                if not created:
                    supply.level = data.get('level', supply.level)
                    supply.current_capacity = data.get('current_capacity', supply.current_capacity)
                    supply.save()
            
            return Response({'message': 'Suprimentos atualizados com sucesso'})
        
        except Exception as e:
            return Response(
                {'error': f'Erro ao atualizar suprimentos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def discover(self, request):
        """Descobrir impressoras na rede"""
        if not request.user.is_technician:
            return Response(
                {'error': 'Permissão negada'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PrinterDiscoverySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        discovery_service = PrinterDiscoveryService()
        discovered_printers = discovery_service.discover_printers(
            ip_range=serializer.validated_data['ip_range'],
            timeout=serializer.validated_data['timeout'],
            snmp_community=serializer.validated_data['snmp_community']
        )
        
        return Response({
            'discovered_printers': discovered_printers,
            'count': len(discovered_printers)
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estatísticas das impressoras"""
        stats = {
            'total_printers': Printer.objects.count(),
            'active_printers': Printer.objects.filter(status='active').count(),
            'offline_printers': Printer.objects.filter(status='offline').count(),
            'maintenance_printers': Printer.objects.filter(status='maintenance').count(),
            'laser_printers': Printer.objects.filter(printer_type='laser').count(),
            'inkjet_printers': Printer.objects.filter(printer_type='inkjet').count(),
            'multifunction_printers': Printer.objects.filter(printer_type='multifunction').count(),
        }
        
        return Response(stats)


class PrintJobViewSet(viewsets.ModelViewSet):
    """ViewSet para trabalhos de impressão"""
    
    queryset = PrintJob.objects.all()
    serializer_class = PrintJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'printer', 'user', 'is_color', 'is_duplex']
    search_fields = ['job_name', 'user__username', 'printer__name']
    ordering_fields = ['submitted_at', 'pages', 'copies']
    ordering = ['-submitted_at']
    
    def get_queryset(self):
        """Filtrar por usuário se não for admin"""
        if self.request.user.is_admin:
            return PrintJob.objects.all()
        return PrintJob.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Definir usuário atual ao criar trabalho"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar trabalho de impressão"""
        job = self.get_object()
        
        # Verificar permissão
        if job.user != request.user and not request.user.is_technician:
            return Response(
                {'error': 'Permissão negada'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if job.status in ['completed', 'cancelled']:
            return Response(
                {'error': 'Trabalho já foi concluído ou cancelado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job.status = 'cancelled'
        job.save()
        
        return Response({'message': 'Trabalho cancelado com sucesso'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estatísticas de impressão"""
        queryset = self.get_queryset()
        
        stats = {
            'total_jobs': queryset.count(),
            'completed_jobs': queryset.filter(status='completed').count(),
            'pending_jobs': queryset.filter(status='pending').count(),
            'failed_jobs': queryset.filter(status='error').count(),
            'total_pages': queryset.aggregate(total=Count('pages'))['total'] or 0,
            'color_jobs': queryset.filter(is_color=True).count(),
            'duplex_jobs': queryset.filter(is_duplex=True).count(),
        }
        
        return Response(stats)


class PrinterPermissionViewSet(viewsets.ModelViewSet):
    """ViewSet para permissões de impressora"""
    
    queryset = PrinterPermission.objects.all()
    serializer_class = PrinterPermissionSerializer
    permission_classes = [IsAdminOrTechnician]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'printer', 'permission', 'is_active']
    search_fields = ['user__username', 'printer__name']
    ordering = ['user', 'printer']
    
    def perform_create(self, serializer):
        """Definir quem concedeu a permissão"""
        serializer.save(granted_by=self.request.user)
