#!/usr/bin/env python3
"""
AT Protocol PDS Status Monitor

This script monitors the status of an AT Protocol Personal Data Server (PDS),
performs AT Protocol requests (authenticated or unauthenticated), and generates
updated analysis graphs with each run.
"""

import os
import json
import time
import glob
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from atproto import Client, exceptions

# --- Configuration ---
PDS_URL = os.environ.get("PDS_URL", "https://jglypt.net")
USER_HANDLE = os.environ.get("BLUESKY_USER")
APP_PASSWORD = os.environ.get("BLUESKY_APP_PASSWORD")
RESULTS_DIR = "results"
ANALYSIS_DIR = "analysis"
RESULTS_FILE = os.path.join(RESULTS_DIR, "pds_monitoring_data.json")

# --- Set up logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDSMonitor:
    """
    Monitors a PDS, performs checks, and saves results.
    """
    def __init__(self, pds_url: str, user_handle: Optional[str] = None, app_password: Optional[str] = None):
        self.pds_url = pds_url.rstrip('/')
        self.user_handle = user_handle
        self.app_password = app_password
        self.client = self._get_client()

    def _get_client(self) -> Client:
        """Creates a new atproto Client and optionally logs in."""
        client = Client(base_url=self.pds_url)
        if self.user_handle and self.app_password:
            try:
                logger.info(f"Attempting to log in as {self.user_handle}...")
                client.login(self.user_handle, self.app_password)
                logger.info("Login successful.")
            except exceptions.AtProtocolError as e:
                logger.error(f"Login failed: {e}")
        else:
            logger.info("No credentials provided, proceeding with unauthenticated client.")
        return client

    def _run_check(self, check_name: str, func, **kwargs) -> Dict[str, Any]:
        """Helper to run a single check and capture its result."""
        start_time = time.time()
        result = {
            "endpoint": check_name,
            "status": "failed",
            "response_time": None,
            "response_code": None,
            "error": None
        }
        try:
            response = func(**kwargs)
            result["status"] = "success"
            # Assuming the client gives us a dict-like object
            if hasattr(response, 'to_dict'):
                # Clean up the response if needed
                pass
        except exceptions.AtProtocolError as e:
            result["error"] = str(e)
            if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                result["response_code"] = e.response.status_code
        except Exception as e:
            result["error"] = str(e)
        finally:
            result["response_time"] = round(time.time() - start_time, 3)

        status_emoji = "🟢" if result['status'] == 'success' else "🔴"
        logger.info(f"{status_emoji} {check_name}: {result['status']} ({result['response_time']}s)")
        return result

    def run_all_checks(self) -> List[Dict[str, Any]]:
        """Runs all monitoring checks."""
        logger.info(f"Starting checks for PDS at {self.pds_url}")
        results = []

        # --- Unauthenticated requests ---
        results.append(self._run_check("describe_server", self.client.com.atproto.server.describe_server))
        if self.user_handle:
            results.append(self._run_check("get_profile", self.client.app.bsky.actor.get_profile, actor=self.user_handle))
            results.append(self._run_check("get_author_feed", self.client.app.bsky.feed.get_author_feed, actor=self.user_handle, limit=5))

        # --- Authenticated requests ---
        if self.client.me:
            results.append(self._run_check("get_session", self.client.com.atproto.server.get_session))
            results.append(self._run_check("get_timeline", self.client.app.bsky.feed.get_timeline, limit=5))

        return results

def load_results(filepath: str) -> List[Dict[str, Any]]:
    """Loads monitoring results from the JSON file."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading results file {filepath}: {e}")
        return []

def save_results(filepath: str, data: List[Dict[str, Any]]):
    """Saves monitoring results to the JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Results saved to {filepath}")
    except IOError as e:
        logger.error(f"Error saving results to {filepath}: {e}")

