# Sistema de Gestão de Impressoras HP - Frontend

## Interface React para Gestão de Impressoras HP

Interface moderna e responsiva desenvolvida em React.js para o sistema de gestão centralizada de impressoras HP.

### Funcionalidades

- 🖨️ **Dashboard Intuitivo**: Visão geral do status de todas as impressoras
- 📋 **Monitoramento em Tempo Real**: Acompanhamento de níveis de toner, papel e filas
- 🔔 **Sistema de Alertas**: Notificações inteligentes e personalizadas
- 📈 **Relatórios Detalhados**: Análises e estatísticas completas
- 👥 **Gestão de Usuários**: Controle de acesso e permissões
- 🛠️ **Manutenção**: Agendamento e controle de manutenções

### Tecnologias

- **React 18** - Framework principal
- **Material-UI 5** - Componentes e design system
- **Redux Toolkit** - Gerenciamento de estado
- **React Query** - Cache e sincronização de dados
- **Recharts** - Gráficos e visualizações
- **Axios** - Cliente HTTP
- **TypeScript** - Tipagem estática

### Instalação

```bash
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm start

# Build para produção
npm run build
```

### Estrutura do Projeto

```
src/
├── components/          # Componentes reutilizáveis
├── pages/               # Páginas principais
├── hooks/               # Hooks customizados
├── services/            # Serviços de API
├── store/               # Configuração Redux
├── utils/               # Utilitários
└── types/               # Tipos TypeScript
```

### Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### Funcionalidades Principais

#### Dashboard
- Visão geral do status de todas as impressoras
- Gráficos de consumo e performance
- Alertas recentes e ações rápidas

#### Gestão de Impressoras
- Listação com filtros avançados
- Monitoramento de status em tempo real
- Configuração e testes de conexão

#### Monitoramento
- Níveis de suprimentos em tempo real
- Histórico de performance
- Métricas detalhadas

#### Alertas
- Configuração de regras personalizadas
- Notificações em tempo real
- Gerenciamento de alertas ativos

#### Relatórios
- Relatórios de consumo
- Análises de uso por usuário
- Exportação em PDF/Excel

### Autor
MiniMax Agent

### Licença
Projeto desenvolvido para uso corporativo
