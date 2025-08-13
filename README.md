# PDS Status Monitor

A simplified, unified GitHub Actions-based monitoring system that checks the status of your AT Protocol Personal Data Server (PDS), performs various checks, and generates analysis graphs automatically.

## Features

- **Automated Monitoring**: Runs every 30 minutes via GitHub Actions.
- **Unified Script**: A single Python script handles monitoring, data storage, and analysis.
- **Optional Authenticated Checks**: If you provide credentials, it runs additional tests that require login.
- **On-the-Fly Analysis**: Automatically regenerates uptime and endpoint success graphs after each run.
- **Simplified Data Storage**: All results are stored in a single, easy-to-parse JSON file.

## Quick Start

### 1. Fork the Repository

Fork this repository to your own GitHub account.

### 2. Configure via GitHub Secrets

Configuration is handled by GitHub repository secrets. This keeps your credentials secure.

1.  In your forked repository, go to `Settings` > `Secrets and variables` > `Actions`.
2.  Create the following secrets:

| Secret Name             | Description                                                                                             | Required |
| ----------------------- | ------------------------------------------------------------------------------------------------------- | -------- |
| `PDS_URL`               | The full URL of your PDS (e.g., `https://my-pds.com`). Defaults to `https://bsky.social` if not set.    | No       |
| `BLUESKY_USER`          | Your Bluesky username/handle (e.g., `my-handle.bsky.social`). **Required for authenticated checks.**      | No       |
| `BLUESKY_APP_PASSWORD`  | An app password for your Bluesky account. **Required for authenticated checks.**                          | No       |

**Note:** To enable authenticated checks, you must provide both `BLUESKY_USER` and `BLUESKY_APP_PASSWORD`. Otherwise, the monitor will only perform unauthenticated checks.

### 3. Enable GitHub Actions

The monitoring will automatically start running every 30 minutes. You can also trigger it manually:

1.  Go to your repository on GitHub and click the **Actions** tab.
2.  Select the **Monitor PDS Status** workflow.
3.  Click **Run workflow** to trigger a manual run.

## How It Works

- Every 30 minutes, the GitHub Action runs the `monitor_pds.py` script.
- The script performs a series of checks against your PDS.
- A new data point, including the results of the checks, is appended to `results/pds_monitoring_data.json`.
- The script then regenerates the analysis graphs in the `analysis/` directory based on the complete dataset.
- The workflow commits the updated data file and graphs back to your repository.

## Viewing Results

- **Raw Data**: The full history of monitoring checks is in `results/pds_monitoring_data.json`.
- **Visualizations**: Check the `analysis/` directory for the latest graphs:
    - `uptime_graph.png`: Shows PDS uptime and response times.
    - `endpoint_analysis.png`: Shows the success rate for each monitored endpoint.

## Customization

### Changing Monitoring Frequency

Edit `.github/workflows/monitor_pds.yml` and modify the `cron` schedule:

```yaml
schedule:
  # Run every 15 minutes
  - cron: '*/15 * * * *'
```

### Adding New Checks

Modify the `run_all_checks` method in `monitor_pds.py` to add new client calls.

## Troubleshooting

- **Actions not running**: Ensure you have enabled GitHub Actions for your repository.
- **Login failed errors**: Double-check your `BLUESKY_USER` and `BLUESKY_APP_PASSWORD` secrets. Ensure the app password is correct and has the necessary permissions.
- **Commit errors**: The workflow needs `write` permissions for `contents` to push results back to the repository. This is configured in `monitor_pds.yml` by default.

## License

This project is open source and available under the [LICENSE](LICENSE) file.
