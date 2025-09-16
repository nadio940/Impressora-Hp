# Documentação de Instalação e Configuração

## Sistema de Gestão de Impressoras HP

### Pré-requisitos

- **Python 3.9+**
- **Node.js 16+**
- **PostgreSQL 13+**
- **Redis 6+**
- **Docker** (opcional)

### Instalação com Docker (Recomendado)

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd hp_printer_management
```

2. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Execute com Docker Compose:**
```bash
docker-compose up -d
```

4. **Execute as migrações:**
```bash
docker-compose exec backend python manage.py migrate
```

5. **Crie um superusuário:**
```bash
docker-compose exec backend python manage.py createsuperuser
```

### Instalação Manual

#### Backend (Django)

1. **Criar ambiente virtual:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

3. **Configurar banco de dados:**
```bash
# Criar banco PostgreSQL
creatdb hp_printer_db

# Configurar variáveis de ambiente
export DATABASE_URL="postgresql://user:password@localhost:5432/hp_printer_db"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key"
export DEBUG="True"
```

4. **Executar migrações:**
```bash
python manage.py migrate
```

5. **Criar superusuário:**
```bash
python manage.py createsuperuser
```

6. **Iniciar servidor de desenvolvimento:**
```bash
python manage.py runserver
```

#### Frontend (React)

1. **Instalar dependências:**
```bash
cd frontend
npm install
```

2. **Configurar variáveis de ambiente:**
```bash
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
```

3. **Iniciar servidor de desenvolvimento:**
```bash
npm start
```

#### Workers Celery

1. **Iniciar Redis:**
```bash
redis-server
```

2. **Iniciar worker Celery:**
```bash
celery -A hp_management worker -l info
```

3. **Iniciar Celery Beat (tarefas agendadas):**
```bash
celery -A hp_management beat -l info
```

### Configuração das Impressoras HP

#### Habilitar SNMP nas Impressoras

1. **Acesse o painel web da impressora**
2. **Vá para Configurações > Rede > SNMP**
3. **Habilite SNMP v1/v2c**
4. **Configure a community (padrão: "public")**
5. **Anote o endereço IP da impressora**

#### Descoberta Automática

1. **Acesse o sistema web**
2. **Vá para Impressoras > Descobrir**
3. **Digite a faixa de IP da rede (ex: 192.168.1.0/24)**
4. **Execute a descoberta**
5. **Adicione as impressoras encontradas**

### Configuração de Alertas

#### Email

1. **Configure as variáveis de email no .env:**
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourcompany.com
```

#### SMS (Opcional)

1. **Configure provedor de SMS (Twilio, AWS SNS, etc.)**
2. **Implemente o método `_send_sms` em `alerts/services.py`**

### Configuração LDAP (Opcional)

```bash
# Adicione ao .env
AUTH_LDAP_SERVER_URI=ldap://your-ldap-server:389
AUTH_LDAP_BIND_DN=cn=admin,dc=company,dc=com
AUTH_LDAP_BIND_PASSWORD=admin-password
```

### Monitoramento e Logs

#### Logs

- **Backend:** `backend/hp_management.log`
- **Celery:** Logs no console
- **Frontend:** Console do navegador

#### Monitoramento

- **Django Admin:** `http://localhost:8000/admin/`
- **API Documentation:** `http://localhost:8000/api/docs/`
- **Frontend:** `http://localhost:3000/`

### Backup e Manutenção

#### Backup do Banco de Dados

```bash
pg_dump hp_printer_db > backup_$(date +%Y%m%d).sql
```

#### Limpeza de Dados Antigos

```bash
# Executar tarefa de limpeza
python manage.py shell -c "from monitoring.tasks import cleanup_old_data; cleanup_old_data()"
```

### Solução de Problemas

#### Impressora não responde

1. **Verificar conectividade de rede**
2. **Verificar configuração SNMP**
3. **Testar conexão manual**

#### Alertas não funcionam

1. **Verificar configuração de email**
2. **Verificar workers Celery**
3. **Verificar regras de alerta**

#### Performance lenta

1. **Verificar índices do banco**
2. **Ajustar intervalos de monitoramento**
3. **Configurar cache Redis**

### Autor
MiniMax Agent

### Suporte

Para suporte técnico, consulte:
- Documentação da API: `/api/docs/`
- Logs do sistema
- Django Admin para configurações
