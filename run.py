#!/usr/bin/env python3
"""
DATAGUARD AI — Main Application Launcher
Runs database migrations/seeding and starts the FastAPI server.
"""
import sys
import os
import webbrowser
import uvicorn

def main():
    print("=" * 70)
    print("  DATAGUARD AI: Structural Data Inconsistencies Detection System")
    print("  Based on IEEE Access Research Paper (Accura - InsurTech Pre-Migration QA)")
    print("=" * 70)

    # Add current dir to path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    print("[*] Initializing Database & Seeding InsurTech Templates/Rules...")
    try:
        from backend.app.seed_data import seed_database
        seed_database()
        print("[+] Database initialized and seeded successfully.")
    except Exception as e:
        print(f"[!] Warning during seeding: {e}")

    host = "127.0.0.1"
    port = 8000
    app_url = f"http://{host}:{port}"

    print(f"\n[+] Application Web Interface: {app_url}")
    print(f"[+] Interactive Swagger API Docs: {app_url}/docs")
    print(f"[+] Pre-configured Accounts:")
    print("    - Administrator:  admin@dataguard.ai  / admin123")
    print("    - Technical QA:   tech@dataguard.ai   / tech123")
    print("    - Client User:    client@inventiva.com / client123")
    print("=" * 70)
    print("Starting server... Press Ctrl+C to stop.\n")

    # Launch browser automatically
    try:
        webbrowser.open(app_url)
    except Exception:
        pass

    uvicorn.run("backend.app.main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()

