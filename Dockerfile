
FROM python:3.9
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip supervisor
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
EXPOSE 80

CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
