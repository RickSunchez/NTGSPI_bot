FROM python:3.9-slim

COPY req.txt .
RUN pip3 install --user -r req.txt

WORKDIR /app

COPY . .

ENV PATH=/root/.local:$PATH

CMD ["python3", "-u", "./main.py"]