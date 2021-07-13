ARG ENVIRONMENT="dev"
FROM python:3.9-buster AS app-prod
RUN pip3 install --upgrade pip
RUN useradd --no-create-home --gid root runner

WORKDIR /code

COPY requirements.prod.txt .
RUN pip3 install --no-cache-dir -r requirements.prod.txt

FROM app-prod AS app-dev
COPY requirements.dev.txt .
RUN pip3 install --no-cache-dir -r requirements.dev.txt

FROM app-${ENVIRONMENT} AS app

COPY . .

RUN chown -R runner:root /code && chmod -R g=u /code

USER runner

EXPOSE 8000

ENTRYPOINT [ "/code/docker-entrypoint.sh" ]
