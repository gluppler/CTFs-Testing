FROM python:3.12

# Install packages
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

#create user
RUN groupadd --system app && useradd --system --gid app --create-home --home-dir /home/app app

# Upgrade pip
RUN python -m pip install --upgrade pip

# Setup app
RUN mkdir -p /app

# Switch working environment
WORKDIR /app


COPY challenge/requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt

# Add application
COPY challenge .
RUN mkdir -p /app/uploads && chown -R app:app /app
# Copy configs
COPY challenge/config/supervisord.conf /etc/supervisord.conf

# Expose port the server is reachable on
EXPOSE 5000

# Disable pycache
ENV PYTHONDONTWRITEBYTECODE=1

# Run supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]