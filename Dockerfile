FROM python:3.13-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Variável de ambiente para o FastAPI
ENV PYTHONPATH=/app

# Expor porta
EXPOSE 8000

# Rodar FastAPI
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]

