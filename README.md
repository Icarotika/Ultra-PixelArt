# Assistente Acadêmica Web (Secretaria de Faculdade)

Projeto simples e funcional dividido em **frontend** (HTML/CSS/JS puro) e **backend** (FastAPI).

## Estrutura

```bash
.
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
└── dados.json
```

## Requisitos

- Python 3.10+
- Navegador web moderno

## Como rodar

### 1) Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload
```

API disponível em: `http://localhost:8000`

### 2) Frontend (HTML/CSS/JS)

Abra o arquivo `frontend/index.html` no navegador.

> Opcional (recomendado): servir com um servidor local para evitar limitações de arquivo local:

```bash
cd frontend
python -m http.server 5500
```

Depois acesse: `http://localhost:5500`

## Como funciona

- O frontend envia a pergunta do usuário para `POST /chat` via `fetch`.
- O backend carrega `dados.json` com regras da secretaria.
- O backend cria um **prompt base** com identidade e regras fixas.
- Se a variável `OPENAI_API_KEY` estiver definida, tenta responder via API da OpenAI.
- Caso contrário (ou em falha externa), usa um fallback local orientado por tópicos do JSON.
- Se a pergunta não tiver cobertura no `dados.json`, retorna:
  - `Não possuo dados suficientes para responder essa pergunta com segurança.`

## Variáveis de ambiente (opcional)

```bash
export OPENAI_API_KEY="sua_chave"
export OPENAI_MODEL="gpt-4o-mini"
```

Sem chave, o sistema continua funcional em modo local.
