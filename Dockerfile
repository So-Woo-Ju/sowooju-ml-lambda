# Pull the base image with python 3.8 as a runtime for your Lambda
FROM public.ecr.aws/lambda/python:3.8

# Install OS packages for Pillow-SIMD
RUN yum install -y tar gzip xz zlib unzip freetype-devel \
    gcc \
    ghostscript \
    lcms2-devel \
    libffi-devel \
    libimagequant-devel \
    libjpeg-devel \
    libraqm-devel \
    libtiff-devel \
    libwebp-devel \
    make \
    openjpeg2-devel \
    rh-python36 \
    rh-python36-python-virtualenv \
    sudo \
    tcl-devel \
    tk-devel \
    tkinter \
    which \
    xorg-x11-server-Xvfb \
    zlib-devel \
    ffmpeg libsndfile \
    && yum clean all

RUN pip install musdb museval
RUN pip install spleeter

# ffmepg 파일 복사
COPY ffmpeg.tar.xz .
RUN tar -xf ffmpeg.tar.xz
# ffmepg 관련 파일 경로 설정
RUN mv ffmpeg-*-amd64-static/* /usr/bin

# Copy the earlier created requirements.txt file to the container
COPY requirements.txt ./

# Install the python requirements from requirements.txt
RUN python3.8 -m pip install -r requirements.txt
# Replace Pillow with Pillow-SIMD to take advantage of AVX2
RUN pip uninstall -y pillow && CC="cc -mavx2" pip install -U --force-reinstall pillow-simd

# Copy the earlier created app.py file to the container
COPY app.py ./ 
COPY trained-model ./

# Set the CMD to your handler
CMD ["app.lambda_handler"]