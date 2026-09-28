# Seemingly cannot use slim as it doesn't find a compiler for numpy's c code
FROM python:3.14.7-trixie@sha256:0876e54cf728d89fd9d0fdaf5837b9ee879ea5fbbd6fd0cddbe5eb0cce3f5f9e AS base

WORKDIR /app
RUN pip install poetry==2.3.2 poetry-plugin-export==1.10.0
RUN python -m venv .venv
COPY poetry.lock pyproject.toml README.md ./
RUN poetry install --no-root --without=dev
COPY nexuscreator_container/ nexuscreator_container/
RUN .venv/bin/pip install .


FROM python:3.14.7-slim-trixie@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d AS prod

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
COPY .flake8 ./
COPY resources/ /app/resources/

CMD ["pytest", "tests", "--cov=nexuscreator_container", "--cov-report=term-missing", "--cov-report=xml"]
