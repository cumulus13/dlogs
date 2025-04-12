# DLogs

`DLogs` is a Python script designed to tail and format logs from Docker Compose services. It processes log lines, extracts relevant information such as timestamps, log levels, and logger details, and displays them in a styled format using the `rich` library.

## Features

- **Real-time Log Tailing**: Continuously streams logs from Docker Compose services.
- **Log Parsing**: Extracts and formats key fields such as timestamps, log levels, logger names, and caller information.
- **Log Styling**: Applies styles to log messages based on their severity levels (e.g., `info`, `error`, `debug`).
- **Keyword-based Severity Inference**: Infers log levels from keywords in the log message if not explicitly provided.
- **Timestamp Extraction**: Supports multiple timestamp formats, including ISO 8601 and PostgreSQL-style dates.

## Requirements

- Python 3.8 or higher
- Docker Compose
- `rich` library for styled console output

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/cumulus13/dlogs.git
   cd dlogs
   ```

2. Install the required Python dependencies:
   Ensure `rich` is installed:
   ```bash
   pip install rich
   ```

3. Ensure Docker Compose is installed and accessible from the command line.

## Usage

Run the script to start tailing logs from your Docker Compose services:
```bash
python dlogs.py
```

### Stopping the Script

To stop the script, press `Ctrl+C`. The script will terminate gracefully and display a message indicating that log tailing has stopped.

## How It Works

1. **Log Tailing**:
   - The script uses `subprocess.Popen` to execute the `docker-compose logs -f` command, streaming logs in real-time.

2. **Log Parsing**:
   - Each log line is processed by the `format_line` function, which extracts and formats key fields:
     - **Timestamp**: Extracted using regex patterns and formatted into a readable format.
     - **Log Level**: Detected from the log line or inferred from keywords.
     - **Logger and Caller**: Extracted using regex patterns.

3. **Log Styling**:
   - The `rich` library is used to style log messages based on their severity levels. Styles are defined in the `LEVEL_STYLES` dictionary.

4. **Output**:
   - The formatted and styled log messages are printed to the console.

## Log Formatting

The script formats log lines into the following structure:
```
[timestamp] [app_name]:[logger] [caller] [message]
```

### Example Output

```
2025/04/12 12:34:56.789000 my_app:main.py:42 This is an info message
2025/04/12 12:34:57.123000 my_app:main.py:45 [ERROR] Something went wrong!
```

## Configuration

### Log Level Styles

You can customize the styles for different log levels by modifying the `LEVEL_STYLES` dictionary in the script:
```python
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
```

### Keyword-based Severity Mapping

The `KEYWORD_LEVELS` dictionary maps keywords to severity levels. You can extend or modify this mapping as needed:
```python
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
```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the script.

## License

This project is licensed under the MIT License.

## Author
[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

## Coffee
[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)

[Support me on Patreon](https://www.patreon.com/cumulus13)