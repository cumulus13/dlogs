import subprocess
import re
from rich.console import Console
from rich.text import Text

console = Console()

# Updated level-to-style mapping
LEVEL_STYLES = {
    "info": "bright_cyan",
    "debug": "black on orange3",
    "error": "white on red",
    "warning": "black on yellow",
    "notice": "black on cyan",
    "alert": "white on blue",
    "emergency": "white on magenta",
    "critical": "black on green",
}

# Regex to extract log level from line
LEVEL_PATTERN = re.compile(r"\blevel=(\w+)\b", re.IGNORECASE)

def format_line(line: str) -> Text:
    match = LEVEL_PATTERN.search(line)
    if match:
        level = match.group(1).lower()
        style = LEVEL_STYLES.get(level)
        if style:
            return Text(line.strip(), style=style)
    return Text(line.strip())  # Default style if level not found

def tail_docker_logs():
    process = subprocess.Popen(
        ["docker-compose", "logs", "-f"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        for line in process.stdout:
            console.print(format_line(line))
    except KeyboardInterrupt:
        process.terminate()
        console.print("[bold yellow]Stopped tailing logs.[/bold yellow]")

if __name__ == "__main__":
    tail_docker_logs()
