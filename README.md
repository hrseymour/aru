# ARU Project

A simple project with a Flask API and Gradio frontend.

## Project Structure

```
aru/
├── requirements.txt
├── setup.sh
├── api/
│   ├── __init__.py
│   ├── app.py
│   └── wsgi.py
├── frontend/
│   ├── __init__.py
│   ├── app.py
│   └── wsgi.py
└── nginx/
    └── strawman.conf
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/hrseymour/aru.git
cd aru
```

2. Run the setup script to create the virtual environment and install dependencies:
```bash
chmod +x setup.sh
./setup.sh
```

## Running the Applications

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

- `POST /add`: Add two numbers
  - Request body: `{"a": number, "b": number}`
  - Response: `{"result": number}`

- `GET /health`: Health check endpoint
  - Response: `{"status": "healthy"}`

## Deploying with Nginx

1. Install Nginx if you haven't already:
```bash
sudo apt update
sudo apt install nginx
sudo apt install gunicorn
```

2. Copy the Nginx configuration file:
```bash
sudo cp nginx/aru.conf /etc/nginx/sites-available/
```

3. Create a symbolic link to enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/aru.conf /etc/nginx/sites-enabled/
```

4. Test the Nginx configuration:
```bash
sudo nginx -t
```

5. Restart Nginx:
```bash
sudo systemctl restart nginx
```

6. Run both applications with Gunicorn for production:

For the API:
```bash
source venv/bin/activate
# from /
gunicorn --bind 0.0.0.0:8000 api.wsgi:app
```

For the Frontend:
```bash
source venv/bin/activate
cd frontend
python app.py  # Gradio has its own production server
```

7. Access your applications:
   - Main application: http://localhost/
   - API: http://localhost/api/

## Production Deployment Tips

For production deployment, consider:

1. Creating systemd service files for automatic startup
2. Setting up SSL certificates with Let's Encrypt
3. Adding proper logging configuration
4. Implementing rate limiting in Nginx