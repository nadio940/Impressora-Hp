import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { authService } from '../services/authService';
import { User } from '../types/user';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: false,
    isLoading: true,
  });

  const queryClient = useQueryClient();

  // Query para obter perfil do usuário
  const { data: user, isLoading: userLoading } = useQuery(
    'user-profile',
    authService.getProfile,
    {
      enabled: !!authState.token,
      retry: false,
      onError: () => {
        // Token inválido, fazer logout
        logout();
      },
    }
  );

  // Mutation para login
  const loginMutation = useMutation(authService.login, {
    onSuccess: (data) => {
      const { access_token, user } = data;
      localStorage.setItem('token', access_token);
      setAuthState({
        user,
        token: access_token,
        isAuthenticated: true,
        isLoading: false,
      });
      queryClient.invalidateQueries('user-profile');
    },
    onError: (error) => {
      console.error('Login error:', error);
    },
  });

  // Mutation para logout
  const logoutMutation = useMutation(authService.logout, {
    onSuccess: () => {
      localStorage.removeItem('token');
      setAuthState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
      queryClient.clear();
    },
  });

  useEffect(() => {
    if (user) {
      setAuthState((prev) => ({
        ...prev,
        user,
        isAuthenticated: true,
        isLoading: false,
      }));
    } else if (!authState.token) {
      setAuthState((prev) => ({
        ...prev,
        isLoading: false,
      }));
    }
  }, [user, authState.token]);

  const login = async (credentials: { username: string; password: string }) => {
    return loginMutation.mutateAsync(credentials);
  };

  const logout = async () => {
    return logoutMutation.mutateAsync();
  };

  return {
    user: authState.user,
    token: authState.token,
    isAuthenticated: authState.isAuthenticated,
    isLoading: authState.isLoading || userLoading,
    login,
    logout,
    loginLoading: loginMutation.isLoading,
    loginError: loginMutation.error,
  };
};
