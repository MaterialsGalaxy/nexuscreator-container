FROM python:3.13.13-trixie@sha256:89a86b28b69c14fa431559849e0cc8139cf17258a0abaaa7d5d98bb2cf20ac1d AS base

WORKDIR /app
RUN pip install poetry==2.3.2 poetry-plugin-export==1.10.0
RUN python -m venv .venv
COPY poetry.lock pyproject.toml README.md ./
RUN poetry install --no-root --without=dev
COPY nexuscreator_container/ nexuscreator_container/
RUN .venv/bin/pip install .


FROM python:3.13.13-slim-trixie@sha256:9213d136547f0602c3337ff48291e937f9cc43060b3e123402cf2aaff1a08b75 AS prod

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

CMD ["pytest", "tests", "--cov=nexuscreator_container", "--cov-report=term-missing", "--cov-report=xml"]
