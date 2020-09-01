FROM python:3.7-slim as build-step

RUN pip install --no-cache-dir poetry

COPY . /build/

WORKDIR /build

RUN poetry build

FROM python:3.7-slim as final-step

COPY --from=build-step /build/dist/shaman_api-1.0.2-py3-none-any.whl /tmp/

RUN pip install --no-cache-dir /tmp/shaman_api-1.0.2-py3-none-any.whl

ENTRYPOINT ["shaman-api", "prod"]
