FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=America/Argentina/Buenos_Aires
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app --home-dir /app app
COPY requirements-docker.txt ./
RUN python -m pip install --no-cache-dir -r requirements-docker.txt
COPY --chown=app:app . .
RUN mkdir -p /app/data/emisiones && chown -R app:app /app/data
USER app
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)" || exit 1
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--browser.gatherUsageStats=false"]
