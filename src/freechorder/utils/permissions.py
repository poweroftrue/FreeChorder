"""
Permissions helper for macOS accessibility
"""

import subprocess
import click
import os


def check_accessibility_permissions() -> bool:
    """Check if the current process has accessibility permissions."""
    try:
        # Try to capture stderr to check for the "not trusted" message
        import sys
        from io import StringIO
        from pynput import keyboard
        
        # Capture stderr
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        
        try:
            # Create a test listener
            listener = keyboard.Listener(on_press=lambda k: False, suppress=False)
            listener.start()
            
            # Give it a moment to print any errors
            import time
            time.sleep(0.2)
            
            # Check stderr for the "not trusted" message
            stderr_output = sys.stderr.getvalue()
            has_error = "not trusted" in stderr_output.lower()
            
            listener.stop()
            
            return not has_error
            
        finally:
            # Restore stderr
            sys.stderr = old_stderr
        
    except Exception:
        return False


def get_terminal_app_name() -> str:
    """Get the name of the current terminal application."""
    # Get the parent process
    try:
        ppid = os.getppid()
        result = subprocess.run(['ps', '-p', str(ppid), '-o', 'comm='], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            app_path = result.stdout.strip()
            app_name = os.path.basename(app_path)
            
            # Map common terminal apps
            terminal_map = {
                'Terminal': 'Terminal',
                'iTerm2': 'iTerm',
                'iTerm': 'iTerm',
                'Hyper': 'Hyper',
                'Alacritty': 'Alacritty',
                'kitty': 'kitty',
                'WezTerm': 'WezTerm',
                'zsh': 'Terminal',  # Default shell often means Terminal.app
                'bash': 'Terminal',
            }
            
            for key, value in terminal_map.items():
                if key in app_name:
                    return value
                    
            return app_name
    except:
        pass
    
    return "your terminal application"


def show_accessibility_instructions():
    """Show detailed instructions for granting accessibility permissions."""
    terminal_app = get_terminal_app_name()
    
    click.echo("\n📋 How to Grant Accessibility Permissions:\n")
    click.echo("1. Open System Settings (or System Preferences)")
    click.echo("2. Go to Privacy & Security → Accessibility")
    click.echo("3. Click the lock icon and enter your password")
    click.echo(f"4. Find '{terminal_app}' in the list")
    click.echo("5. Check the box next to it to enable")
    click.echo(f"6. If '{terminal_app}' is not in the list:")
    click.echo("   - Click the '+' button")
    click.echo("   - Navigate to Applications (or Applications/Utilities)")
    click.echo(f"   - Select {terminal_app}.app")
    click.echo("7. Restart your terminal application\n")
    
    if terminal_app == "Terminal":
        click.echo("💡 For Terminal.app specifically:")
        click.echo("   The app is in /System/Applications/Utilities/Terminal.app\n")
    elif terminal_app == "iTerm":
        click.echo("💡 For iTerm2 specifically:")
        click.echo("   The app is usually in /Applications/iTerm.app\n")
    
    click.echo("🔐 Why is this needed?")
    click.echo("   Impulse mode needs to monitor your keyboard to detect")
    click.echo("   chord combinations. macOS requires explicit permission")
    click.echo("   for apps to monitor keyboard input for security.\n")


def open_accessibility_settings():
    """Open the macOS accessibility settings."""
    try:
        # Try to open directly to accessibility
        subprocess.run(['open', 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'])
    except:
        try:
            # Fallback to general privacy settings
            subprocess.run(['open', 'x-apple.systempreferences:com.apple.preference.security?Privacy'])
        except:
            click.echo("Please open System Settings → Privacy & Security → Accessibility manually.")
