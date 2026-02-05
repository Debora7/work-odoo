# --------------------------
# Dockerfile final funcțional
# --------------------------
FROM linuxserver/libreoffice:25.8.1

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PATH="/opt/venv/bin:$PATH"

# --------------------------
# Install system deps (Alpine)
# --------------------------
RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    ttf-dejavu \
    libxrender libxext libx11 libsm libice mesa-gl \
    bash \
    curl \
    wget

# --------------------------
# Create virtual environment
# --------------------------
RUN python3 -m venv /opt/venv --system-site-packages \
 && /opt/venv/bin/pip install --upgrade pip

# --------------------------
# Python app
# --------------------------
WORKDIR /app
COPY requirements.txt /app/
RUN /opt/venv/bin/pip install --no-cache-dir -r /app/requirements.txt
COPY server.py /app/

EXPOSE 8084 8100

# --------------------------
# Run LibreOffice headless + Python server
# --------------------------
CMD soffice \
    --headless \
    --invisible \
    --nologo \
    --nodefault \
    --nofirststartwizard \
    --accept="socket,host=0.0.0.0,port=8100;urp;" & \
    exec python3 /app/server.py
