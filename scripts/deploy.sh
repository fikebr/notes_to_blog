#!/bin/bash
# Deployment script for Notes to Blog Application
# This script handles production deployment and monitoring

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
APP_NAME="notes-to-blog"
LOG_FILE="logs/deploy.log"
PID_FILE="logs/app.pid"

# Create logs directory if it doesn't exist
mkdir -p logs

# Log function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if application is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# Start the application
start() {
    log "Starting $APP_NAME..."
    
    if is_running; then
        print_warning "$APP_NAME is already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    # Set production environment
    export APP_ENV=production
    export DEBUG=false
    
    # Start the application in background
    nohup uv run python main.py process-batch > logs/app.log 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 2
    
    if is_running; then
        print_success "$APP_NAME started successfully (PID: $(cat $PID_FILE))"
        log "Application started with PID: $(cat $PID_FILE)"
    else
        print_error "Failed to start $APP_NAME"
        log "Failed to start application"
        return 1
    fi
}

# Stop the application
stop() {
    log "Stopping $APP_NAME..."
    
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            sleep 2
            
            if ps -p "$pid" > /dev/null 2>&1; then
                print_warning "Application didn't stop gracefully, force killing..."
                kill -9 "$pid"
            fi
            
            rm -f "$PID_FILE"
            print_success "$APP_NAME stopped"
            log "Application stopped"
        else
            print_warning "$APP_NAME is not running"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "$APP_NAME is not running"
    fi
}

# Restart the application
restart() {
    log "Restarting $APP_NAME..."
    stop
    sleep 2
    start
}

# Show status
status() {
    if is_running; then
        pid=$(cat "$PID_FILE")
        print_success "$APP_NAME is running (PID: $pid)"
        
        # Show recent logs
        echo ""
        print_status "Recent logs:"
        tail -n 10 logs/app.log
        
        # Show process info
        echo ""
        print_status "Process information:"
        ps -p "$pid" -o pid,ppid,cmd,etime,pcpu,pmem
        
    else
        print_warning "$APP_NAME is not running"
    fi
}

# Monitor the application
monitor() {
    print_status "Starting monitoring for $APP_NAME..."
    
    while true; do
        if ! is_running; then
            print_warning "$APP_NAME is not running, restarting..."
            start
        fi
        
        # Check memory usage
        if [ -f "$PID_FILE" ]; then
            pid=$(cat "$PID_FILE")
            mem_usage=$(ps -p "$pid" -o pmem= 2>/dev/null || echo "0")
            if [ "$mem_usage" != "" ] && [ "$mem_usage" -gt 80 ]; then
                print_warning "High memory usage detected: ${mem_usage}%"
                log "High memory usage: ${mem_usage}%"
            fi
        fi
        
        sleep 30
    done
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Check if application is running
    if ! is_running; then
        print_error "Health check failed: Application is not running"
        return 1
    fi
    
    # Check log file for errors
    if [ -f "logs/app.log" ]; then
        error_count=$(tail -n 100 logs/app.log | grep -i "error\|exception\|traceback" | wc -l)
        if [ "$error_count" -gt 5 ]; then
            print_warning "Health check warning: $error_count errors in recent logs"
        fi
    fi
    
    # Check disk space
    disk_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        print_warning "Health check warning: High disk usage: ${disk_usage}%"
    fi
    
    print_success "Health check passed"
    return 0
}

# Backup function
backup() {
    print_status "Creating backup..."
    
    timestamp=$(date '+%Y%m%d_%H%M%S')
    backup_dir="backups/backup_$timestamp"
    
    mkdir -p "$backup_dir"
    
    # Backup important directories
    if [ -d "output" ]; then
        cp -r output "$backup_dir/"
    fi
    
    if [ -d "images" ]; then
        cp -r images "$backup_dir/"
    fi
    
    if [ -d "data" ]; then
        cp -r data "$backup_dir/"
    fi
    
    # Backup configuration
    if [ -f ".env" ]; then
        cp .env "$backup_dir/"
    fi
    
    print_success "Backup created: $backup_dir"
    log "Backup created: $backup_dir"
}

# Show usage
usage() {
    echo "Usage: $0 {start|stop|restart|status|monitor|health|backup}"
    echo ""
    echo "Commands:"
    echo "  start     Start the application"
    echo "  stop      Stop the application"
    echo "  restart   Restart the application"
    echo "  status    Show application status"
    echo "  monitor   Monitor the application (continuous)"
    echo "  health    Perform health check"
    echo "  backup    Create backup of output and data"
    echo ""
}

# Main function
main() {
    case "$1" in
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        status)
            status
            ;;
        monitor)
            monitor
            ;;
        health)
            health_check
            ;;
        backup)
            backup
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 