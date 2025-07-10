import win32serviceutil

def is_service_running(service_name: str) -> str:
    try:
        status = win32serviceutil.QueryServiceStatus(service_name)[1]
        return "running" if status == 4 else "not running"
    except Exception as e:
        return f"Error checking service status: {e}"

def start_service(service_name: str) -> str:
    try:
        win32serviceutil.StartService(service_name)
        return f"Service '{service_name}' started successfully."
    except Exception as e:
        return f"Error starting service: {e}"

def stop_service(service_name: str) -> str:
    try:
        win32serviceutil.StopService(service_name)
        return f"Service '{service_name}' stopped successfully."
    except Exception as e:
        return f"Error stopping service: {e}"
