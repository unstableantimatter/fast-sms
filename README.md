# Fast SMS Alert System

A sleek, modern application for monitoring log files and sending SMS alerts when specific patterns are detected.

## Features

- **Real-time log file monitoring**: Track changes to log files as they happen
- **Pattern detection**: Define keywords or patterns to trigger alerts
- **SMS notifications**: Send alerts via TextBelt with 1 free SMS per day
- **Pattern matching display**: View detected patterns in the monitoring interface
- **Persistent configuration**: Save your settings between sessions
- **Modern UI**: Dark-themed, intuitive interface

## Requirements

- Python 3.7+
- Internet connection for TextBelt API access

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/unstableantimatter/fast-sms.git
   cd fast-sms
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## Usage

### Setting up SMS Notifications

1. Navigate to the **Settings** tab
2. The default TextBelt API key "textbelt" provides 1 free SMS per day with TextBelt attribution
3. For more messages, enter your paid TextBelt API key
4. Add recipient phone numbers in international format (e.g., +1XXXXXXXXXX)
5. Click "Test Connection" to verify your settings
6. Click "Save Settings" to save your configuration

### Monitoring a Log File

1. Navigate to the **Monitor** tab
2. Enter the path to the log file or click "Browse" to select it
3. Enter patterns or keywords to trigger alerts (one per line)
4. Click "Start Monitoring" to begin tracking the file
5. View activity logs and pattern matches in the output area
6. Click "Send Test SMS" to verify SMS functionality

## TextBelt Free Tier Usage

This application uses TextBelt for SMS notifications:
- Free tier: 1 SMS message per day using API key "textbelt" (includes attribution)
- For higher volume, purchase credits at https://textbelt.com
- SMS are sent via standard carriers with high deliverability

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
