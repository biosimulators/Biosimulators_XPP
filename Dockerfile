# Base OS
FROM python:3.9-slim-buster

ARG VERSION="0.0.5"
ARG SIMULATOR_VERSION=8.0

# metadata
LABEL \
    org.opencontainers.image.title="XPP" \
    org.opencontainers.image.version="${SIMULATOR_VERSION}" \
    org.opencontainers.image.description="Tool for solving differential, difference, delay, functional, and stochastic equations and boundary value problems." \
    org.opencontainers.image.url="http://www.math.pitt.edu/~bard/xpp/xpp.html" \
    org.opencontainers.image.documentation="http://www.math.pitt.edu/~bard/xpp/xpp.html" \
    org.opencontainers.image.source="https://github.com/Ermentrout/xppaut" \
    org.opencontainers.image.authors="BioSimulators Team <info@biosimulators.org>" \
    org.opencontainers.image.vendor="BioSimulators Team" \
    org.opencontainers.image.licenses="SPDX:GPL-3.0-only" \
    \
    base_image="python:3.9-slim-buster" \
    version="${VERSION}" \
    software="XPP" \
    software.version="${SIMULATOR_VERSION}" \
    about.summary="Tool for solving differential, difference, delay, functional, and stochastic equations and boundary value problems." \
    about.home="http://www.math.pitt.edu/~bard/xpp/xpp.html" \
    about.documentation="http://www.math.pitt.edu/~bard/xpp/xpp.html" \
    about.license_file="https://github.com/Ermentrout/xppaut/blob/master/LICENSE" \
    about.license="SPDX:GPL-3.0-only" \
    about.tags="kinetic modeling,dynamical simulation,systems biology,biochemical networks,XPP,XPPAUT,SED-ML,COMBINE,OMEX,BioSimulators" \
    maintainer="BioSimulators Team <info@biosimulators.org>"

# Install XPP
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        wget \
        make \
        gcc \
        libx11-dev \
        libc6-dev \
        libx11-6 \
        libc6 \
    \
    && cd /tmp \
    && wget http://www.math.pitt.edu/~bard/bardware/xppaut_latest.tar.gz \
    && mkdir xpp \
    && tar zxvf xppaut_latest.tar.gz --directory xpp \
    && cd xpp \
    && make \
    && make install \
    \
    && cd /tmp \
    && rm xppaut_latest.tar.gz \
    && rm -r xpp \
    \
    && apt-get remove -y \
        wget \
        make \
        gcc \
        libx11-dev \
        libc6-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# fonts for matplotlib
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Copy code for command-line interface into image and install it
COPY . /root/Biosimulators_XPP
RUN pip install /root/Biosimulators_XPP \
    && rm -rf /root/Biosimulators_XPP
ENV VERBOSE=0 \
    MPLBACKEND=PDF
RUN mkdir -p /.config/matplotlib \
    && mkdir -p /.cache/matplotlib \
    && chmod ugo+rw /.config/matplotlib \
    && chmod ugo+rw /.cache/matplotlib

# Entrypoint
ENTRYPOINT ["biosimulators-xpp"]
CMD []
