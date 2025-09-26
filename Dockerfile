FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema necessárias para o Firebird
RUN apt-get update && apt-get install -y \
    firebird-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]