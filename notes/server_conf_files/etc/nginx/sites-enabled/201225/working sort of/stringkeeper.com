upstream app_server {
    server unix:/home/ubuntu/daphne.sock fail_timeout=0;
}

server {
    listen 80;
    server_name stringkeeper.com www.stringkeeper.com;
    return 301 https://stringkeeper.com$request_uri;
}


server {
    listen 443 ssl http2;
    server_name stringkeeper.com www.stringkeeper.com;

    ssl_certificate     /etc/letsencrypt/live/stringkeeper.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/stringkeeper.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/stringkeeper.com/chain.pem;

    access_log /var/log/nginx/stringkeeper.com.access.log;
    error_log /var/log/nginx/stringkeeper.com.error.log;



#location /wss/ {
# proxy_pass http://app_server;
# proxy_http_version 1.1;
# proxy_set_header Upgrade $http_upgrade;
# proxy_set_header Connection “upgrade”;
# proxy_redirect off;
# proxy_set_header Host $host;
# proxy_set_header X-Real-IP $remote_addr;
# proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
# proxy_set_header X-Forwarded-Host $server_name;
# }

    location / {
#            proxy_pass 8000;
#            proxy_pass http://unix:/run/gunicorn.sock;
#           proxy_pass http://app_server;
            proxy_pass http://unix:/home/ubuntu/daphne.sock;
#       proxy_pass http://0.0.0:8000;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_redirect off;
    }

    location /static {
        alias home/ubuntu/stringkeeper/static;
    }

    location  /favicon.ico {
        alias home/ubuntu/stringkeeper/static/favicon.ico;
    }

    location  /robots.txt {
        alias home/ubuntu/stringkeeper/static/robots.txt;
    }

}
