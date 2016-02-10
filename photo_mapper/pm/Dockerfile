FROM 799617403160.dkr.ecr.us-east-1.amazonaws.com/photomapper_base:latest
WORKDIR /app
RUN cd . && git clone https://github.com/jaymell/photo_mapper .
RUN pip install -r requirements.txt
RUN ./get_jpgps.sh
ADD config ./
EXPOSE 5000
CMD ["./run_app.sh"]
