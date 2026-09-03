FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md mcp_server.py ./
RUN pip install --no-cache-dir .
ENTRYPOINT ["python", "mcp_server.py"]
