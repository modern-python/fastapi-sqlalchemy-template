FROM python:3.9-buster
RUN pip3 install --upgrade pip
RUN useradd --no-create-home --gid root runner

WORKDIR /code

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R runner:root /code && chmod -R g=u /code

USER runner

EXPOSE 8000

ENTRYPOINT [ "/code/docker-entrypoint.sh" ]
