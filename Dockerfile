FROM python:3.12.12-slim-bookworm 

RUN apt-get update && apt-get install -y tree nano git-all

RUN echo "# PS1 personalization\nPS1='${debian_chroot:+($debian_chroot)}\[\e[36m\]🦧 \u \[\e[32m\]⌛ \T \[\e[33m\]📁 \w\[\e[34m\] ~\\$\[\e[0m\] '" >> $HOME/.bashrc
RUN echo "# ls colors auto\nalias ls='ls --color=auto'" >> $HOME/.bashrc
RUN chmod +x $HOME/.bashrc && $HOME/.bashrc
RUN mkdir -p /var/run/celery && mkdir -p /var/log/celery

WORKDIR /retriever
RUN pip install --upgrade pip && pip install uv && uv venv --clear /venv 
ENV PATH="/venv/bin:$PATH"
COPY pyproject.toml uv.lock ./
RUN uv sync --active && uv run --active playwright install

# Install latest chrome dev package and fonts to support major charsets (Chinese, Japanese, Arabic, Hebrew, Thai and a few others)
# Note: this installs the necessary libs to make the bundled version of Chrome for Testing that Puppeteer
# installs, work.
RUN apt-get update \
    && apt-get install -y wget gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1 \
      --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY /app ./app

# CMD ["ls","-a"]
ENTRYPOINT ["/bin/bash"]
