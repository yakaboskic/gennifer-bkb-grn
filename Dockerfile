FROM julia:1.9

RUN apt-get update && apt-get install -y time python3-dev build-essential python3-pip

# add app user
RUN groupadd gennifer_user && useradd -ms /bin/bash -g gennifer_user gennifer_user

# Set the working directory to /app
WORKDIR /app

COPY ./requirements.txt /app

# Install the required packages
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# chown all the files to the app user
RUN chown -R gennifer_user:gennifer_user /app

USER gennifer_user

# Julia libs we want
COPY ./installPackages.jl /app
RUN julia installPackages.jl

# Copy the current directory contents into the container at /app
COPY . /app

# Start the Flask app
CMD ["flask", "--app", "pidc", "run", "--host", "0.0.0.0", "--debug"]
