# ARU Project

A simple project with a Flask API for addition and a Gradio frontend interface.

## Project Structure

```
aru/
├── requirements.txt
├── setup.sh
├── install.sh
├── api/
│   ├── __init__.py
│   ├── app.py
│   └── wsgi.py
├── frontend/
│   ├── __init__.py
│   ├── app.py
│   └── wsgi.py
├── nginx/
│   └── aru.conf
└── systemd/
    ├── aru-api.service
    └── aru-frontend.service
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/hrseymour/aru.git
cd aru
```

2. Run the installation script to create the virtual environment and install dependencies (assuming Python 3.10+ and Pip are already installed):
```bash
chmod +x install.sh
./install.sh
```

## Running the Applications Locally

### API (Flask)

```bash
source venv/bin/activate
cd api
python app.py
```

This will start the Flask API server on port 8000.

### Frontend (Gradio)

```bash
source venv/bin/activate
cd frontend
python app.py
```

This will start the Gradio frontend on port 8001.

## API Endpoints

- `POST /api/add`: Add two numbers
  - Request body: `{"a": number, "b": number}`
  - Response: `{"result": number}`

- `GET /api/health`: Health check endpoint
  - Response: `{"status": "healthy"}`

## Deploying with Gunicorn and Nginx

### 1. Install Required Software

```bash
sudo apt update
sudo apt install nginx
```

### 2. Set Up Gunicorn for Flask API

From the project root directory:

```bash
source venv/bin/activate
# Run the Flask API with Gunicorn
gunicorn --bind 0.0.0.0:8000 api.wsgi:app
```

### 3. Set Up Nginx

1. Copy the Nginx configuration file:
```bash
sudo cp nginx/aru.conf /etc/nginx/sites-available/
```

2. Create a symbolic link to enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/aru.conf /etc/nginx/sites-enabled/
```

3. Remove the default site if it exists:
```bash
sudo rm -f /etc/nginx/sites-enabled/default
```

4. Test the Nginx configuration:
```bash
sudo nginx -t
```

5. Reload Nginx:
```bash
sudo systemctl reload nginx
```

### 4. Access Your Application

- API Endpoints: 
  - http://localhost/api/add
  - http://localhost/api/health
- Frontend UI: http://localhost/ui/

## Production Deployment with SystemD

For production deployment, use systemd to manage your services:

### 1. Set Up SystemD Service Files

1. Copy the service files to systemd:
```bash
sudo cp systemd/aru-api.service /etc/systemd/system/
sudo cp systemd/aru-frontend.service /etc/systemd/system/
```

2. Update the paths in the service files if necessary:
```bash
sudo vim /etc/systemd/system/aru-api.service
sudo vim /etc/systemd/system/aru-frontend.service
```

3. Reload systemd daemon:
```bash
sudo systemctl daemon-reload
```

### 2. Enable and Start the Services

```bash
# Enable services to start on boot
sudo systemctl enable aru-api
sudo systemctl enable aru-frontend

# Start services
sudo systemctl start aru-api
sudo systemctl start aru-frontend
```

### 3. Managing the Services

```bash
# Check service status
sudo systemctl status aru-api
sudo systemctl status aru-frontend

# Restart services
sudo systemctl restart aru-api
sudo systemctl restart aru-frontend

# Stop services
sudo systemctl stop aru-api
sudo systemctl stop aru-frontend

# View service logs
sudo journalctl -u aru-api
sudo journalctl -u aru-frontend
```

## Troubleshooting

### Check if Services Are Running

```bash
# Check if the ports are in use
sudo lsof -i :8000
sudo lsof -i :8001

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Common Issues

1. **Port already in use**: Stop all gunicorn processes with `pkill -9 gunicorn`

2. **Nginx configuration errors**: Check syntax with `sudo nginx -t`

3. **API not accessible**: Make sure the Flask app has the correct Blueprint setup for `/api` prefix

4. **Frontend UI not loading**: Check browser console for errors and ensure the UI is running on port 8001

## Additional Production Considerations

1. **SSL/TLS**: Use Let's Encrypt and Certbot to secure your application with HTTPS
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

2. **Rate Limiting**: Add rate limiting in Nginx to protect against abuse
   ```nginx
   # Add to the server block in aru.conf
   limit_req_zone $binary_remote_addr zone=api:10m rate=5r/s;
   location /api/ {
       limit_req zone=api burst=10 nodelay;
       # ...other configuration...
   }
   ```

3. **Monitoring**: Set up monitoring with tools like Prometheus and Grafana

4. **Backups**: Set up regular backups of your application and configuration

5. **Logging**: Configure proper logging with rotation to prevent disk space issues
   ```bash
   sudo apt install logrotate
   ```