from win10toast import ToastNotifier
from notification_model import NotificationModel

def show_notification():
    # Initialize ToastNotifier object
    toaster = ToastNotifier()
    
    # Show notification
    toaster.show_toast(
        title="Hello World",
        msg="This is a notification from Python!",
        duration=10,  # Duration in seconds
        icon_path=None,  # Optional: Path to .ico file
        threaded=True  # True = run in a separate thread
    )

if __name__ == "__main__":
    show_notification()

notifier = NotificationModel()
notifier.show_notification("Test", "Test notification!")