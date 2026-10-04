FROM lscr.io/linuxserver/code-server:latest

USER root
ARG TARGETARCH
ARG NODE_VERSION=24.19.0

# /config is the volume linuxserver images persist, so it is the right home for
# things a user installs at runtime (their pipx/composer/npm globals survive
# restarts) but the wrong place to bake anything at build time: a user's
# `-v ./config:/config` bind mount shadows whatever we put there. Tools we ship
# go to /usr/local instead; the prefixes below are for runtime installs only.
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
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Official Node binaries keep the CLI tools on a supported Node release rather
# than the older distro Node. Verify the archive against official checksums.
RUN case "$TARGETARCH" in amd64) node_arch=x64 ;; arm64) node_arch=arm64 ;; *) exit 1 ;; esac \
 && node_archive="node-v${NODE_VERSION}-linux-${node_arch}.tar.xz" \
 && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/${node_archive}" -o "/tmp/${node_archive}" \
 && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt" -o /tmp/node-shasums \
 && grep " ${node_archive}\$" /tmp/node-shasums > /tmp/node-selected-shasum \
 && (cd /tmp && sha256sum -c node-selected-shasum) \
 && tar -xJf "/tmp/${node_archive}" -C /usr/local --strip-components=1 \
 && npm install -g --prefix /usr/local \
    pnpm@12.9.1 npm-check-updates@23.1.0 prettier@3.9.9 \
    eslint@10.12.0 typescript@7.0.2 tsx@4.23.15 \
 && mkdir -p /usr/local/share/baked-tools \
 && npm list -g --prefix /usr/local --depth=0 --json > /usr/local/share/baked-tools/npm.json \
 && dpkg-query -W > /usr/local/share/baked-tools/dpkg.txt \
 && node --version > /usr/local/share/baked-tools/node.txt \
 && (phpdismod xdebug || echo "WARNING: could not disable xdebug") \
 && curl -fsSL https://getcomposer.org/installer -o /tmp/composer-setup.php \
 && curl -fsSL https://composer.github.io/installer.sig -o /tmp/composer-installer.sig \
 && php -r 'if (hash_file("sha384", "/tmp/composer-setup.php") !== trim(file_get_contents("/tmp/composer-installer.sig"))) { fwrite(STDERR, "Composer installer checksum mismatch\n"); exit(1); }' \
 && php /tmp/composer-setup.php --install-dir=/usr/local/bin --filename=composer \
 && composer --version > /usr/local/share/baked-tools/composer.txt \
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
  'export HISTTIMEFORMAT="%F %T "' \
  'shopt -s histappend' \
  'PROMPT_COMMAND="history -a; history -n; $PROMPT_COMMAND"' \
  'alias ll="ls -lah"' \
  'alias gs="git status"' \
  'alias gd="git diff"' \
  'alias grep="grep --color=auto"' \
  'alias cat="batcat --style=plain"' \
  'alias fd="fdfind"' \
  >> /etc/bash.bashrc \
 && rm -rf /tmp/* /var/tmp/* /config/.npm/_cacache /config/.npm/_logs
