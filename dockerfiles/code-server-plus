FROM lscr.io/linuxserver/code-server:latest

USER root

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    bash \
    ca-certificates \
    curl \
    wget \
    git \
    unzip \
    zip \
    xz-utils \
    nano \
    vim \
    less \
    jq \
    yq \
    tree \
    file \
    procps \
    htop \
    btop \
    net-tools \
    iputils-ping \
    dnsutils \
    rsync \
    openssh-client \
    sudo \
    ripgrep \
    fd-find \
    tmux \
    screen \
    make \
    build-essential \
    pkg-config \
    software-properties-common \
    gnupg \
    lsb-release \
    apt-transport-https \
    sqlite3 \
    postgresql-client \
    default-mysql-client \
    redis-tools \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    pipx \
    nodejs \
    npm \
    php-cli \
    php-common \
    php-curl \
    php-mbstring \
    php-xml \
    php-zip \
    php-gd \
    php-intl \
    php-bcmath \
    php-soap \
    php-sqlite3 \
    php-mysql \
    php-pgsql \
    php-redis \
    php-imagick \
    php-opcache \
    php-xdebug \
 && rm -rf /var/lib/apt/lists/*

RUN npm install -g \
    pnpm \
    npm-check-updates \
    eslint \
    prettier \
    typescript \
    tsx

RUN curl -fsSL https://getcomposer.org/installer -o /tmp/composer-setup.php \
 && php /tmp/composer-setup.php --install-dir=/usr/local/bin --filename=composer \
 && rm -f /tmp/composer-setup.php

RUN mkdir -p /config/.local/bin /config/.composer /config/.npm /config/.cache /workspace \
 && chown -R abc:abc /config /workspace

ENV PATH="/config/.local/bin:/config/.npm-global/bin:${PATH}" \
    PIPX_HOME="/config/.local/pipx" \
    PIPX_BIN_DIR="/config/.local/bin" \
    COMPOSER_HOME="/config/.composer" \
    NPM_CONFIG_PREFIX="/config/.npm-global"

RUN pipx ensurepath \
 && pipx install poetry \
 && pipx install uv

USER abc
