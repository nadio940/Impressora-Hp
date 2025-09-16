import ipaddress
import socket
from pysnmp.hlapi import *
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SNMPService:
    """Serviço para comunicação SNMP com impressoras HP"""
    
    # OIDs padrão para impressoras HP
    OIDS = {
        'system_description': '1.3.6.1.2.1.1.1.0',
        'system_name': '1.3.6.1.2.1.1.5.0',
        'device_type': '1.3.6.1.2.1.25.3.2.1.2.1',
        'serial_number': '1.3.6.1.2.1.43.5.1.1.17.1',
        'model': '1.3.6.1.2.1.25.3.2.1.3.1',
        'firmware_version': '1.3.6.1.2.1.43.15.1.1.6.1.1',
        
        # Status da impressora
        'printer_status': '1.3.6.1.2.1.25.3.2.1.5.1',
        'printer_state': '1.3.6.1.2.1.43.10.2.1.4.1.1',
        
        # Suprimentos
        'supply_level': '1.3.6.1.2.1.43.11.1.1.9.1',
        'supply_max_capacity': '1.3.6.1.2.1.43.11.1.1.8.1',
        'supply_description': '1.3.6.1.2.1.43.11.1.1.6.1',
        'supply_type': '1.3.6.1.2.1.43.11.1.1.5.1',
        
        # Papel
        'paper_input_status': '1.3.6.1.2.1.43.8.2.1.10.1',
        'paper_input_level': '1.3.6.1.2.1.43.8.2.1.9.1',
        'paper_input_capacity': '1.3.6.1.2.1.43.8.2.1.8.1',
        
        # Contadores
        'total_pages': '1.3.6.1.2.1.43.10.2.1.4.1.1',
        'color_pages': '1.3.6.1.2.1.43.10.2.1.4.1.2',
        
        # Erros
        'error_status': '1.3.6.1.2.1.43.18.1.1.1.1',
        'error_description': '1.3.6.1.2.1.43.18.1.1.2.1',
    }
    
    def __init__(self, ip_address: str, community: str = 'public', port: int = 161):
        self.ip_address = ip_address
        self.community = community
        self.port = port
    
    def test_connection(self) -> bool:
        """Testar conexão SNMP com a impressora"""
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.ip_address, self.port)),
                ContextData(),
                ObjectType(ObjectIdentity(self.OIDS['system_description'])),
                lexicographicMode=False
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if errorIndication:
                logger.error(f"SNMP Error: {errorIndication}")
                return False
            
            if errorStatus:
                logger.error(f"SNMP Error: {errorStatus.prettyPrint()}")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Exception testing SNMP connection: {e}")
            return False
    
    def get_basic_info(self) -> Dict:
        """Obter informações básicas da impressora"""
        info = {}
        
        try:
            # OIDs para informações básicas
            oids_to_query = [
                ('description', self.OIDS['system_description']),
                ('name', self.OIDS['system_name']),
                ('serial_number', self.OIDS['serial_number']),
                ('model', self.OIDS['model']),
                ('firmware_version', self.OIDS['firmware_version']),
            ]
            
            for name, oid in oids_to_query:
                try:
                    iterator = getCmd(
                        SnmpEngine(),
                        CommunityData(self.community),
                        UdpTransportTarget((self.ip_address, self.port)),
                        ContextData(),
                        ObjectType(ObjectIdentity(oid)),
                        lexicographicMode=False
                    )
                    
                    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
                    
                    if not errorIndication and not errorStatus:
                        for varBind in varBinds:
                            info[name] = str(varBind[1])
                    
                except Exception as e:
                    logger.warning(f"Error getting {name}: {e}")
                    info[name] = None
        
        except Exception as e:
            logger.error(f"Error getting basic info: {e}")
        
        return info
    
    def get_printer_status(self) -> Dict:
        """Obter status da impressora"""
        status = {}
        
        try:
            # Status da impressora
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.ip_address, self.port)),
                ContextData(),
                ObjectType(ObjectIdentity(self.OIDS['printer_status'])),
                lexicographicMode=False
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if not errorIndication and not errorStatus:
                for varBind in varBinds:
                    status_code = int(varBind[1])
                    status['status_code'] = status_code
                    status['status'] = self._interpret_printer_status(status_code)
        
        except Exception as e:
            logger.error(f"Error getting printer status: {e}")
            status['status'] = 'unknown'
        
        return status
    
    def get_supplies_status(self) -> Dict:
        """Obter status dos suprimentos"""
        supplies = {}
        
        try:
            # Usar nextCmd para obter múltiplas entradas
            iterator = nextCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.ip_address, self.port)),
                ContextData(),
                ObjectType(ObjectIdentity(self.OIDS['supply_description'])),
                ObjectType(ObjectIdentity(self.OIDS['supply_level'])),
                ObjectType(ObjectIdentity(self.OIDS['supply_max_capacity'])),
                ObjectType(ObjectIdentity(self.OIDS['supply_type'])),
                lexicographicMode=False
            )
            
            for errorIndication, errorStatus, errorIndex, varBinds in iterator:
                if errorIndication:
                    break
                
                if errorStatus:
                    break
                
                # Processar dados dos suprimentos
                if len(varBinds) >= 4:
                    description = str(varBinds[0][1])
                    level = int(varBinds[1][1]) if varBinds[1][1] != -1 else 0
                    max_capacity = int(varBinds[2][1]) if varBinds[2][1] != -1 else 100
                    supply_type_code = int(varBinds[3][1])
                    
                    supply_type = self._interpret_supply_type(description, supply_type_code)
                    
                    if supply_type:
                        supplies[supply_type] = {
                            'description': description,
                            'level': level,
                            'max_capacity': max_capacity,
                            'current_capacity': int((level / 100) * max_capacity) if max_capacity > 0 else 0,
                            'status': self._get_supply_status(level)
                        }
        
        except Exception as e:
            logger.error(f"Error getting supplies status: {e}")
        
        return supplies
    
    def get_paper_status(self) -> Dict:
        """Obter status do papel"""
        paper_status = {}
        
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.ip_address, self.port)),
                ContextData(),
                ObjectType(ObjectIdentity(self.OIDS['paper_input_level'])),
                ObjectType(ObjectIdentity(self.OIDS['paper_input_capacity'])),
                ObjectType(ObjectIdentity(self.OIDS['paper_input_status'])),
                lexicographicMode=False
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if not errorIndication and not errorStatus:
                if len(varBinds) >= 3:
                    level = int(varBinds[0][1]) if varBinds[0][1] != -1 else 0
                    capacity = int(varBinds[1][1]) if varBinds[1][1] != -1 else 250
                    status_code = int(varBinds[2][1]) if varBinds[2][1] != -1 else 0
                    
                    paper_status = {
                        'level': level,
                        'capacity': capacity,
                        'status_code': status_code,
                        'status': self._interpret_paper_status(status_code),
                        'percentage': int((level / capacity) * 100) if capacity > 0 else 0
                    }
        
        except Exception as e:
            logger.error(f"Error getting paper status: {e}")
        
        return paper_status
    
    def _interpret_printer_status(self, status_code: int) -> str:
        """Interpretar código de status da impressora"""
        status_map = {
            1: 'other',
            2: 'unknown',
            3: 'idle',
            4: 'printing',
            5: 'warmup',
        }
        return status_map.get(status_code, 'unknown')
    
    def _interpret_supply_type(self, description: str, type_code: int) -> Optional[str]:
        """Interpretar tipo de suprimento baseado na descrição"""
        desc_lower = description.lower()
        
        if 'black' in desc_lower or 'preto' in desc_lower:
            if 'toner' in desc_lower:
                return 'toner_black'
            elif 'ink' in desc_lower or 'tinta' in desc_lower:
                return 'ink_black'
        elif 'cyan' in desc_lower or 'ciano' in desc_lower:
            if 'toner' in desc_lower:
                return 'toner_cyan'
            elif 'ink' in desc_lower or 'tinta' in desc_lower:
                return 'ink_cyan'
        elif 'magenta' in desc_lower:
            if 'toner' in desc_lower:
                return 'toner_magenta'
            elif 'ink' in desc_lower or 'tinta' in desc_lower:
                return 'ink_magenta'
        elif 'yellow' in desc_lower or 'amarelo' in desc_lower:
            if 'toner' in desc_lower:
                return 'toner_yellow'
            elif 'ink' in desc_lower or 'tinta' in desc_lower:
                return 'ink_yellow'
        elif 'drum' in desc_lower or 'cilindro' in desc_lower:
            return 'drum'
        elif 'fuser' in desc_lower or 'fusor' in desc_lower:
            return 'fuser'
        
        return None
    
    def _get_supply_status(self, level: int) -> str:
        """Determinar status do suprimento baseado no nível"""
        if level <= 0:
            return 'empty'
        elif level <= 10:
            return 'very_low'
        elif level <= 25:
            return 'low'
        else:
            return 'ok'
    
    def _interpret_paper_status(self, status_code: int) -> str:
        """Interpretar status do papel"""
        status_map = {
            0: 'unknown',
            3: 'ok',
            4: 'low',
            5: 'empty',
            8: 'jam',
        }
        return status_map.get(status_code, 'unknown')


