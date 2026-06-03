# CaloCount Backend

API REST para o contador de calorias CaloCount. Desenvolvida com FastAPI, SQLAlchemy e Celery.

## Stack

- **FastAPI** — framework web
- **SQLAlchemy** — ORM
- **MySQL** — banco de dados (desenvolvimento)
- **PostgreSQL** — banco de dados (produção)
- **Celery + Redis** — processamento de tasks (síncronas em dev)
- **Gemini Pro Vision** — análise de refeições por foto

## Setup

### 1. Criar e ativar virtualenv

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` com suas credenciais de MySQL, Redis e Gemini API Key.

### 4. Criar o banco de dados MySQL

```sql
CREATE DATABASE calocount CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;.
```

### 5. Rodar a aplicação

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`.

Documentação interativa: `http://localhost:8000/docs`

---

## Estrutura

```
app/
├── main.py              # Entry point FastAPI
├── config.py            # Settings via pydantic-settings
├── db/
│   ├── base.py          # SQLAlchemy Base
│   ├── session.py       # Dependency get_db
│   └── init_db.py       # Cria tabelas
├── models/
│   ├── user.py          # Model User
│   └── calorie_log.py   # Model CalorieLog
├── schemas/
│   ├── auth.py          # Schemas de autenticação
│   ├── user.py          # Schema UserOut
│   └── calorie_log.py   # Schemas de registro de calorias
├── api/
│   └── endpoints/
│       ├── auth.py      # /auth/register, /auth/login, /auth/me
│       ├── calories.py  # CRUD /calories/ + summary
│       └── ai.py        # /ai/analyze (foto → Gemini)
├── tasks/
│   ├── celery_app.py    # Celery instance
│   └── ai_tasks.py      # Task de análise por IA
└── core/
    ├── security.py      # JWT + hash de senha
    └── deps.py          # Dependências FastAPI
```

---

## Endpoints (Sessão 1)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/auth/register` | Cadastrar usuário |
| POST | `/auth/login` | Login → JWT |
| GET | `/auth/me` | Dados do usuário atual |

## Endpoints (Sessão 2)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/calories/` | Registrar refeição |
| GET | `/calories/` | Listar registros |
| GET | `/calories/summary` | Total por dia |
| DELETE | `/calories/{id}` | Remover registro |
| POST | `/ai/analyze` | Analisar foto com Gemini |
