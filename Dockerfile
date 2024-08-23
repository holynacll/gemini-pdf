FROM python:3.11-slim-buster

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    telnet \
    netcat \
    git \
    wget \
    curl \
    sqlite3 \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    default-libmysqlclient-dev \
    && apt-get -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

# Define a porta em que a aplicação irá rodar
ENV PORT 8000
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["python", "main.py"]
