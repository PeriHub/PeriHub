FROM python:3.7

RUN pip install fastapi uvicorn matplotlib scipy numpy aiofiles pandas

WORKDIR /app/

EXPOSE 80

COPY ./app /app

CMD ["uvicorn", "modelGeneratorControl:app", "--host", "0.0.0.0", "--port", "80", "--reload", "--reload-dir", "/app"]