class PrinterDiscoveryService:
    """Serviço para descoberta automática de impressoras na rede"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def discover_printers(self, ip_range: str, timeout: int = 5, snmp_community: str = 'public') -> List[Dict]:
        """Descobrir impressoras em uma faixa de IP"""
        discovered_printers = []
        
        try:
            # Converter string de range para objetos de rede
            network = ipaddress.IPv4Network(ip_range, strict=False)
            
            for ip in network.hosts():
                ip_str = str(ip)
                
                # Testar conexão SNMP
                if self._test_snmp_connection(ip_str, snmp_community, timeout):
                    printer_info = self._get_printer_info(ip_str, snmp_community)
                    if printer_info:
                        printer_info['ip_address'] = ip_str
                        discovered_printers.append(printer_info)
        
        except Exception as e:
            self.logger.error(f"Error during printer discovery: {e}")
        
        return discovered_printers
    
    def _test_snmp_connection(self, ip_address: str, community: str, timeout: int) -> bool:
        """Testar conexão SNMP com um IP"""
        try:
            snmp_service = SNMPService(ip_address, community)
            return snmp_service.test_connection()
        except Exception:
            return False
    
    def _get_printer_info(self, ip_address: str, community: str) -> Optional[Dict]:
        """Obter informações da impressora via SNMP"""
        try:
            snmp_service = SNMPService(ip_address, community)
            basic_info = snmp_service.get_basic_info()
            
            # Verificar se é realmente uma impressora HP
            description = basic_info.get('description', '').lower()
            if 'hp' in description or 'hewlett' in description:
                return {
                    'name': basic_info.get('name', f'Impressora-{ip_address}'),
                    'model': basic_info.get('model', 'Desconhecido'),
                    'serial_number': basic_info.get('serial_number', ''),
                    'firmware_version': basic_info.get('firmware_version', ''),
                    'description': basic_info.get('description', ''),
                    'discovered_at': timezone.now().isoformat(),
                }
        
        except Exception as e:
            self.logger.error(f"Error getting printer info for {ip_address}: {e}")
        
        return None
    
    def ping_host(self, ip_address: str, timeout: int = 3) -> bool:
        """Fazer ping em um host para verificar se está ativo"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip_address, 161))  # Porta SNMP
            sock.close()
            return result == 0
        except Exception:
            return False
