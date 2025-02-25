FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the script and dependencies
COPY ip-tool.py /app/ip-tool.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the script on container startup
CMD ["python", "/app/ip-tool.py", "--check-collision", "collected_ips.json"]
