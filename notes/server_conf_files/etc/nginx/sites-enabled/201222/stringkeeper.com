upstream app_server {
    server unix:/home/ubuntu/daphne.sock fail_timeout=0;
}

server {
    listen 80;
    server_name stringkeeper.com www.stringkeeper.com;
    return 301 https://stringkeeper.com$request_uri;
    ssl_certificate /etc/letsencrypt/live/stringkeeper.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/stringkeeper.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/stringkeeper.com/chain.pem;
#    include snippets/ssl.conf;
#    include snippets/letsencrypt.conf;
}

server {
        listen 443 ssl http2;
        server_name <hostname>;

        client_max_body_size 20M; # this is optionally, I usually put it very big in nginx and do$

        ssl_certificate /etc/letsencrypt/live/stringkeeper.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/stringkeeper.com/privkey.pem;
        ssl_trusted_certificate /etc/letsencrypt/live/stringkeeper.com/chain.pem;
#        include snippets/ssl.conf;
#        include snippets/letsencrypt.conf;

        location /static/ {
            sendfile on;
            location ~* \.(?:ico|css|js|gif|jpe?g|png|svg|woff|bmp)$ {
            expires 7d;
        }
        alias /home/ubuntu/stringkeeper/static/;
    }


    location / {
        proxy_pass http://app_server;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header X-Forwarded-Proto "https";
        proxy_set_header Connection "upgrade";
        add_header Referrer-Policy "no-referrer-when-downgrade";
    }
}
