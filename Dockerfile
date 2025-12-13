# Production Dockerfile for Cerberus Security Scanner
# Includes all security scanning tools

FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    gnupg \
    ca-certificates \
    default-jdk \
    maven \
    unzip \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Install Syft (for SBOM and Dependency Consistency)
RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

WORKDIR /cerberus

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install security tools stage
FROM base AS tools

# Install Trivy
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v0.48.0

# Install Grype
RUN curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin v0.74.0

# Install Gitleaks
RUN wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.1/gitleaks_8.18.1_linux_x64.tar.gz && \
    tar -xzf gitleaks_8.18.1_linux_x64.tar.gz && \
    mv gitleaks /usr/local/bin/ && \
    rm gitleaks_8.18.1_linux_x64.tar.gz

# Install Semgrep
RUN pip install --no-cache-dir semgrep

# Install Hadolint
RUN wget https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64 && \
    chmod +x hadolint-Linux-x86_64 && \
    mv hadolint-Linux-x86_64 /usr/local/bin/hadolint

# Install Checkov
RUN pip install --no-cache-dir checkov

# Install Kubescape
RUN curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash

# Install Kubeaudit
RUN wget https://github.com/Shopify/kubeaudit/releases/download/v0.22.1/kubeaudit_0.22.1_linux_amd64.tar.gz && \
    tar -xzf kubeaudit_0.22.1_linux_amd64.tar.gz && \
    mv kubeaudit /usr/local/bin/ && \
    rm kubeaudit_0.22.1_linux_amd64.tar.gz

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install OWASP Dependency-Check
RUN wget https://github.com/jeremylong/DependencyCheck/releases/download/v9.0.7/dependency-check-9.0.7-release.zip && \
    unzip dependency-check-9.0.7-release.zip && \
    mv dependency-check /opt/ && \
    ln -s /opt/dependency-check/bin/dependency-check.sh /usr/local/bin/dependency-check && \
    rm dependency-check-9.0.7-release.zip

# Install SpotBugs
RUN wget https://github.com/spotbugs/spotbugs/releases/download/4.8.3/spotbugs-4.8.3.tgz && \
    tar -xzf spotbugs-4.8.3.tgz && \
    mv spotbugs-4.8.3 /opt/spotbugs && \
    chmod +x /opt/spotbugs/bin/spotbugs && \
    ln -s /opt/spotbugs/bin/spotbugs /usr/local/bin/spotbugs && \
    rm spotbugs-4.8.3.tgz

# Final stage
FROM tools

# Copy Cerberus application
COPY . /cerberus/

# Create reports directory
RUN mkdir -p /cerberus/reports

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/cerberus:${PATH}"

# Make cerberus.py executable
RUN chmod +x /cerberus/cerberus.py

# Create non-root user for security
RUN useradd -m -u 1000 cerberus && \
    chown -R cerberus:cerberus /cerberus

USER cerberus

# Set entrypoint
ENTRYPOINT ["python3", "/cerberus/cerberus.py"]

# Default command (show help)
CMD ["--help"]
