FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY sentor_mcp/ ./sentor_mcp/

RUN pip install --no-cache-dir -e ".[http]"

ENV SENTOR_BASE_URL=https://sentor.app/api

EXPOSE 8080

CMD ["python", "-m", "sentor_mcp.server_http"]
