FROM 799617403160.dkr.ecr.us-east-1.amazonaws.com/python-opencv-0
ENV cmake_dir /opencv
ENV cmake_bin_dir $cmake_dir/work
RUN mkdir $cmake_bin_dir
WORKDIR $cmake_bin_dir
RUN cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local $cmake_dir
RUN make
RUN make install
