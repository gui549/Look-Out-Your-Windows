FROM python:3.8-buster

RUN set -ex && mkdir /repo
WORKDIR /repo

COPY docker-requirements.txt ./requirements.txt
RUN pip install --upgrade pip~=21.0.0
RUN pip install -r requirements.txt

COPY __init__.py ./__init__.py
COPY HiDT_module.py ./HiDT_module.py
COPY styles.txt ./styles.txt
COPY configs/ ./configs
COPY hidt/ ./hidt
COPY images/ ./images
COPY trained_models/ ./trained_models

ENV PYTHONPATH /repo
CMD ["python3", "./HiDT_module.py"]