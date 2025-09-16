export interface User {
  id: number;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  fullName: string;
  role: 'admin' | 'technician' | 'user';
  department?: string;
  phone?: string;
  isActive: boolean;
  isStaff: boolean;
  isLdapUser: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface UserActivity {
  id: number;
  user: number;
  userName: string;
  action: 'login' | 'logout' | 'print' | 'scan' | 'config' | 'maintenance';
  actionDisplay: string;
  description?: string;
  ipAddress?: string;
  userAgent?: string;
  timestamp: string;
}

export interface UserFilters {
  role?: string;
  department?: string;
  isActive?: boolean;
  isLdapUser?: boolean;
  search?: string;
  ordering?: string;
  page?: number;
  pageSize?: number;
}

export interface UserCreateData {
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  password: string;
  role: 'admin' | 'technician' | 'user';
  department?: string;
  phone?: string;
  isActive?: boolean;
}

export interface UserUpdateData {
  email?: string;
  firstName?: string;
  lastName?: string;
  role?: 'admin' | 'technician' | 'user';
  department?: string;
  phone?: string;
  isActive?: boolean;
}
