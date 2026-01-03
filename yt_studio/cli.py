#!/usr/bin/env python3
"""
yt-studio CLI - Start the visualization web interface.

This module provides the command-line interface for starting both the
backend (FastAPI) and frontend (Vite) servers.
"""

import os
import sys
import signal
import subprocess
import time
import argparse
import shutil
from pathlib import Path


# ANSI colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


def get_package_dir() -> Path:
    """Get the directory where the package is installed."""
    return Path(__file__).parent.parent


def print_banner():
    """Print the startup banner."""
    print(f"{Colors.CYAN}╔════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.CYAN}║         yt-studio Visualization Tool       ║{Colors.NC}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════╝{Colors.NC}")
    print()


def check_node_installed() -> bool:
    """Check if Node.js is installed."""
    return shutil.which('node') is not None and shutil.which('npm') is not None


def install_frontend_deps(frontend_dir: Path) -> bool:
    """Install frontend dependencies if needed."""
    node_modules = frontend_dir / 'node_modules'
    if not node_modules.exists():
        print(f"{Colors.YELLOW}Installing frontend dependencies...{Colors.NC}")
        try:
            subprocess.run(
                ['npm', 'install'],
                cwd=frontend_dir,
                check=True,
                capture_output=True
            )
            print(f"{Colors.GREEN}✓ Frontend dependencies installed{Colors.NC}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}✗ Failed to install frontend dependencies{Colors.NC}")
            print(f"  Error: {e.stderr.decode() if e.stderr else str(e)}")
            return False
    return True


def main():
    """Main entry point for yt-studio CLI."""
    parser = argparse.ArgumentParser(
        description='Start the yt-studio visualization web interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  yt-studio                    Start with default ports
  yt-studio --backend-port 8080 --frontend-port 3000
  yt-studio --backend-only     Start only the backend server
"""
    )
    parser.add_argument(
        '--backend-port', type=int, default=9010,
        help='Port for the backend server (default: 9010)'
    )
    parser.add_argument(
        '--frontend-port', type=int, default=5173,
        help='Port for the frontend server (default: 5173)'
    )
    parser.add_argument(
        '--backend-only', action='store_true',
        help='Start only the backend server (no frontend)'
    )
    parser.add_argument(
        '--host', type=str, default='0.0.0.0',
        help='Host to bind servers to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--version', action='version', version='yt-studio 2.0.0'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    package_dir = get_package_dir()
    backend_dir = package_dir / 'backend'
    frontend_dir = package_dir / 'frontend'
    
    # Verify directories exist
    if not backend_dir.exists():
        print(f"{Colors.RED}✗ Backend directory not found: {backend_dir}{Colors.NC}")
        sys.exit(1)
    
    if not args.backend_only and not frontend_dir.exists():
        print(f"{Colors.RED}✗ Frontend directory not found: {frontend_dir}{Colors.NC}")
        sys.exit(1)
    
    # Check Node.js for frontend
    if not args.backend_only:
        if not check_node_installed():
            print(f"{Colors.RED}✗ Node.js is required for the frontend.{Colors.NC}")
            print(f"  Install Node.js from https://nodejs.org/ or run with --backend-only")
            sys.exit(1)
        
        if not install_frontend_deps(frontend_dir):
            sys.exit(1)
    
    # Store process references for cleanup
    processes = []
    
    def cleanup(signum=None, frame=None):
        """Clean up child processes on exit."""
        print()
        print(f"{Colors.YELLOW}Shutting down servers...{Colors.NC}")
        for proc in processes:
            if proc.poll() is None:  # Still running
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print(f"{Colors.GREEN}✓ All servers stopped{Colors.NC}")
        sys.exit(0)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Start backend server
    print(f"{Colors.BLUE}Starting backend server...{Colors.NC}")
    
    # Add the package directory to Python path so imports work
    env = os.environ.copy()
    python_path = str(package_dir)
    if 'PYTHONPATH' in env:
        python_path = f"{python_path}:{env['PYTHONPATH']}"
    env['PYTHONPATH'] = python_path
    
    backend_proc = subprocess.Popen(
        [
            sys.executable, '-c',
            f'''
import sys
sys.path.insert(0, "{package_dir}")
import uvicorn
from backend.main import app
uvicorn.run(app, host="{args.host}", port={args.backend_port}, log_level="warning")
'''
        ],
        env=env,
        cwd=package_dir
    )
    processes.append(backend_proc)
    
    # Wait a moment for backend to start
    time.sleep(2)
    
    # Check if backend started successfully
    if backend_proc.poll() is not None:
        print(f"{Colors.RED}✗ Backend failed to start{Colors.NC}")
        cleanup()
    
    print(f"{Colors.GREEN}✓ Backend running on http://localhost:{args.backend_port}{Colors.NC}")
    
    # Start frontend server (unless backend-only)
    if not args.backend_only:
        print(f"{Colors.BLUE}Starting frontend server...{Colors.NC}")
        
        frontend_proc = subprocess.Popen(
            ['npm', 'run', 'dev', '--', '--port', str(args.frontend_port), '--host'],
            cwd=frontend_dir,
            env=env
        )
        processes.append(frontend_proc)
        
        # Wait for frontend to start
        time.sleep(3)
        
        # Check if frontend started
        if frontend_proc.poll() is not None:
            print(f"{Colors.RED}✗ Frontend failed to start{Colors.NC}")
            cleanup()
        
        print(f"{Colors.GREEN}✓ Frontend running on http://localhost:{args.frontend_port}{Colors.NC}")
    
    # Print status
    print()
    print(f"{Colors.GREEN}╔════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║  Servers are running!                      ║{Colors.NC}")
    print(f"{Colors.GREEN}╠════════════════════════════════════════════╣{Colors.NC}")
    if not args.backend_only:
        print(f"{Colors.GREEN}║  Frontend: {Colors.BLUE}http://localhost:{args.frontend_port:<5}{Colors.GREEN}          ║{Colors.NC}")
    print(f"{Colors.GREEN}║  Backend:  {Colors.BLUE}http://localhost:{args.backend_port:<5}{Colors.GREEN}          ║{Colors.NC}")
    print(f"{Colors.GREEN}╠════════════════════════════════════════════╣{Colors.NC}")
    print(f"{Colors.GREEN}║  Press {Colors.YELLOW}Ctrl+C{Colors.GREEN} to stop all servers         ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════╝{Colors.NC}")
    print()
    
    # Wait for processes
    try:
        while True:
            # Check if any process has died
            for proc in processes:
                if proc.poll() is not None:
                    print(f"{Colors.RED}A server process has stopped unexpectedly{Colors.NC}")
                    cleanup()
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()


if __name__ == '__main__':
    main()
