import apiClient, { formatApiResponse, handleApiError } from './api';
import { User } from '../types/user';

interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

interface ChangePasswordData {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

export const authService = {
  // Login
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    try {
      const response = await apiClient.post('/auth/token/', {
        username: credentials.username,
        password: credentials.password,
      });
      return formatApiResponse(response);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Logout
  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/auth/logout/');
    } catch (error) {
      // Ignorar erros de logout, apenas limpar token local
      console.warn('Logout error:', error);
    }
  },

  // Obter perfil do usuário
  getProfile: async (): Promise<User> => {
    try {
      const response = await apiClient.get('/users/profile/');
      return formatApiResponse(response);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Atualizar perfil
  updateProfile: async (data: Partial<User>): Promise<User> => {
    try {
      const response = await apiClient.patch('/users/profile/', data);
      return formatApiResponse(response);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Alterar senha
  changePassword: async (data: ChangePasswordData): Promise<void> => {
    try {
      await apiClient.post('/users/change_password/', data);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Refresh token
  refreshToken: async (refreshToken: string): Promise<LoginResponse> => {
    try {
      const response = await apiClient.post('/auth/refresh/', {
        refresh: refreshToken,
      });
      return formatApiResponse(response);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
