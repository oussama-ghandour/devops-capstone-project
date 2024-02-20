# insert code to python:3.9.16-slim as base image
FROM python:3.9-slim
# create working folder and insert code to install dependencies from requirements.txt
WORKDIR /app
# Copy requirements.txt to /app directory in the Docker image
COPY requirements.txt .
# install requirements using --no-cache-dir optiont to keep the image small
RUN pip install --no-cache-dir -r requirements.txt
# copy the application contents
COPY service/ ./service/
# switch to a non-root user
RUN useradd --uid 1000 theia && chown -R theia /app
USER theia
# expose port 8080 and the service
EXPOSE 8080
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--log-level=info", "service:app"]
