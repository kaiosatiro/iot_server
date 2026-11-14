server {
	listen 80;
	server_name adminer.iotserverapp.com;
	return 301 https://$host$request_uri;
}

server {
	listen 443 ssl;
	server_name adminer.iotserverapp.com;
	
	ssl_certificate /etc/letsencrypt/live/iotserverapp.com/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/iotserverapp.com/privkey.pem;

	ssl_session_cache shared:le_nginx_SSL:10m;
	ssl_session_timeout 1440m;
	ssl_session_tickets off;
	ssl_protocols TLSv1.2 TLSv1.3;
	ssl_prefer_server_ciphers off;

	client_max_body_size 20M;

	location / {
		proxy_pass http://localhost:8080/;

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


