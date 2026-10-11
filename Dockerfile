FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY cipherscope ./cipherscope
COPY experiments ./experiments
RUN pip install --no-cache-dir . && mkdir -p /app/data /app/output/reports && chown -R 65534:65534 /app/data /app/output
ENV PYTHONDONTWRITEBYTECODE=1
USER 65534:65534
EXPOSE 8000
CMD ["uvicorn", "cipherscope.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
