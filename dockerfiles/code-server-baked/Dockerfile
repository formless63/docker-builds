FROM lscr.io/linuxserver/code-server:latest

USER root

ENV DEBIAN_FRONTEND=noninteractive \
    HOME=/config \
    PATH=/config/.local/bin:/config/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    PIPX_HOME=/config/.local/pipx \
    PIPX_BIN_DIR=/config/.local/bin \
    COMPOSER_HOME=/config/.composer \
    NPM_CONFIG_PREFIX=/config/.npm-global

RUN apt-get update && apt-get install -y --no-install-recommends \
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
    ripgrep \
    fd-find \
    bat \
    tmux \
    make \
    build-essential \
    pkg-config \
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
 && npm install -g pnpm npm-check-updates prettier eslint typescript tsx \
 && curl -fsSL https://getcomposer.org/installer -o /tmp/composer-setup.php \
 && php /tmp/composer-setup.php --install-dir=/usr/local/bin --filename=composer \
 && rm -f /tmp/composer-setup.php \
 && mkdir -p \
    /config/.local/bin \
    /config/.local/pipx \
    /config/.composer \
    /config/.npm \
    /config/.npm-global \
    /config/.cache \
    /config/shell \
    /workspace \
 && chown -R abc:abc /config /workspace \
 && git config --system init.defaultBranch main \
 && git config --system pull.rebase false \
 && printf '%s\n' \
    'export HISTFILE=/config/shell/.bash_history' \
    'export HISTSIZE=50000' \
    'export HISTFILESIZE=50000' \
    'shopt -s histappend' \
    'PROMPT_COMMAND="history -a; history -c; history -r; $PROMPT_COMMAND"' \
    'alias ll="ls -lah"' \
    'alias gs="git status"' \
    'alias gd="git diff"' \
    'alias grep="grep --color=auto"' \
    'alias cat="batcat --style=plain"' \
    >> /etc/bash.bashrc \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

USER abc
