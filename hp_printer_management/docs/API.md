# API Documentation

## Sistema de Gestão de Impressoras HP - API REST

### Base URL
```
http://localhost:8000/api
```

### Autenticação

O sistema utiliza autenticação JWT (JSON Web Token).

#### Login
```http
POST /auth/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

**Resposta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

#### Usar Token
```http
Authorization: Bearer <access_token>
```

### Endpoints Principais

#### Impressoras

**Listar impressoras**
```http
GET /printers/
```

**Obter impressora**
```http
GET /printers/{id}/
```

**Criar impressora**
```http
POST /printers/
Content-Type: application/json

{
  "name": "HP LaserJet Pro M404n",
  "model": "M404n",
  "serial_number": "CNBB123456",
  "ip_address": "192.168.1.100",
  "printer_type": "laser",
  "location": "Escritório 1",
  "department": "TI"
}
```

**Testar conexão**
```http
POST /printers/{id}/test_connection/
```

**Descobrir impressoras**
```http
POST /printers/discover/
Content-Type: application/json

{
  "ip_range": "192.168.1.0/24",
  "timeout": 5,
  "snmp_community": "public"
}
```

#### Alertas

**Listar alertas**
```http
GET /alerts/
```

**Reconhecer alerta**
```http
POST /alerts/{id}/acknowledge/
```

**Resolver alerta**
```http
POST /alerts/{id}/resolve/
Content-Type: application/json

{
  "resolution_notes": "Problema resolvido substituindo toner"
}
```

**Listar regras de alerta**
```http
GET /alert-rules/
```

**Criar regra de alerta**
```http
POST /alert-rules/
Content-Type: application/json

{
  "name": "Toner Baixo",
  "trigger_type": "supply_low",
  "severity": "medium",
  "threshold_value": 20,
  "send_email": true,
  "send_sms": false,
  "cooldown_minutes": 60
}
```

#### Monitoramento

**Status das impressoras**
```http
GET /monitoring/printer-status/
```

**Métricas de performance**
```http
GET /monitoring/performance-metrics/
```

**Histórico de manutenção**
```http
GET /monitoring/maintenance-records/
```

#### Relatórios

**Listar relatórios**
```http
GET /reports/
```

**Gerar relatório**
```http
POST /reports/
Content-Type: application/json

{
  "name": "Consumo Mensal",
  "report_type": "consumption",
  "format": "pdf",
  "date_from": "2023-11-01",
  "date_to": "2023-11-30",
  "printers": [1, 2, 3]
}
```

**Download relatório**
```http
GET /reports/{id}/download/
```

#### Usuários

**Listar usuários**
```http
GET /users/
```

**Perfil do usuário atual**
```http
GET /users/profile/
```

**Atualizar perfil**
```http
PATCH /users/profile/
Content-Type: application/json

{
  "first_name": "João",
  "last_name": "Silva",
  "email": "joao.silva@example.com"
}
```

**Alterar senha**
```http
POST /users/change_password/
Content-Type: application/json

{
  "old_password": "senha_atual",
  "new_password": "nova_senha",
  "confirm_password": "nova_senha"
}
```

### Filtros e Paginação

#### Filtros
Todos os endpoints de listagem suportam filtros via query parameters:

```http
GET /printers/?status=active&printer_type=laser&search=HP
```

#### Paginação
```http
GET /printers/?page=2&page_size=20
```

**Resposta paginada:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/printers/?page=3",
  "previous": "http://localhost:8000/api/printers/?page=1",
  "results": [...]
}
```

#### Ordenação
```http
GET /printers/?ordering=-created_at
GET /printers/?ordering=name
```

### Códigos de Status HTTP

- `200` - OK
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

### Tratamento de Erros

**Formato de erro padrão:**
```json
{
  "error": "Mensagem de erro",
  "details": {
    "field_name": ["Erro específico do campo"]
  }
}
```

### WebSockets (Opcional)

Para notificações em tempo real:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications/');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Nova notificação:', data);
};
```

### Documentação Interativa

Acesse a documentação interativa da API:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`

### Autor
MiniMax Agent
