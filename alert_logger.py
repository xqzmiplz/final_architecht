from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import os

# Получаем путь к файлу логов из переменной окружения
LOG_FILE = os.getenv('ALERT_LOG_FILE', '/app/alerts.log')

# Проверяем существование директории и создаем её, если отсутствует
log_dir = os.path.dirname(LOG_FILE)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Проверяем существование файла и создаем его, если отсутствует
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'a'):
        pass

# Настройка логирования в файл
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AlertHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # Парсим JSON из тела запроса
            alert_data = json.loads(post_data.decode('utf-8'))
            
            # Логируем алерт
            for alert in alert_data.get('alerts', []):
                alert_name = alert.get('labels', {}).get('alertname', 'Unknown')
                status = alert.get('status', 'Unknown')
                summary = alert.get('annotations', {}).get('summary', 'No summary')
                description = alert.get('annotations', {}).get('description', 'No description')
                
                log_message = (
                    f"Alert: {alert_name}, Status: {status}, "
                    f"Summary: {summary}, Description: {description}"
                )
                logging.info(log_message)
            
            # Отправляем успешный ответ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
            
        except Exception as e:
            logging.error(f"Error processing alert: {str(e)}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"status": "error"}')

def run(server_class=HTTPServer, handler_class=AlertHandler, port=9094):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Starting alert logger server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()