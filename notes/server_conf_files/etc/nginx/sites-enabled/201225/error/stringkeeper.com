# THIS MAKES ERROR 403 FORBIDDEN.


upstream app_server {
    server unix:/home/ubuntu/daphne.sock fail_timeout=0;
}

server {
    listen 80;
    server_name stringkeeper.com www.stringkeeper.com;
}

server {
    server_name stringkeeper.com www.stringkeeper.com;
    listen 443 ssl; 

    ssl_certificate     /etc/letsencrypt/live/stringkeeper.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/stringkeeper.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/stringkeeper.com/chain.pem;
    access_log /var/log/nginx/stringkeeper.com.access.log;
    error_log /var/log/nginx/stringkeeper.com.error.log;
}

server {
    if ($host = www.stringkeeper.com) {
        return 301 https://$host$request_uri;
    }

    if ($host = stringkeeper.com) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    server_name stringkeeper.com www.stringkeeper.com;
    return 404;
}

