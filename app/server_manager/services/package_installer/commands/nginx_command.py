import os

from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command


class NginxCommand(Command):

    def __init__(self, config):
        self.config = config

    def execute(self, data):
        self.config = data.get('config', self.config)

        run_command("sudo apt-get update")

        # Install Nginx
        run_command("sudo apt-get install -y --force-yes nginx")
        run_command("sudo systemctl enable nginx.service")

        # Generate dhparam File
        run_command("sudo openssl dhparam -out /etc/nginx/dhparams.pem 2048")

        # Configure Nginx and PHP-FPM settings
        self.configure_php_fpm()
        self.configure_nginx()
        self.configure_gzip()
        self.configure_cloudflare()

        # Disable default Nginx site
        if os.path.exists('/etc/nginx/sites-enabled/default'):
            os.remove('/etc/nginx/sites-enabled/default')
        if os.path.exists('/etc/nginx/sites-available/default'):
            os.remove('/etc/nginx/sites-available/default')

        run_command("sudo service nginx restart")

        # Install a catch-all server
        self.install_catch_all_server()

        # Restart Nginx and PHP-FPM services
        self.restart_services()

        # Add forge user to www-data group
        run_command("sudo usermod -a -G www-data super_forge")
        run_command("sudo id super_forge")
        run_command("sudo groups super_forge")

        # Update logrotate configuration
        file_exists = run_command('test -f /etc/logrotate.d/nginx && echo "exists"', return_json=False)
        if file_exists.strip() == "exists":
            grep_output = run_command('grep --count "maxsize" /etc/logrotate.d/nginx', return_json=False,
                                      raise_exception=False)
            if grep_output is None or grep_output.strip() == "0":
                with open('/etc/logrotate.d/nginx', 'r') as file:
                    lines = file.readlines()

                with open('/etc/logrotate.d/nginx', 'w') as file:
                    for line in lines:
                        file.write(line)
                        if line.strip() in ['daily', 'weekly', 'monthly', 'yearly']:
                            file.write('maxsize 100M\n')
        else:
            # Create logrotate file for nginx
            with open('/etc/logrotate.d/nginx', 'w') as f:
                f.write('daily\nmaxsize 100M\n')

        # Install Node.js and global npm packages
        self.install_node_js_and_npm_packages()

        return {"message": "Nginx installed and configured successfully"}

    def configure_php_fpm(self):
        nginx_conf_path = "/etc/nginx/nginx.conf"
        mime_types_path = "/etc/nginx/mime.types"

        if not os.path.exists(nginx_conf_path):
            self.create_default_nginx_conf(nginx_conf_path)

        if not os.path.exists(mime_types_path):
            self.create_default_mime_types(mime_types_path)

        memory_limit = self.config.get('memory_limit', '512M')
        run_command(f"sudo sed -i 's/memory_limit = .*/memory_limit = {memory_limit}/' /etc/php/8.3/fpm/php.ini")
        run_command("sudo sed -i 's/error_reporting = .*/error_reporting = E_ALL/' /etc/php/8.3/fpm/php.ini")
        run_command("sudo sed -i 's/display_errors = .*/display_errors = Off/' /etc/php/8.3/fpm/php.ini")
        run_command("sudo sed -i 's/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/' /etc/php/8.3/fpm/php.ini")

    def configure_nginx(self):
        run_command("sudo sed -i 's/user www-data;/user super_forge;/' /etc/nginx/nginx.conf")
        run_command("sudo sed -i 's/worker_processes.*/worker_processes auto;/' /etc/nginx/nginx.conf")
        run_command("sudo sed -i 's/# multi_accept.*/multi_accept on;/' /etc/nginx/nginx.conf")
        run_command(
            "sudo sed -i 's/# server_names_hash_bucket_size.*/server_names_hash_bucket_size 128;/' /etc/nginx/nginx.conf")

    def create_default_nginx_conf(self, path):
        default_conf = """
            user www-data;
            worker_processes auto;
            pid /run/nginx.pid;
            include /etc/nginx/modules-enabled/*.conf;
        
            events {
                worker_connections 768;
                # multi_accept on;
            }
        
            http {
                sendfile on;
                tcp_nopush on;
                tcp_nodelay on;
                keepalive_timeout 65;
                types_hash_max_size 2048;
                # server_tokens off;
        
                include /etc/nginx/mime.types;
                default_type application/octet-stream;
        
                access_log /var/log/nginx/access.log;
                error_log /var/log/nginx/error.log;
        
                gzip on;
                gzip_disable "msie6";
        
                include /etc/nginx/conf.d/*.conf;
                include /etc/nginx/sites-enabled/*;
            }
            """
        with open(path, 'w') as f:
            f.write(default_conf)

        print(f"Created default Nginx configuration at {path}")

    def create_default_mime_types(self, path):
        mime_types_content = """
    types {
        text/html                             html htm shtml;
        text/css                              css;
        text/xml                              xml;
        image/gif                             gif;
        image/jpeg                            jpeg jpg;
        application/javascript                js;
        application/atom+xml                  atom;
        application/rss+xml                   rss;

        text/mathml                           mml;
        text/plain                            txt;
        text/vnd.sun.j2me.app-descriptor      jad;
        text/vnd.wap.wml                      wml;
        text/x-component                      htc;

        image/png                             png;
        image/tiff                            tif tiff;
        image/vnd.wap.wbmp                    wbmp;
        image/x-icon                          ico;
        image/x-jng                           jng;
        image/x-ms-bmp                        bmp;
        image/svg+xml                         svg svgz;
        image/webp                            webp;
        application/font-woff                 woff;
        application/java-archive              jar war ear;
        application/json                      json;
        application/mac-binhex40              hqx;
        application/msword                    doc;
        application/pdf                       pdf;
        application/postscript                ps eps ai;
        application/rtf                       rtf;
        application/vnd.apple.mpegurl         m3u8;
        application/vnd.ms-excel              xls;
        application/vnd.ms-fontobject         eot;
        application/vnd.ms-powerpoint         ppt;
        application/vnd.wap.wmlc              wmlc;
        application/vnd.google-earth.kml+xml  kml;
        application/vnd.google-earth.kmz      kmz;
        application/x-7z-compressed           7z;
        application/x-cocoa                   cco;
        application/x-java-archive-diff       jardiff;
        application/x-java-jnlp-file          jnlp;
        application/x-makeself                run;
        application/x-perl                    pl pm;
        application/x-pilot                   prc pdb;
        application/x-rar-compressed          rar;
        application/x-redhat-package-manager  rpm;
        application/x-sea                     sea;
        application/x-shockwave-flash         swf;
        application/x-stuffit                 sit;
        application/x-tcl                     tcl tk;
        application/x-x509-ca-cert            der pem crt;
        application/x-xpinstall               xpi;
        application/xhtml+xml                 xhtml;
        application/xspf+xml                  xspf;
        application/zip                       zip;

        application/octet-stream              bin exe dll;
        application/octet-stream              deb;
        application/octet-stream              dmg;
        application/octet-stream              iso img;
        application/octet-stream              msi msp msm;

        application/vnd.openxmlformats-officedocument.wordprocessingml.document    docx;
        application/vnd.openxmlformats-officedocument.spreadsheetml.sheet          xlsx;
        application/vnd.openxmlformats-officedocument.presentationml.presentation  pptx;

        audio/midi                            mid midi kar;
        audio/mpeg                            mp3;
        audio/ogg                             ogg;
        audio/x-m4a                           m4a;
        audio/x-realaudio                     ra;

        video/3gpp                            3gpp 3gp;
        video/mp2t                            ts;
        video/mp4                             mp4;
        video/mpeg                            mpeg mpg;
        video/quicktime                       mov;
        video/webm                            webm;
        video/x-flv                           flv;
        video/x-m4v                           m4v;
        video/x-mng                           mng;
        video/x-ms-asf                        asx asf;
        video/x-ms-wmv                        wmv;
        video/x-msvideo                       avi;
    }
    """
        with open(path, 'w') as f:
            f.write(mime_types_content)

        print(f"Created default mime.types at {path}")

    def configure_gzip(self):
        gzip_config = """
    gzip_comp_level 5;
    gzip_min_length 256;
    gzip_proxied any;
    gzip_vary on;
    gzip_http_version 1.1;

    gzip_types
    application/atom+xml
    application/javascript
    application/json
    application/ld+json
    application/manifest+json
    application/rss+xml
    application/vnd.geo+json
    application/vnd.ms-fontobject
    application/x-font-ttf
    application/x-web-app-manifest+json
    application/xhtml+xml
    application/xml
    font/opentype
    image/bmp
    image/svg+xml
    image/x-icon
    text/cache-manifest
    text/css
    text/plain
    text/vcard
    text/vnd.rim.location.xloc
    text/vtt
    text/x-component
    text/x-cross-domain-policy;
    """
        with open('/etc/nginx/conf.d/gzip.conf', 'w') as f:
            f.write(gzip_config)

    def configure_cloudflare(self):
        cloudflare_config = """
    set_real_ip_from 173.245.48.0/20;
    set_real_ip_from 103.21.244.0/22;
    set_real_ip_from 103.22.200.0/22;
    set_real_ip_from 103.31.4.0/22;
    set_real_ip_from 141.101.64.0/18;
    set_real_ip_from 108.162.192.0/18;
    set_real_ip_from 190.93.240.0/20;
    set_real_ip_from 188.114.96.0/20;
    set_real_ip_from 197.234.240.0/22;
    set_real_ip_from 198.41.128.0/17;
    set_real_ip_from 162.158.0.0/15;
    set_real_ip_from 104.16.0.0/13;
    set_real_ip_from 104.24.0.0/14;
    set_real_ip_from 172.64.0.0/13;
    set_real_ip_from 131.0.72.0/22;
    set_real_ip_from 2400:cb00::/32;
    set_real_ip_from 2606:4700::/32;
    set_real_ip_from 2803:f800::/32;
    set_real_ip_from 2405:b500::/32;
    set_real_ip_from 2405:8100::/32;
    set_real_ip_from 2a06:98c0::/29;
    set_real_ip_from 2c0f:f248::/32;
    real_ip_header X-Forwarded-For;
    """
        with open('/etc/nginx/conf.d/cloudflare.conf', 'w') as f:
            f.write(cloudflare_config)

    def install_catch_all_server(self):
        if not os.path.exists('/etc/nginx/ssl/'):
            os.makedirs('/etc/nginx/ssl/')

        run_command("sudo openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout "
                    "/etc/nginx/ssl/catch-all.invalid.key -out /etc/nginx/ssl/catch-all.invalid.crt -subj "
                    "\"/C=US/ST=California/L=San Francisco/O=Example Company/OU=IT/CN=example.com\"")

        catch_all_config = """
    server {
        listen 80 default_server;
        listen [::]:80 default_server;
        listen 443 ssl http2 default_server;
        listen [::]:443 ssl http2 default_server;
        server_name _;
        server_tokens off;

        ssl_certificate /etc/nginx/ssl/catch-all.invalid.crt;
        ssl_certificate_key /etc/nginx/ssl/catch-all.invalid.key;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_dhparam /etc/nginx/dhparams.pem;
        ssl_reject_handshake on;

        return 444;
    }
    """
        with open('/etc/nginx/sites-available/000-catch-all', 'w') as f:
            f.write(catch_all_config)

        if not os.path.exists('/etc/nginx/sites-available/000-catch-all'):
            os.symlink('/etc/nginx/sites-available/000-catch-all', '/etc/nginx/sites-enabled/000-catch-all')

    def restart_services(self):
        nginx_status = run_command("ps aux | grep nginx | grep -v grep", raise_exception=False)
        if not nginx_status.strip():
            run_command("sudo service nginx start")
            print("Started Nginx")
        else:
            run_command("sudo service nginx reload")
            print("Reloaded Nginx")

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

    def install_node_js_and_npm_packages(self):
        run_command("sudo apt-get install -y apt-transport-https")
        if not os.path.exists('/etc/apt/keyrings'):
            os.makedirs('/etc/apt/keyrings')

        run_command(
            "sudo curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg")

        node_major = 18
        with open('/etc/apt/sources.list.d/nodesource.list', 'w') as f:
            f.write(
                f"deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_{node_major}.x nodistro main")

        run_command("sudo apt-get update")
        run_command("sudo apt-get install -y --force-yes nodejs")

        run_command("sudo npm install -g pm2")
        run_command("sudo npm install -g gulp")
        run_command("sudo npm install -g yarn")
        run_command("sudo npm install -g bun")
