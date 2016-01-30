FROM nginx
RUN rm /etc/nginx/conf.d/*
COPY nginx.conf /etc/nginx/
COPY photo_mapper.conf /etc/nginx/conf.d/photo_mapper.conf
EXPOSE 80
EXPOSE 443
CMD ["nginx"]
