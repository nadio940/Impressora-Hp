export interface Printer {
  id: number;
  name: string;
  model: string;
  serialNumber: string;
  ipAddress: string;
  macAddress?: string;
  printerType: 'laser' | 'inkjet' | 'multifunction';
  typeDisplay: string;
  status: 'active' | 'inactive' | 'maintenance' | 'error' | 'offline';
  statusDisplay: string;
  location?: string;
  department?: string;
  snmpCommunity: string;
  snmpPort: number;
  paperCapacity: number;
  supportsDuplex: boolean;
  supportsColor: boolean;
  firmwareVersion?: string;
  isMonitored: boolean;
  isOnline: boolean;
  createdAt: string;
  updatedAt: string;
  lastSeen?: string;
  supplies: PrinterSupply[];
  tonerLevels: Record<string, number>;
  paperLevel: number;
  queueSize: number;
}

export interface PrinterSupply {
  id: number;
  supplyType: string;
  supplyTypeDisplay: string;
  level: number;
  maxCapacity: number;
  currentCapacity: number;
  status: 'ok' | 'low' | 'very_low' | 'empty' | 'unknown';
  statusDisplay: string;
  lastUpdated: string;
}

export interface PrintJob {
  id: number;
  printer: number;
  printerName: string;
  user: number;
  userName: string;
  jobName: string;
  pages: number;
  copies: number;
  totalPages: number;
  isColor: boolean;
  isDuplex: boolean;
  status: 'pending' | 'printing' | 'completed' | 'cancelled' | 'error';
  statusDisplay: string;
  submittedAt: string;
  startedAt?: string;
  completedAt?: string;
  errorMessage?: string;
}

export interface PrinterPermission {
  id: number;
  user: number;
  userName: string;
  printer: number;
  printerName: string;
  permission: 'print' | 'scan' | 'configure' | 'maintain';
  permissionDisplay: string;
  grantedBy: number;
  grantedByName: string;
  grantedAt: string;
  isActive: boolean;
}

export interface PrinterFilters {
  status?: string;
  printerType?: string;
  department?: string;
  isMonitored?: boolean;
  search?: string;
  ordering?: string;
  page?: number;
  pageSize?: number;
}

export interface PrinterCreateData {
  name: string;
  model: string;
  serialNumber: string;
  ipAddress: string;
  macAddress?: string;
  printerType: 'laser' | 'inkjet' | 'multifunction';
  location?: string;
  department?: string;
  snmpCommunity?: string;
  snmpPort?: number;
  paperCapacity?: number;
  supportsDuplex?: boolean;
  supportsColor?: boolean;
  isMonitored?: boolean;
}

export interface PrinterUpdateData {
  name?: string;
  model?: string;
  serialNumber?: string;
  ipAddress?: string;
  macAddress?: string;
  printerType?: 'laser' | 'inkjet' | 'multifunction';
  status?: 'active' | 'inactive' | 'maintenance' | 'error' | 'offline';
  location?: string;
  department?: string;
  snmpCommunity?: string;
  snmpPort?: number;
  paperCapacity?: number;
  supportsDuplex?: boolean;
  supportsColor?: boolean;
  isMonitored?: boolean;
}

export interface PrintJobFilters {
  status?: string;
  printer?: number;
  user?: number;
  isColor?: boolean;
  isDuplex?: boolean;
  search?: string;
  ordering?: string;
  page?: number;
  pageSize?: number;
}
