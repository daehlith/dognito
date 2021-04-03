FROM python:3.9.3-slim
RUN pip install aiohttp==3.7.4.post0 cryptography==3.4.7 pyjwt==2.0.1
WORKDIR /dognito
COPY . .
ENTRYPOINT ["python3", "-u", "dognito.py"]
