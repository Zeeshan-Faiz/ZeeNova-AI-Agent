# Use an official slim Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy all files and folders into the container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Optional: Streamlit-specific env vars
ENV STREAMLIT_PORT=7860
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expose the default Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]