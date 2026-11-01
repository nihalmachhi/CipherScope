FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
RUN mkdir -p /app/data /app/output/reports && chown -R 65534:65534 /app/data /app/output
ENV PYTHONDONTWRITEBYTECODE=1
USER 65534:65534
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "cipherscope.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
