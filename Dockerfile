FROM debian:bookworm

# 1. Install system dependencies, including CA certificates
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    texlive-extra-utils \
    texlive-latex-extra && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2. Set workdir
WORKDIR /app

# 3. Copy project files
COPY . /app

# 4. Create and activate virtual environment
RUN python3 -m venv /venv

# 5. Install Python dependencies using pip from virtual environment
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# 6. Expose port if needed
EXPOSE 8000

# 7. Add entrypoint or CMD if needed
CMD ["/venv/bin/python", "main.py"]
