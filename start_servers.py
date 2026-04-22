#!/usr/bin/env python
"""
Start both Flask backend and frontend server
Works on Windows, Linux, and Mac
"""
import subprocess
import sys
import time
import os
from threading import Thread

def start_flask():
    """Start Flask backend on port 5000"""
    print("Starting Flask API server...")
    print("API Endpoints: http://localhost:5000/api")
    print("Note: Frontend is served separately on port 8080")
    print()
    
    # Disable Flask reloader to prevent double start
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '0'  # Disable debug mode
    
    subprocess.run([sys.executable, "app.py"], env=env)

def start_frontend():
    """Start frontend server on port 8080"""
    print("Starting frontend HTTP server on port 8080...")
    os.chdir("frontend")
    subprocess.run([sys.executable, "-m", "http.server", "8080"])

def main():
    print("=" * 60)
    print(" Procurement Anomaly Detection")
    print(" Upload Interface Setup")
    print("=" * 60)
    print()
    
    # Start Flask in a separate thread
    flask_thread = Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Wait for Flask to start
    print("Waiting for Flask to initialize...")
    time.sleep(2)
    
    print()
    print("=" * 60)
    print(" READY!")
    print("=" * 60)
    print()
    print("📤 Upload Interface: http://localhost:8080")
    print("📊 Dashboard: http://localhost:8080/dashboard.html")
    print("🔌 Flask API: http://localhost:5000/api")
    print()
    print("Press Ctrl+C to stop all servers")
    print("=" * 60)
    print()
    
    # Start frontend in main thread (blocking)
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n\nShutting down servers...")
        print("✓ Servers stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
