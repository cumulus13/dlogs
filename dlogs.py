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
    "failed": "alert",
    "emergency": "emergency",
    "debug": "debug",
}

PATTERN_TIMESTAMP = re.compile(r"\b(?:t|ts|time)=([0-9T:.+-]+Z?)")
PATTERN_LEVEL = re.compile(r"\blevel=(\w+)", re.IGNORECASE)
PATTERN_LOGGER = re.compile(r"\blogger=([^\s]+)")
PATTERN_CALLER = re.compile(r"\b(?:caller|source)=([^\s]+)")
PATTERN_DATE_FALLBACK = re.compile(r"\b(\w{3} \w{3} \d{1,2} \d{2}:\d{2}:\d{2}) \w+ (\d{4})\b")


def infer_level_from_text(text: str) -> str | None:
    for keyword, level in KEYWORD_LEVELS.items():
        if re.search(rf"\b{keyword}\b", text, re.IGNORECASE):
            return level
    return None


def extract_timestamp(text: str) -> str:
    match = PATTERN_TIMESTAMP.search(text)
    if match:
        try:
            dt = datetime.fromisoformat(match.group(1).replace("Z", "+00:00"))
            return dt.strftime("%Y/%m/%d %H:%M:%S.%f")
        except Exception:
            return match.group(1)
    match = PATTERN_DATE_FALLBACK.search(text)
    if match:
        try:
            dt = datetime.strptime(f"{match.group(1)} {match.group(2)}", "%a %b %d %H:%M:%S %Y")
            return dt.strftime("%Y/%m/%d %H:%M:%S.000000")
        except Exception:
            return match.group(0)
    return "?"


def format_line(line: str) -> Text:
    parts = line.strip().split("|", 1)
    if len(parts) == 2:
        app_name = parts[0].strip()
        content = parts[1].strip()
    else:
        app_name = line.strip().split(":")[0].strip()
        content = line.strip()

    # Extract metadata
    timestamp = extract_timestamp(content)
    logger = PATTERN_LOGGER.search(content)
    caller = PATTERN_CALLER.search(content)
    level_match = PATTERN_LEVEL.search(content)
    level = (level_match.group(1).lower() if level_match else infer_level_from_text(content)) or "info"
    style = LEVEL_STYLES.get(level, None)

    logger_val = logger.group(1) if logger else "-"
    caller_val = caller.group(1) if caller else "-"

    # Only remove known metadata keys, but keep ts/time/etc. for output
    # clean_msg = re.sub(r"\b(logger|caller|source|level)=\S+", "", content).strip()
    clean_msg = re.sub(r"\b(logger|caller|source|level|ts|t|time)=\S+", "", content).strip()

    output = f"{timestamp} {app_name}:{logger_val} {caller_val} {clean_msg}"
    return Text(output, style=style)


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
            if line.strip():
                console.print(format_line(line))
    except KeyboardInterrupt:
        process.terminate()
        console.print("[bold yellow]Stopped tailing logs.[/bold yellow]")


if __name__ == "__main__":
    tail_docker_logs()
