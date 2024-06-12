# Use an official Python runtime as a parent image
FROM --platform=linux/arm64 python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages
RUN pip install streamlit

# Expose the port Streamlit runs on
EXPOSE 8501

CMD streamlit run app.py \
    --server.headless true \
    --browser.serverAddress="0.0.0.0" \
    --server.enableCORS false \
    --browser.gatherUsageStats false \
    --server.port 8501