# Pull the base image with python 3.8 as a runtime for your Lambda
FROM public.ecr.aws/lambda/python:3.7

ENV NUMBA_CACHE_DIR=/tmp/numba_cache

ENV SNDFILE_VERSION=1.0.28

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
    ffmpeg libsndfile1-dev libsndfile1 \
    && yum clean all

RUN pip install musdb museval
RUN pip install lambda-multiprocessing
RUN pip install librosa
RUN pip install SoundFile
RUN pip install spleeter
RUN pip install webvtt

# ffmepg 파일 복사
COPY ffmpeg.tar.xz .
RUN tar -xf ffmpeg.tar.xz
# ffmepg 관련 파일 경로 설정
RUN mv ffmpeg-*-amd64-static/* /usr/bin

# Copy the earlier created requirements.txt file to the container
COPY requirements.txt ./

# Install the python requirements from requirements.txt
RUN python3.7 -m pip install -r requirements.txt
# Replace Pillow with Pillow-SIMD to take advantage of AVX2
RUN pip uninstall -y pillow && CC="cc -mavx2" pip install -U --force-reinstall pillow-simd

# Copy the earlier created app.py file to the container
COPY app.py ./ 
COPY trained-model ./
COPY spleeter-2.3.0 ../lang/lib/python3.7/site-packages/

ENV SNDFILE_VERSION=1.0.28
WORKDIR /tmp

RUN mkdir -p "/tmp/sndfile"

RUN yum install -y autoconf autogen automake build-essential libasound2-dev \
  libflac-dev libogg-dev libtool libvorbis-dev libopus-dev pkg-config gcc-c++

WORKDIR "/tmp/sndfile"

RUN curl -L -o "libsndfile-${SNDFILE_VERSION}.tar.gz" "http://www.mega-nerd.com/libsndfile/files/libsndfile-${SNDFILE_VERSION}.tar.gz"

RUN tar xf "libsndfile-${SNDFILE_VERSION}.tar.gz"

WORKDIR "/tmp/sndfile/libsndfile-${SNDFILE_VERSION}"

RUN ./configure --prefix=/opt/
RUN make
RUN make install

# set workdir back
WORKDIR /var/task

# Set the CMD to your handler
CMD ["app.lambda_handler"]