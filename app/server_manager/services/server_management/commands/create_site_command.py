import os
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command


class CreateSiteCommand(Command):
    def __init__(self, data):
        self.config = data
        print(f"Config: {data}")

    def execute(self, data):
        self.config = data.get('data', {})

        self.create_fastcgi_params()
        self.generate_dhparams()
        self.write_nginx_server_block()
        self.add_tls_for_ubuntu()
        self.create_nginx_config_directories()
        self.enable_nginx_sites()
        self.write_redirector()
        self.restart_services()

        return {"message": "Site web-server config created and configured"}

    def create_fastcgi_params(self):
        fastcgi_params = """
fastcgi_param   QUERY_STRING        \\$query_string;
fastcgi_param   REQUEST_METHOD      \\$request_method;
fastcgi_param   CONTENT_TYPE        \\$content_type;
fastcgi_param   CONTENT_LENGTH      \\$content_length;
fastcgi_param   SCRIPT_FILENAME     \\$realpath_root\\$fastcgi_script_name;
fastcgi_param   SCRIPT_NAME         \\$fastcgi_script_name;
fastcgi_param   REQUEST_URI         \\$request_uri;
fastcgi_param   DOCUMENT_URI        \\$document_uri;
fastcgi_param   DOCUMENT_ROOT       \\$realpath_root;
fastcgi_param   SERVER_PROTOCOL     \\$server_protocol;
fastcgi_param   GATEWAY_INTERFACE   CGI/1.1;
fastcgi_param   SERVER_SOFTWARE     nginx/\\$nginx_version;
fastcgi_param   REMOTE_ADDR         \\$remote_addr;
fastcgi_param   REMOTE_PORT         \\$remote_port;
fastcgi_param   SERVER_ADDR         \\$server_addr;
fastcgi_param   SERVER_PORT         \\$server_port;
fastcgi_param   SERVER_NAME         \\$server_name;
fastcgi_param   HTTPS               \\$https if_not_empty;
fastcgi_param   REDIRECT_STATUS     200;
fastcgi_param   HTTP_PROXY          \\"\\";
"""
        run_command(f'echo "{fastcgi_params.strip()}" | sudo tee /etc/nginx/fastcgi_params')

    def generate_dhparams(self):
        if not os.path.isfile('/etc/nginx/dhparams.pem'):
            run_command("sudo openssl dhparam -out /etc/nginx/dhparams.pem 2048")

    def write_nginx_server_block(self):
        domain = self.config.get('domain')
        nginx_config = f"""
        # IMPORTANT CONFIG (DO NOT REMOVE!)
        include forge-conf/{domain}/before/*;
        
        server {{
            listen 80;
            listen [::]:80;
            server_name {domain};
            server_tokens off;
            root /home/super_forge/{domain}/public;
        
            # FORGE SSL (DO NOT REMOVE!)
            # ssl_certificate;
            # ssl_certificate_key;
        
            ssl_protocols TLSv1.2 TLSv1.3;
            ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
            ssl_prefer_server_ciphers off;
            ssl_dhparam /etc/nginx/dhparams.pem;
        
            add_header X-Frame-Options "SAMEORIGIN";
            add_header X-XSS-Protection "1; mode=block";
            add_header X-Content-Type-Options "nosniff";
        
            index index.html index.htm index.php;
        
            charset utf-8;
        
            # FORGE CONFIG (DO NOT REMOVE!)
            include forge-conf/{domain}/server/*;
        
            location / {{
                try_files $uri $uri/ /index.php?$query_string;
            }}
        
            location = /favicon.ico {{ access_log off; log_not_found off; }}
            location = /robots.txt  {{ access_log off; log_not_found off; }}
        
            access_log off;
            error_log  /var/log/nginx/{domain}-error.log error;
        
            error_page 404 /index.php;
        
            location ~ \.php$ {{
                fastcgi_split_path_info ^(.+\.php)(/.+)$;
                fastcgi_pass unix:/var/run/php/php8.3-fpm.sock;
                fastcgi_index index.php;
                include fastcgi_params;
                }}
                
                location ~ /\.(?!well-known).* {{
                deny all;
                }}
                }}
                
                # FORGE CONFIG (DO NOT REMOVE!)
                include forge-conf/{domain}/after/*;
                """
        with open('/tmp/nginx_server_block.conf', 'w') as f:
            f.write(nginx_config.strip())

        run_command(f'sudo mv /tmp/nginx_server_block.conf /etc/nginx/sites-available/{domain}')

    def add_tls_for_ubuntu(self):
        ubuntu_version = run_command("lsb_release -rs").strip()
        domain = self.config.get('domain')
        if self.version_to_int(ubuntu_version) >= self.version_to_int("20.04"):
            print(f"Server on Ubuntu {ubuntu_version}")
            config_file_path = f"/etc/nginx/sites-available/{domain}"
            if os.path.exists(config_file_path):
                run_command(f'sudo sed -i "s/ssl_protocols .*/ssl_protocols TLSv1.2 TLSv1.3;/g" {config_file_path}')
            else:
                raise Exception(f"File {config_file_path} does not exist.")

    def create_nginx_config_directories(self):
        run_command(f"sudo mkdir -p /etc/nginx/forge-conf/{self.config['domain']}/before")
        run_command(f"sudo mkdir -p /etc/nginx/forge-conf/{self.config['domain']}/after")
        run_command(f"sudo mkdir -p /etc/nginx/forge-conf/{self.config['domain']}/server")

    def enable_nginx_sites(self):
        run_command(f"sudo rm -f /etc/nginx/sites-enabled/{self.config['domain']}")
        run_command(f"sudo rm -f /etc/nginx/sites-enabled/www.{self.config['domain']}")
        run_command(
            f"sudo ln -s /etc/nginx/sites-available/{self.config['domain']} /etc/nginx/sites-enabled/{self.config['domain']}")

    def write_redirector(self):
        redirector_config = f"""
        server {{
            listen 80;
            listen [::]:80;
            server_tokens off;
        
            server_name www.{self.config['domain']};
        
            if ($http_x_forwarded_proto = 'https') {{
                return 301 https://{self.config['domain']}$request_uri;
            }}
        
            return 301 $scheme://{self.config['domain']}$request_uri;
        }}
        """
        with open('/tmp/nginx_redirector.conf', 'w') as f:
            f.write(redirector_config.strip())

        run_command(
            f'sudo mv /tmp/nginx_redirector.conf /etc/nginx/forge-conf/{self.config["domain"]}/before/redirect.conf')

    def restart_services(self):
        run_command("sudo service nginx reload")
        php_fpm_versions = [
            "php8.3-fpm",
            "php8.2-fpm",
            "php8.1-fpm",
            "php8.0-fpm",
            "php7.4-fpm",
            "php7.3-fpm",
            "php7.2-fpm",
            "php7.1-fpm",
            "php7.0-fpm",
            "php5.6-fpm",
            "php5-fpm"
        ]

        for version in php_fpm_versions:
            if run_command(f"pgrep {version}", raise_exception=False):
                run_command(f"sudo service {version} restart")

    @staticmethod
    def version_to_int(version):
        return int("".join(version.split(".")))