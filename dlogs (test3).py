import subprocess
import re
from datetime import datetime
from rich.console import Console
from rich.text import Text

console = Console()

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

# Regex patterns
TS_PATTERN = re.compile(r"\bt=([0-9T:+.-]+)")
LEVEL_PATTERN = re.compile(r"\blevel=(\w+)\b", re.IGNORECASE)
LOGGER_PATTERN = re.compile(r"\blogger=([^\s]+)")
CALLER_PATTERN = re.compile(r"\bcaller=([^\s]+)")

# Fallback keyword-based severity detection
# KEYWORD_LEVELS = {
#     "warning": "warning",
#     "warn": "warning",
#     "error": "error",
#     "err": "error",
#     "fail": "error",
#     "fatal": "critical",
#     "critical": "critical",
#     "alert": "alert",
#     "emergency": "emergency",
# }
KEYWORD_LEVELS = {
    "fatal": "critical",
    "panic": "emergency",
    "error": "error",
    "err": "error",
    "fail": "error",
    "warning": "warning",
    "warn": "warning",
    "log": "info",
    "hint": "notice",
    "notice": "notice",
    "alert": "alert",
    "emergency": "emergency",
    "debug": "debug",
}

def infer_level_from_text(text: str) -> str | None:
    for keyword, level in KEYWORD_LEVELS.items():
        if re.search(rf"\b{keyword}\b", text, re.IGNORECASE):
            return level
    return None


def format_line(line: str) -> Text:
    parts = line.strip().split("|", 1)
    if len(parts) == 2:
        app_name = parts[0].strip()
        log_content = parts[1].strip()
    else:
        # fallback for logs like from postgresql: whole line is message
        app_name = line.strip().split(":")[0].strip()
        log_content = line.strip()

    # Extract timestamp from known format or fallback
    ts_match = TS_PATTERN.search(log_content)
    ts_fmt = ""
    if ts_match:
        ts_str = ts_match.group(1)
        try:
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            ts_fmt = dt.strftime("%Y/%m/%d %H:%M:%S.%f")
        except Exception:
            ts_fmt = ts_str
    else:
        # Try to extract from PostgreSQL-style: Fri Apr 11 16:44:22 WIB 2025
        date_match = re.search(r"\b(\w{3} \w{3} \d{1,2} \d{2}:\d{2}:\d{2}) \w+ (\d{4})\b", log_content)
        if date_match:
            try:
                dt_str = f"{date_match.group(1)} {date_match.group(2)}"
                dt = datetime.strptime(dt_str, "%a %b %d %H:%M:%S %Y")
                ts_fmt = dt.strftime("%Y/%m/%d %H:%M:%S.000000")
            except Exception:
                pass

    logger_match = LOGGER_PATTERN.search(log_content)
    caller_match = CALLER_PATTERN.search(log_content)

    logger = logger_match.group(1) if logger_match else "-"
    caller = caller_match.group(1) if caller_match else "-"

    level_match = LEVEL_PATTERN.search(log_content)
    level = level_match.group(1).lower() if level_match else infer_level_from_text(log_content)
    style = LEVEL_STYLES.get(level, None)

    # Remove parsed fields
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
