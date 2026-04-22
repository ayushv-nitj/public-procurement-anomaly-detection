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
    print("Starting Flask backend on port 5000...")
    subprocess.run([sys.executable, "app.py"])

def start_frontend():
    """Start frontend server on port 8080"""
    print("Starting frontend server on port 8080...")
    os.chdir("frontend")
    subprocess.run([sys.executable, "-m", "http.server", "8080"])

def main():
    print("=" * 60)
    print(" Procurement Anomaly Detection")
    print(" Upload Interface Setup")
    print("=" * 60)
    print()
    print("Starting servers...")
    print()
    
    # Start Flask in a separate thread
    flask_thread = Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Wait for Flask to start
    print("Waiting for Flask to start...")
    time.sleep(3)
    
    print()
    print("=" * 60)
    print(" READY!")
    print("=" * 60)
    print()
    print("Upload Interface: http://localhost:8080")
    print("Dashboard: http://localhost:8080/dashboard.html")
    print("Flask API: http://localhost:5000/api")
    print()
    print("Press Ctrl+C to stop all servers")
    print("=" * 60)
    print()
    
    # Start frontend in main thread (blocking)
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()
