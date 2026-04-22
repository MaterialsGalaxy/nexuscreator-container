FROM python:3.13.12-trixie@sha256:b90dba245435afbe522568fb3dc93483cdbe54fbccb48516fb03b43b3e73c3bb AS base

WORKDIR /app
RUN pip install poetry==2.3.2 poetry-plugin-export==1.10.0
RUN python -m venv .venv
COPY poetry.lock pyproject.toml README.md ./
RUN poetry install --no-root --without=dev
COPY nexuscreator_container/ nexuscreator_container/
RUN .venv/bin/pip install .


FROM python:3.13.12-slim-trixie@sha256:8bc60ca09afaa8ea0d6d1220bde073bacfedd66a4bf8129cbdc8ef0e16c8a952 AS prod

ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
RUN addgroup --gid 500 --system nexuscreator
RUN adduser --system --gid 500 --uid 500 --home /app nexuscreator
COPY --from=base /app/.venv/ /app/.venv/
COPY resources/ /app/resources/
RUN chown -R nexuscreator:nexuscreator /app
USER nexuscreator


FROM base AS dev

ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
RUN poetry install --with=dev
COPY .flake8 .safety-policy.yml ./

CMD ["pytest", "tests", "--cov=nexuscreator_container", "--cov-report=term-missing", "--cov-report=xml"]
