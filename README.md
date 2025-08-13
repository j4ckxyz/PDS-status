# PDS Status Monitor

A GitHub Actions-based monitoring system that checks the status of your AT Protocol Personal Data Server (PDS) every 30 minutes and performs various AT Protocol requests to test functionality.

## Features

- **Automated Monitoring**: Runs every 30 minutes via GitHub Actions
- **Comprehensive Testing**: Tests AT Protocol endpoints and server health
- **Data Storage**: Saves results as JSON files for easy analysis
- **Visualization Tools**: Generate graphs, calendar views, and reports
- **Configurable**: Easy to adapt for any PDS and user handle

## Quick Start

### 1. Configuration

Edit the configuration in `monitor_pds.py`:

```python
# Configuration - Change these values for your PDS
PDS_URL = "https://jglypt.net"  # Your PDS URL
USER_HANDLE = "@j4ck.xyz"       # Your AT Protocol handle
```

### 2. Manual Testing

Test the monitoring script locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run a single monitoring check
python monitor_pds.py
```

This will:
- Check your PDS status
- Perform AT Protocol requests
- Save results to `results/pds_monitor_YYYYMMDD_HHMMSS.json`
- Display a summary in the terminal

### 3. Enable GitHub Actions

The monitoring will automatically start running every 30 minutes once you push to the main branch. You can also trigger it manually:

1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. Select "Monitor PDS Status" workflow
4. Click "Run workflow" to trigger manually

## Data Analysis

### Generate Visualizations

After collecting some monitoring data, generate visualizations:

```bash
# Install analysis dependencies
pip install -r requirements.txt

# Generate all visualizations and reports
python analyze_results.py
```

This creates several files in the `analysis/` directory:

- **`uptime_graph.png`**: Shows PDS uptime and response times over time
- **`success_rate_graph.png`**: Shows AT Protocol request success rates
- **`calendar_heatmap.png`**: Calendar view of daily uptime percentages
- **`endpoint_analysis.png`**: Success rates for each AT Protocol endpoint
- **`summary_report.txt`**: Text summary of all monitoring data

### Viewing Results

#### Graph View
The uptime graph shows:
- PDS online/offline status over time
- Response times for each check
- Clear visualization of downtime periods

#### Calendar View
The calendar heatmap shows:
- Daily uptime percentages
- Color-coded days (green = high uptime, red = low uptime)
- Weekly patterns and trends

#### Endpoint Analysis
The endpoint analysis shows:
- Success rates for each AT Protocol endpoint
- Which endpoints are most reliable
- Potential issues with specific functionality

### Downloading Data

All monitoring results are stored as JSON files in the `results/` directory. You can:

1. **Download individual files**: Click on any JSON file in the GitHub interface
2. **Download all results**: Use the "Code" → "Download ZIP" option
3. **Clone the repository**: `git clone <your-repo-url>`

## Data Format

Each monitoring result is saved as a JSON file with this structure:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "pds_url": "https://jglypt.net",
  "user_handle": "@j4ck.xyz",
  "pds_status": {
    "status": "online",
    "response_time": 0.245,
    "error": null,
    "details": { ... }
  },
  "atproto_requests": [
    {
      "endpoint": "server_describe",
      "status": "success",
      "response_time": 0.123,
      "response_code": 200
    }
  ],
  "summary": {
    "total_requests": 10,
    "successful_requests": 1,
    "success_rate": 10.0,
    "pds_online": true
  }
}
```

## Understanding the Results

### Expected Behavior

- **PDS Status**: Should show "online" if your PDS is working
- **AT Protocol Requests**: Most endpoints will return 401 (Unauthorized) because they require authentication
- **Server Describe**: This endpoint should always work and return 200
- **Response Times**: Should be under 1 second for good performance

### What 401 Errors Mean

401 (Unauthorized) errors are **normal and expected** for most AT Protocol endpoints when making unauthenticated requests. This indicates:
- Your PDS is online and responding
- The endpoints are working correctly
- Authentication is properly configured

### What to Monitor

- **PDS Status**: Ensure it stays "online"
- **Response Times**: Watch for performance degradation
- **Server Describe**: This should always return 200
- **Overall Uptime**: Track percentage of successful checks

## Customization

### Adding New Endpoints

To test additional AT Protocol endpoints, edit the `endpoints` list in `monitor_pds.py`:

```python
endpoints = [
    # ... existing endpoints ...
    {
        'name': 'your_new_endpoint',
        'url': f"{self.pds_url}/xrpc/your.endpoint.path",
        'params': {'param1': 'value1'}
    }
]
```

### Changing Monitoring Frequency

Edit `.github/workflows/monitor_pds.yml`:

```yaml
schedule:
  # Run every 15 minutes
  - cron: '*/15 * * * *'
  # Run every hour
  - cron: '0 * * * *'
```

### Custom Analysis

Modify `analyze_results.py` to create custom visualizations or add new analysis functions.

## Troubleshooting

### Common Issues

1. **PDS not responding**: Check if your PDS is running and accessible
2. **Authentication errors**: Most endpoints require authentication (this is normal)
3. **Rate limiting**: The script includes delays to avoid overwhelming your PDS

### Debug Mode

Run with verbose logging:

```bash
python -u monitor_pds.py 2>&1 | tee monitoring.log
```

### Check GitHub Actions

If the automated monitoring isn't working:
1. Check the "Actions" tab in your GitHub repository
2. Look for any error messages in the workflow logs
3. Ensure the repository has the necessary permissions

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the [LICENSE](LICENSE) file.
