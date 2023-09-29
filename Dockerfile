# Base image
FROM python:3.10-slim-buster

# Install system dependencies
RUN apt-get update \
    && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to the PATH
ENV PATH="/root/.local/bin:${PATH}"

# Set the working directory
WORKDIR /app

# Copy the poetry.lock and pyproject.toml files
COPY poetry.lock pyproject.toml ./

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the Flask app code
COPY /api .

# Expose the Flask app port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
