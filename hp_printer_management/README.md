# Sistema de Gestão de Impressoras HP

## Central de Monitoramento e Controle

### Visão Geral
Sistema completo de gestão centralizada para impressoras HP, oferecendo monitoramento em tempo real, controle de uso, manutenção preventiva e relatórios detalhados.

### Funcionalidades Principais
- ✅ Gestão completa de impressoras HP
- ✅ Monitoramento em tempo real (toner, papel, filas)
- ✅ Sistema de usuários e permissões
- ✅ Alertas automáticos por email/SMS
- ✅ Relatórios e estatísticas detalhadas
- ✅ Integração SNMP e APIs HP
- ✅ Interface moderna e responsiva

### Tecnologias Utilizadas
- **Backend**: Python + Django + Django REST Framework
- **Frontend**: React.js + Material-UI
- **Banco de Dados**: PostgreSQL
- **Comunicação**: SNMP, APIs HP
- **Autenticação**: JWT + LDAP
- **Monitoramento**: Celery + Redis

### Estrutura do Projeto
```
hp_printer_management/
├── backend/                 # API Django
├── frontend/               # Interface React
├── docker-compose.yml      # Orquestração containers
├── requirements.txt        # Dependências Python
└── docs/                   # Documentação
```

### Instalação e Configuração

#### Pré-requisitos
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Redis

#### Backend (Django)
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

#### Frontend (React)
```bash
cd frontend
npm install
npm start
```

### Configuração de Rede
1. Configure as impressoras HP na rede local
2. Habilite SNMP nas impressoras
3. Configure os IPs no painel administrativo
4. Execute descoberta automática de impressoras

### Funcionalidades por Módulo

#### Gestão de Impressoras
- Descoberta automática na rede
- Adição/remoção manual
- Monitoramento de status
- Configuração de parâmetros

#### Monitoramento
- Níveis de toner/tinta em tempo real
- Status de papel e atolamentos
- Filas de impressão
- Métricas de performance

#### Usuários e Permissões
- Perfis: Administrador, Técnico, Usuário
- Controle de acesso por impressora
- Audit log de atividades
- Integração LDAP/Active Directory

#### Relatórios
- Consumo por período
- Uso por usuário/departamento
- Estatísticas de manutenção
- Exportação PDF/Excel

### Autor
MiniMax Agent

### Licença
Projeto desenvolvido para uso corporativo
