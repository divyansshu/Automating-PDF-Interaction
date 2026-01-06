# Use Python 3.10
FROM python:3.10-slim

# Set the working directory to /code
WORKDIR /code

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy the requirements file first for caching
COPY --chown=user ./backend/requirements.txt /code/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the entire backend directory to /code/backend
# This ensures that 'from backend.app...' imports work correctly
COPY --chown=user ./backend /code/backend

# Expose the port
EXPOSE 7860

# Command to run the application
# We run from /code, so "backend.app.main" is a valid module path
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]
