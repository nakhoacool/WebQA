# Use a specific version of Python
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /core

# Install dependencies
COPY deploy_req.txt .
RUN pip install --no-cache-dir -r deploy_req.txt

# Copy project
COPY . .

# Use Gunicorn as WSGI server with increased timeout and worker settings
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "3", "app:create_app()" ]

# Expose port
EXPOSE 5000