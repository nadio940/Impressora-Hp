from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import UserActivity
from .serializers import (
    UserSerializer, UserProfileSerializer, UserActivitySerializer,
    ChangePasswordSerializer
)
from .permissions import IsAdminOrOwner, IsAdminOrTechnician

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para gestão de usuários"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'department', 'is_active', 'is_ldap_user']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'created_at', 'last_login']
    ordering = ['username']
    
    def get_permissions(self):
        """Permissões diferentes para cada ação"""
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAdminOrTechnician]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAdminOrOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get', 'patch'])
    def profile(self, request):
        """Endpoint para perfil do usuário logado"""
        if request.method == 'GET':
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = UserProfileSerializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Endpoint para mudança de senha"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Senha alterada com sucesso.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """Atividades do usuário"""
        user = self.get_object()
        activities = UserActivity.objects.filter(user=user)
        
        # Filtros opcionais
        action_filter = request.query_params.get('action')
        if action_filter:
            activities = activities.filter(action=action_filter)
        
        # Paginação
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = UserActivitySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estatísticas de usuários"""
        # Verificar permissão
        if not request.user.is_admin:
            return Response(
                {'error': 'Permissão negada'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'admins': User.objects.filter(role='admin').count(),
            'technicians': User.objects.filter(role='technician').count(),
            'regular_users': User.objects.filter(role='user').count(),
            'ldap_users': User.objects.filter(is_ldap_user=True).count(),
        }
        
        return Response(stats)


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para atividades dos usuários (somente leitura)"""
    
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [IsAdminOrTechnician]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action', 'user']
    search_fields = ['description', 'user__username']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
