FROM oven/bun:latest AS frontend-builder
WORKDIR /app/src/ui

COPY src/ui/package.json src/ui/bun.lock* ./
RUN bun install

COPY src/ui ./
RUN bun run build

FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl unzip sudo && rm -rf /var/lib/apt/lists/*

# Install steampipe
RUN /bin/sh -c "$(curl -fsSL https://steampipe.io/install/steampipe.sh)"
RUN useradd -m -s /bin/bash cloudlens
USER cloudlens
WORKDIR /home/cloudlens/app
RUN steampipe plugin install aws

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

ENV PATH="/home/cloudlens/.local/bin:${PATH}"
COPY --chown=cloudlens:cloudlens src/ ./src/
ENV PYTHONPATH=/home/cloudlens/app/src

COPY --from=frontend-builder --chown=cloudlens:cloudlens /app/src/ui/dist ./src/ui/dist

EXPOSE 8000

CMD [ "python3", "-m", "api.run" ]