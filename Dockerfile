FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd --system gameday \
    && useradd --system --gid gameday --create-home gameday

COPY pyproject.toml README.md ./
COPY src ./src
COPY scenarios ./scenarios

RUN pip install --upgrade pip \
    && pip install .

RUN mkdir -p /app/reports \
    && chown -R gameday:gameday /app

USER gameday

ENTRYPOINT ["gameday"]
CMD ["scenarios/pod-crash-dry-run.yaml"]
