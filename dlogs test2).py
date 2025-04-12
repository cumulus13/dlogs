import subprocess
import re
from datetime import datetime
from rich.console import Console
from rich.text import Text

console = Console()

# Color mapping for log levels
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

# Regex for each field
TS_PATTERN = re.compile(r"\bt=([0-9T:+.-]+)")
LEVEL_PATTERN = re.compile(r"\blevel=(\w+)\b", re.IGNORECASE)
LOGGER_PATTERN = re.compile(r"\blogger=([^\s]+)")
CALLER_PATTERN = re.compile(r"\bcaller=([^\s]+)")

def format_line(line: str) -> Text:
    parts = line.strip().split("|", 1)
    if len(parts) != 2:
        return Text(line.strip())  # fallback if unexpected format

    app_name = parts[0].strip()
    log_content = parts[1].strip()

    ts_match = TS_PATTERN.search(log_content)
    ts_str = ts_match.group(1) if ts_match else None
    ts_fmt = ""
    if ts_str:
        try:
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            ts_fmt = dt.strftime("%Y/%m/%d %H:%M:%S.%f")
        except Exception:
            ts_fmt = ts_str

    level_match = LEVEL_PATTERN.search(log_content)
    level = level_match.group(1).lower() if level_match else None
    style = LEVEL_STYLES.get(level, None)

    logger_match = LOGGER_PATTERN.search(log_content)
    caller_match = CALLER_PATTERN.search(log_content)

    logger = logger_match.group(1) if logger_match else "-"
    caller = caller_match.group(1) if caller_match else "-"

    # Remove parsed fields from the message part
    cleaned_content = re.sub(r"\b(logger|t|level|caller)=\S+", "", log_content).strip()

    output = f"{ts_fmt} {app_name}:{logger} {caller} {cleaned_content}"
    return Text(output, style=style if style else None)

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
