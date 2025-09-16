export interface Alert {
  id: number;
  rule: number;
  printer: number;
  printerName: string;
  title: string;
  message: string;
  status: 'new' | 'acknowledged' | 'resolved' | 'escalated' | 'closed';
  severity: 'low' | 'medium' | 'high' | 'critical';
  contextData?: Record<string, any>;
  createdAt: string;
  acknowledgedAt?: string;
  acknowledgedBy?: number;
  acknowledgedByName?: string;
  resolvedAt?: string;
  resolvedBy?: number;
  resolvedByName?: string;
  resolutionNotes?: string;
}

export interface AlertRule {
  id: number;
  name: string;
  description?: string;
  triggerType: 'supply_low' | 'supply_empty' | 'paper_jam' | 'printer_offline' | 
               'error_code' | 'maintenance_due' | 'high_temperature' | 'queue_full';
  severity: 'low' | 'medium' | 'high' | 'critical';
  thresholdValue?: number;
  conditionOperator: 'lt' | 'lte' | 'gt' | 'gte' | 'eq' | 'ne';
  sendEmail: boolean;
  sendSms: boolean;
  sendSystemNotification: boolean;
  printers: number[];
  usersToNotify: number[];
  isActive: boolean;
  cooldownMinutes: number;
  createdAt: string;
  updatedAt: string;
}

export interface NotificationLog {
  id: number;
  alert: number;
  recipient: number;
  recipientName: string;
  notificationType: 'email' | 'sms' | 'system' | 'webhook';
  status: 'pending' | 'sent' | 'failed' | 'delivered';
  recipientAddress: string;
  subject?: string;
  content: string;
  sentAt?: string;
  deliveredAt?: string;
  errorMessage?: string;
  attempts: number;
  maxAttempts: number;
  createdAt: string;
}

export interface AlertFilters {
  status?: string;
  severity?: string;
  printer?: number;
  rule?: number;
  search?: string;
  ordering?: string;
  page?: number;
  pageSize?: number;
}

export interface AlertRuleCreateData {
  name: string;
  description?: string;
  triggerType: string;
  severity: string;
  thresholdValue?: number;
  conditionOperator?: string;
  sendEmail?: boolean;
  sendSms?: boolean;
  sendSystemNotification?: boolean;
  printers?: number[];
  usersToNotify?: number[];
  cooldownMinutes?: number;
}

export interface AlertRuleUpdateData {
  name?: string;
  description?: string;
  triggerType?: string;
  severity?: string;
  thresholdValue?: number;
  conditionOperator?: string;
  sendEmail?: boolean;
  sendSms?: boolean;
  sendSystemNotification?: boolean;
  printers?: number[];
  usersToNotify?: number[];
  isActive?: boolean;
  cooldownMinutes?: number;
}

export interface AlertStatistics {
  totalAlerts: number;
  newAlerts: number;
  acknowledgedAlerts: number;
  resolvedAlerts: number;
  criticalAlerts: number;
  highAlerts: number;
  mediumAlerts: number;
  lowAlerts: number;
  alertsLast24h: number;
  alertsLastWeek: number;
  alertsLastMonth: number;
}
