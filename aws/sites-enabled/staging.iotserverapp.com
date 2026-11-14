server {

	listen 80;
	server_name staging.iotserverapp.com www.staging.iotserverapp.com;
	return 301 https://$server_name$request_uri;
}

server {
	listen 443 ssl default_server;
	server_name staging.iotserverapp.com;
	ssl_certificate /etc/letsencrypt/live/staging.iotserverapp.com/fullchain.pem; # managed by Certbot
   	ssl_certificate_key /etc/letsencrypt/live/staging.iotserverapp.com/privkey.pem; # managed by Certbot

	ssl_session_cache shared:le_nginx_SSL:10m;
	ssl_session_timeout 1440m;
	ssl_session_tickets off;
	ssl_protocols TLSv1.2 TLSv1.3;
	ssl_prefer_server_ciphers off;

	client_max_body_size 20M;
	
	location / {
		return 301 /userapi/v1/docs;
	}	

	location /docs {
		return 301 /userapi/v1/docs;
	}

	location /admin {
		return 301 /userapi/v1/admin;
	}

	location /userapi/v1 {
		proxy_pass http://localhost:8000;

		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "upgrade";
		proxy_redirect   off;
		proxy_buffering  off;
		
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
		proxy_set_header X-Forwarded-Host $http_host;					 
	}

	location /listener/v1 {
		proxy_pass http://localhost:8100;

		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "upgrade";
		proxy_redirect   off;
		proxy_buffering  off;
		
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
		proxy_set_header X-Forwarded-Host $http_host;					 
	}

}

