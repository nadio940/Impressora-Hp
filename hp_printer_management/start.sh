#!/bin/bash

# Script de inicialização do sistema HP Printer Management
# Autor: MiniMax Agent

set -e

echo "=== Sistema de Gestão de Impressoras HP ==="
echo "Inicializando sistema..."

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "Erro: Docker não encontrado. Por favor, instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Erro: Docker Compose não encontrado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "Arquivo .env não encontrado. Copiando do template..."
    cp .env.example .env
    echo "Por favor, edite o arquivo .env com suas configurações antes de continuar."
    echo "Depois execute: ./start.sh"
    exit 1
fi

echo "Construindo imagens Docker..."
docker-compose build

echo "Iniciando serviços..."
docker-compose up -d

echo "Aguardando serviços iniciarem..."
sleep 10

echo "Executando migrações do banco de dados..."
docker-compose exec -T backend python manage.py migrate

echo "Coletando arquivos estáticos..."
docker-compose exec -T backend python manage.py collectstatic --noinput

echo "Criando dados iniciais..."
docker-compose exec -T backend python manage.py loaddata initial_data.json || true

echo ""
echo "=== Sistema inicializado com sucesso! ==="
echo ""
echo "Acesse o sistema em:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000/api"
echo "  Django Admin: http://localhost:8000/admin"
echo "  API Docs: http://localhost:8000/api/docs"
echo ""
echo "Para criar um superusuário, execute:"
echo "  docker-compose exec backend python manage.py createsuperuser"
echo ""
echo "Para parar o sistema:"
echo "  docker-compose down"
echo ""
echo "Para ver logs:"
echo "  docker-compose logs -f"
echo ""
