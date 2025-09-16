from rest_framework import serializers
from .models import (
    Printer, PrinterSupplies, PrintJob, PrinterPermission
)
from users.serializers import UserSerializer


class PrinterSuppliesSerializer(serializers.ModelSerializer):
    """Serializer para suprimentos da impressora"""
    
    supply_type_display = serializers.CharField(source='get_supply_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PrinterSupplies
        fields = [
            'id', 'supply_type', 'supply_type_display', 'level',
            'max_capacity', 'current_capacity', 'status', 'status_display',
            'last_updated'
        ]
        read_only_fields = ['id', 'last_updated']


class PrinterSerializer(serializers.ModelSerializer):
    """Serializer para impressoras"""
    
    supplies = PrinterSuppliesSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_printer_type_display', read_only=True)
    is_online = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Printer
        fields = [
            'id', 'name', 'model', 'serial_number', 'ip_address',
            'mac_address', 'printer_type', 'type_display', 'status',
            'status_display', 'location', 'department', 'snmp_community',
            'snmp_port', 'paper_capacity', 'supports_duplex',
            'supports_color', 'firmware_version', 'is_monitored',
            'is_online', 'created_at', 'updated_at', 'last_seen',
            'supplies'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_seen']


class PrinterListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para lista de impressoras"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_printer_type_display', read_only=True)
    is_online = serializers.BooleanField(read_only=True)
    
    # Campos agregados
    toner_levels = serializers.SerializerMethodField()
    paper_level = serializers.SerializerMethodField()
    queue_size = serializers.SerializerMethodField()
    
    class Meta:
        model = Printer
        fields = [
            'id', 'name', 'model', 'ip_address', 'printer_type',
            'type_display', 'status', 'status_display', 'location',
            'department', 'is_online', 'last_seen', 'toner_levels',
            'paper_level', 'queue_size'
        ]
    
    def get_toner_levels(self, obj):
        """Retorna níveis de toner/tinta"""
        supplies = obj.supplies.filter(
            supply_type__in=['toner_black', 'toner_cyan', 'toner_magenta', 'toner_yellow']
        )
        return {
            supply.supply_type: supply.level
            for supply in supplies
        }
    
    def get_paper_level(self, obj):
        """Retorna nível de papel"""
        paper_supply = obj.supplies.filter(supply_type='paper').first()
        return paper_supply.level if paper_supply else 0
    
    def get_queue_size(self, obj):
        """Retorna tamanho da fila de impressão"""
        return obj.print_jobs.filter(status__in=['pending', 'printing']).count()


class PrintJobSerializer(serializers.ModelSerializer):
    """Serializer para trabalhos de impressão"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    printer_name = serializers.CharField(source='printer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_pages = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PrintJob
        fields = [
            'id', 'printer', 'printer_name', 'user', 'user_name',
            'job_name', 'pages', 'copies', 'total_pages', 'is_color',
            'is_duplex', 'status', 'status_display', 'submitted_at',
            'started_at', 'completed_at', 'error_message'
        ]
        read_only_fields = [
            'id', 'submitted_at', 'started_at', 'completed_at'
        ]


class PrinterPermissionSerializer(serializers.ModelSerializer):
    """Serializer para permissões de impressora"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    printer_name = serializers.CharField(source='printer.name', read_only=True)
    permission_display = serializers.CharField(source='get_permission_display', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.username', read_only=True)
    
    class Meta:
        model = PrinterPermission
        fields = [
            'id', 'user', 'user_name', 'printer', 'printer_name',
            'permission', 'permission_display', 'granted_by',
            'granted_by_name', 'granted_at', 'is_active'
        ]
        read_only_fields = ['id', 'granted_at']


class PrinterDiscoverySerializer(serializers.Serializer):
    """Serializer para descoberta de impressoras na rede"""
    
    ip_range = serializers.CharField(
        help_text="Faixa de IP para busca (ex: 192.168.1.0/24)"
    )
    
    timeout = serializers.IntegerField(
        default=5,
        help_text="Timeout em segundos para cada IP"
    )
    
    snmp_community = serializers.CharField(
        default='public',
        help_text="Community SNMP para testes"
    )


class PrinterStatusUpdateSerializer(serializers.Serializer):
    """Serializer para atualização de status da impressora"""
    
    status = serializers.ChoiceField(choices=Printer.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