def generate_graphs(results: List[Dict[str, Any]]):
    """Generates and saves analysis graphs."""
    if not results:
        logger.warning("No results to analyze, skipping graph generation.")
        return

    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    # --- Prepare data ---
    timestamps = [datetime.fromisoformat(r['timestamp']) for r in results]
    
    # Uptime data (based on describe_server)
    uptime_statuses = [1 if r['results'][0]['status'] == 'success' else 0 for r in results]
    response_times = [r['results'][0]['response_time'] for r in results]

    # Endpoint success rates
    endpoint_stats = {}
    for result in results:
        for check in result['results']:
            endpoint = check['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {'success': 0, 'total': 0}
            endpoint_stats[endpoint]['total'] += 1
            if check['status'] == 'success':
                endpoint_stats[endpoint]['success'] += 1

    # --- Uptime Graph ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(f'PDS Uptime and Response Time ({PDS_URL})', fontsize=16)
    
    ax1.plot(timestamps, uptime_statuses, 'g-', marker='o', markersize=4, linestyle='-', label="Uptime (1=OK)")
    ax1.set_ylabel('Status')
    ax1.set_ylim(-0.1, 1.1)
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax1.legend()

    ax2.plot(timestamps, response_times, 'b-', marker='o', markersize=4, linestyle='-', label="Response Time (s)")
    ax2.set_ylabel('Response Time (s)')
    ax2.set_xlabel('Time')
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax2.legend()

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    uptime_graph_path = os.path.join(ANALYSIS_DIR, "uptime_graph.png")
    plt.savefig(uptime_graph_path)
    logger.info(f"Uptime graph saved to {uptime_graph_path}")
    plt.close()

    # --- Endpoint Success Rate Graph ---
    endpoints = list(endpoint_stats.keys())
    success_rates = [(endpoint_stats[e]['success'] / endpoint_stats[e]['total']) * 100 for e in endpoints]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(endpoints, success_rates, color='skyblue')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title(f'Endpoint Success Rates ({PDS_URL})')
    ax.set_ylim(0, 100)
    plt.xticks(rotation=45, ha='right')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.1f}%', ha='center', va='bottom')

    plt.tight_layout()
    endpoint_graph_path = os.path.join(ANALYSIS_DIR, "endpoint_analysis.png")
    plt.savefig(endpoint_graph_path)
    logger.info(f"Endpoint analysis graph saved to {endpoint_graph_path}")
    plt.close()


def main():
    """Main function to run monitoring and analysis."""
    # This check ensures that we don't generate artifacts during PR checks, only on main/schedule.
    is_pr_check = os.environ.get("GITHUB_EVENT_NAME") == "pull_request"

    monitor = PDSMonitor(PDS_URL, USER_HANDLE, APP_PASSWORD)
    
    # Run the checks
    check_results = monitor.run_all_checks()

    # Structure the new data point
    new_data_point = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pds_url": PDS_URL,
        "authenticated": bool(monitor.client.me),
        "results": check_results
    }

    # On PRs, we only run the checks to get a status, but don't save or graph.
    if is_pr_check:
        logger.info("Pull Request check complete. Skipping artifact generation.")
    else:
        # Load existing data, append new data, and save
        all_data = load_results(RESULTS_FILE)
        all_data.append(new_data_point)
        save_results(RESULTS_FILE, all_data)

        # Generate new graphs
        generate_graphs(all_data)

    # Print summary
    successful_checks = sum(1 for r in check_results if r['status'] == 'success')
    total_checks = len(check_results)
    logger.info(f"Monitoring complete. {successful_checks}/{total_checks} checks successful.")
    print("\n=== PDS Monitoring Summary ===")
    print(f"PDS URL: {PDS_URL}")
    print(f"Authenticated: {'Yes' if new_data_point['authenticated'] else 'No'}")
    print(f"Timestamp: {new_data_point['timestamp']}")
    for res in new_data_point['results']:
        status_emoji = "🟢" if res['status'] == 'success' else "🔴"
        print(f"  {status_emoji} {res['endpoint']}: {res['status']} ({res['response_time']}s)")


if __name__ == "__main__":
    main()
