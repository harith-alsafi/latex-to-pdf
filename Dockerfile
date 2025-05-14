FROM debian:bookworm

# Install only required TeX tools, Python, and build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-xetex \
    texlive-fonts-extra \
    python3 \
    python3-pip \
    python3-venv \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy project files
COPY . /app

# Set up a virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose API port
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
