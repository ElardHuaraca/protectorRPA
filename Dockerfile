FROM python

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD [ "/bin/bash","-c","python manage.py makemigrations; python manage.py migrate; python manage.py runserver 0.0.0.0:8000" ]