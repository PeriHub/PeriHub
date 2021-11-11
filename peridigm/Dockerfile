FROM trilinos 

ARG EXTERNAL
ENV EXTERNAL $EXTERNAL
# ARG if [ "$EXTERNAL" = "False" ]; then \
#         GITLAB_USER; GITLAB_TOKEN;\
#     fi
# ENV if [ "$EXTERNAL" = "False" ]; then \
#         GITLAB_USER $GITLAB_USER; GITLAB_TOKEN $GITLAB_TOKEN;\
#     fi
ARG GITLAB_USER
ENV GITLAB_USER $GITLAB_USER
ARG GITLAB_TOKEN
ENV GITLAB_TOKEN $GITLAB_TOKEN

ENV HOME /root

WORKDIR /

RUN apt-get -yq update
RUN apt-get -yq install git
RUN apt-get -yq install openmpi-bin
RUN apt-get -yq install openssh-server
RUN apt-get -yq install libboost1.55
RUN if [ "$EXTERNAL" = "False" ]; then \
        git clone https://${GITLAB_USER}:${GITLAB_TOKEN}@gitlab.dlr.de/AG-SATT/peridigmDev.git peridigm; else \
        git clone https://github.com/PeriDoX/peridigm.git peridigm; \
    fi

# #Build Peridigm
# RUN mkdir peridigm
# WORKDIR /peridigm
# ADD src src
# ADD test test
# ADD scripts scripts
# ADD examples examples 
# ADD CMakeLists.txt .
RUN mkdir /peridigm/build

WORKDIR /peridigm/build/
RUN cmake \
    -D CMAKE_BUILD_TYPE:STRING=Release \
    -D CMAKE_INSTALL_PREFIX:PATH=/usr/local/peridigm \
    -D CMAKE_CXX_FLAGS:STRING="-O2 -Wall -std=c++14 -pedantic -Wno-long-long -ftrapv -Wno-deprecated" \
    -D TRILINOS_DIR:PATH=/usr/local/trilinos \
    -D CMAKE_CXX_COMPILER:STRING="mpicxx" \
    -D USE_DAKOTA:BOOL=OFF \
    ..; \
    make && make install; 
    # cd ..; \
    # rm -rf peridigm

VOLUME /output
WORKDIR /output
ENV LD_LIBRARY_PATH /usr/local/netcdf/lib
ENV PATH /usr/local/peridigm/bin:$PATH
ENV PATH /usr/local/trilinos/bin:$PATH

RUN mkdir /var/run/sshd

RUN  echo 'root:root' | chpasswd
RUN sed -i'' -e's/^#PermitRootLogin prohibit-password$/PermitRootLogin yes/' /etc/ssh/sshd_config \
        && sed -i'' -e's/^#PasswordAuthentication yes$/PasswordAuthentication yes/' /etc/ssh/sshd_config \
        && sed -i'' -e's/^#PermitEmptyPasswords no$/PermitEmptyPasswords yes/' /etc/ssh/sshd_config \
        && sed -i'' -e's/^UsePAM yes/UsePAM no/' /etc/ssh/sshd_config
RUN service ssh start

WORKDIR /app/

EXPOSE 22
CMD    ["/usr/sbin/sshd", "-D"]

# RUN apt-get --no-install-recommends -y install vim mariadb-server mariadb-client supervisor

# RUN set -x \
#     && git clone https://github.com/SchedMD/slurm.git \
#     && cd slurm \
#     # && git checkout tags/$SLURM_TAG \
#     && ./configure --enable-debug --enable-front-end --prefix=/usr \
#        --sysconfdir=/etc/slurm --with-mysql_config=/usr/bin \
#        --libdir=/usr/lib64 \
#     && make install \
#     && install -D -m644 etc/cgroup.conf.example /etc/slurm/cgroup.conf.example \
#     && install -D -m644 etc/slurm.conf.example /etc/slurm/slurm.conf.example \
#     && install -D -m644 etc/slurm.epilog.clean /etc/slurm/slurm.epilog.clean \
#     && install -D -m644 etc/slurmdbd.conf.example /etc/slurm/slurmdbd.conf.example \
#     && install -D -m644 contribs/slurm_completion_help/slurm_completion.sh /etc/profile.d/slurm_completion.sh \
#     && cd .. \
#     && rm -rf slurm \
#     && groupadd -r slurm  \
#     && useradd -r -g slurm slurm 

# RUN mkdir -p /etc/sysconfig/slurm \
#         /var/spool/slurmd \
#         /var/run/slurmd \        
#         /var/lib/slurmd \
#         /var/log/slurm \
# 	/var/run/supervisor \
# 	/var/run/munge

# RUN chown slurm:root /var/spool/slurmd \
#         /var/run/slurmd \
#         /var/lib/slurmd \
#         /var/log/slurm  \
#     && chown munge:root /var/run/munge 

# COPY slurm.conf /etc/slurm-llnl/slurm.conf
# COPY slurmdbd.conf /etc/slurm-llnl/slurmdbd.conf
# COPY supervisord.conf /etc/

# VOLUME ["/var/lib/mysql", "/var/lib/slurmd", "/var/spool/slurmd", "/var/log/slurm"]

# COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
# CMD ["/bin/bash"]