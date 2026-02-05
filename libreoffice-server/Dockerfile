FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LO_VERSION=25.8.4
ENV LO_URL=https://download.documentfoundation.org/libreoffice/stable/25.8.4/deb/x86_64/LibreOffice_25.8.4_Linux_x86-64_deb.tar.gz
ENV LO_PATH=/opt/libreoffice25.8.4/program/soffice
ENV PYTHONPATH=$LO_PATH

# Install system deps
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    python3 \
    python3-pip \
    python3-uno \
    fonts-dejavu \
    libxrender1 libxext6 libxt6 libx11-6 libsm6 libice6 libglu1-mesa libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Download & install LibreOffice official .deb
WORKDIR /tmp
# Descarcă tar.gz oficial
RUN wget https://download.documentfoundation.org/libreoffice/stable/25.8.4/deb/x86_64/LibreOffice_25.8.4_Linux_x86-64_deb.tar.gz \
 && tar -xzf LibreOffice_25.8.4_Linux_x86-64_deb.tar.gz \
 && dpkg -i LibreOffice_25.8.4_Linux_x86-64_deb/DEBS/*.deb || true \
 && apt-get update && apt-get install -y -f \
 && dpkg -i LibreOffice_25.8.4.2_Linux_x86-64_deb/DEBS/*.deb \
 && rm -rf /tmp/LibreOffice_25.8.4_Linux_x86-64_deb*

# Copy Python app + install deps
WORKDIR /app
COPY requirements.txt /app/
RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt
COPY server.py /app/

EXPOSE 8084 8100

# Run headless LibreOffice + Python server
CMD soffice \
    --headless \
    --invisible \
    --nologo \
    --nodefault \
    --nofirststartwizard \
    --accept="socket,host=0.0.0.0,port=8100;urp;" & \
    exec python3 server.py
