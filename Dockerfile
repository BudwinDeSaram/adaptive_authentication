# BUILD
FROM alpine:3.18

# Install required dependencies for both flexfringe and Flask
RUN set -ex && \
    apk --no-cache --update add \
    sudo libstdc++ cmake g++ gcc bash git linux-headers libpthread-stubs make \
    libpq python3-dev py3-pip py3-wheel

# Create a non-root user and group
RUN addgroup -S appgroup && adduser -S 10005 -G appgroup

# Set up the working directory for flexfringe
WORKDIR /flexfringe

# Copy the flexfringe source code
COPY . ./

# Build flexfringe
RUN make clean all

# Set up the working directory for the Flask app
WORKDIR /app

# Copy the Flask application into the container
COPY authenticator/main.py ./

# Create necessary folders and adjust ownership to the non-root user
RUN mkdir -p /home/flexfringe/model && \
    chown -R 10005:appgroup /home/flexfringe /app /flexfringe

# Set up Python dependencies for Flask
RUN pip install flask user-agents 

# Switch to the non-root user
USER 10005

WORKDIR /home/flexfringe
COPY . .
RUN cp /flexfringe/flexfringe . 

# Expose the Flask application port
EXPOSE 8080

# Set the entry point to run the Flask application
ENTRYPOINT ["python3", "authenticator/main.py"]
