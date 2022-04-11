FROM python:3.8.13-slim

ARG FUNCTION_DIR="/function"

#Install aws-lambda-cpp build dependencies
RUN apt-get update && \
    apt-get install -y \
    g++ \
    make \
    cmake \
    unzip \
    libcurl4-openssl-dev

#Create function directory
RUN mkdir -p ${FUNCTION_DIR}

#Install the runtime interface client
RUN pip install \
    --target ${FUNCTION_DIR} \
    awslambdaric

WORKDIR ${FUNCTION_DIR}

#Copy function code
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/usr/local/bin/python", "-m", "awslambdaric"]
CMD [ "lambda_handler.handler" ]