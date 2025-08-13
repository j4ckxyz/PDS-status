#!/usr/bin/env python3
"""
PDS Monitoring Results Analyzer

This script analyzes the monitoring results and creates visualizations
including graphs and calendar views.

Usage:
    python analyze_results.py
"""

import json
import os
import glob
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns
from typing import List, Dict, Any
import numpy as np

def load_results(results_dir: str = "results") -> List[Dict[str, Any]]:
    """Load all monitoring results from the results directory"""
    results = []
    
    # Find all JSON files in the results directory
    pattern = os.path.join(results_dir, "pds_monitor_*.json")
    files = glob.glob(pattern)
    
    for file_path in sorted(files):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                results.append(data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return results

def create_uptime_graph(results: List[Dict[str, Any]], output_file: str = "uptime_graph.png"):
    """Create a graph showing PDS uptime over time"""
    if not results:
        print("No results to analyze")
        return
    
    # Extract timestamps and status
    timestamps = []
    statuses = []
    response_times = []
    
    for result in results:
        timestamp = datetime.fromisoformat(result['timestamp'].replace('Z', '+00:00'))
        timestamps.append(timestamp)
        
        pds_status = result['pds_status']['status']
        statuses.append(1 if pds_status == 'online' else 0)
        
        response_time = result['pds_status'].get('response_time', 0)
        response_times.append(response_time)
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Uptime plot
    ax1.plot(timestamps, statuses, 'b-', linewidth=2, marker='o', markersize=4)
    ax1.set_ylabel('Status (1=Online, 0=Offline)')
    ax1.set_title('PDS Uptime Over Time')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-0.1, 1.1)
    
    # Response time plot
    ax2.plot(timestamps, response_times, 'r-', linewidth=2, marker='o', markersize=4)
    ax2.set_ylabel('Response Time (seconds)')
    ax2.set_xlabel('Time')
    ax2.set_title('PDS Response Time Over Time')
    ax2.grid(True, alpha=0.3)
    
    # Format x-axis
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Uptime graph saved to {output_file}")

def create_success_rate_graph(results: List[Dict[str, Any]], output_file: str = "success_rate_graph.png"):
    """Create a graph showing AT Protocol request success rates over time"""
    if not results:
        print("No results to analyze")
        return
    
    # Extract timestamps and success rates
    timestamps = []
    success_rates = []
    total_requests = []
    
    for result in results:
        timestamp = datetime.fromisoformat(result['timestamp'].replace('Z', '+00:00'))
        timestamps.append(timestamp)
        
        summary = result['summary']
        success_rates.append(summary['success_rate'])
        total_requests.append(summary['total_requests'])
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Success rate plot
    ax1.plot(timestamps, success_rates, 'g-', linewidth=2, marker='o', markersize=4)
    ax1.set_ylabel('Success Rate (%)')
    ax1.set_title('AT Protocol Request Success Rate Over Time')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 100)
    
    # Total requests plot
    ax2.plot(timestamps, total_requests, 'purple', linewidth=2, marker='o', markersize=4)
    ax2.set_ylabel('Total Requests')
    ax2.set_xlabel('Time')
    ax2.set_title('Total AT Protocol Requests Over Time')
    ax2.grid(True, alpha=0.3)
    
    # Format x-axis
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Success rate graph saved to {output_file}")

def create_calendar_heatmap(results: List[Dict[str, Any]], output_file: str = "calendar_heatmap.png"):
    """Create a calendar heatmap showing daily uptime"""
    if not results:
        print("No results to analyze")
        return
    
    # Group results by date
    daily_data = {}
    
    for result in results:
        timestamp = datetime.fromisoformat(result['timestamp'].replace('Z', '+00:00'))
        date = timestamp.date()
        
        if date not in daily_data:
            daily_data[date] = {'online': 0, 'total': 0}
        
        daily_data[date]['total'] += 1
        if result['pds_status']['status'] == 'online':
            daily_data[date]['online'] += 1
    
    # Calculate daily uptime percentages
    dates = []
    uptime_percentages = []
    
    for date, data in sorted(daily_data.items()):
        dates.append(date)
        uptime_percentage = (data['online'] / data['total']) * 100 if data['total'] > 0 else 0
        uptime_percentages.append(uptime_percentage)
    
    # Create calendar heatmap
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Create a matrix for the heatmap
    start_date = min(dates)
    end_date = max(dates)
    date_range = pd.date_range(start_date, end_date, freq='D')
    
    # Create a DataFrame with dates and uptime percentages
    df = pd.DataFrame({'date': dates, 'uptime': uptime_percentages})
    df.set_index('date', inplace=True)
    
    # Reindex to include all dates
    df = df.reindex(date_range, fill_value=np.nan)
    
    # Reshape for heatmap (weeks as rows, days as columns)
    df_heatmap = df['uptime'].values.reshape(-1, 7)
    
    # Create the heatmap
    im = ax.imshow(df_heatmap.T, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
    
    # Set labels
    ax.set_xlabel('Week')
    ax.set_ylabel('Day of Week')
    ax.set_title('PDS Uptime Calendar Heatmap')
    
    # Set y-axis labels
    ax.set_yticks(range(7))
    ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Uptime Percentage (%)')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Calendar heatmap saved to {output_file}")

def create_endpoint_analysis(results: List[Dict[str, Any]], output_file: str = "endpoint_analysis.png"):
    """Create a bar chart showing success rates for different endpoints"""
    if not results:
        print("No results to analyze")
        return
    
    # Aggregate endpoint data
    endpoint_stats = {}
    
    for result in results:
        for request in result['atproto_requests']:
            endpoint = request['endpoint']
            
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {'success': 0, 'total': 0}
            
            endpoint_stats[endpoint]['total'] += 1
            if request['status'] == 'success':
                endpoint_stats[endpoint]['success'] += 1
    
    # Calculate success rates
    endpoints = []
    success_rates = []
    
    for endpoint, stats in endpoint_stats.items():
        endpoints.append(endpoint)
        success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
        success_rates.append(success_rate)
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    bars = ax.bar(endpoints, success_rates, color='skyblue', alpha=0.7)
    
    # Add value labels on bars
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom')
    
    ax.set_xlabel('AT Protocol Endpoint')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Success Rates by AT Protocol Endpoint')
    ax.set_ylim(0, 100)
    
    # Rotate x-axis labels for better readability
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Endpoint analysis saved to {output_file}")

def generate_summary_report(results: List[Dict[str, Any]], output_file: str = "summary_report.txt"):
    """Generate a text summary report"""
    if not results:
        print("No results to analyze")
        return
    
    with open(output_file, 'w') as f:
        f.write("PDS Monitoring Summary Report\n")
        f.write("=" * 50 + "\n\n")
        
        # Overall statistics
        total_checks = len(results)
        online_checks = sum(1 for r in results if r['pds_status']['status'] == 'online')
        uptime_percentage = (online_checks / total_checks) * 100 if total_checks > 0 else 0
        
        f.write(f"Total monitoring checks: {total_checks}\n")
        f.write(f"Online checks: {online_checks}\n")
        f.write(f"Overall uptime: {uptime_percentage:.2f}%\n\n")
        
        # Time range
        first_check = datetime.fromisoformat(results[0]['timestamp'].replace('Z', '+00:00'))
        last_check = datetime.fromisoformat(results[-1]['timestamp'].replace('Z', '+00:00'))
        f.write(f"Monitoring period: {first_check} to {last_check}\n")
        f.write(f"Duration: {last_check - first_check}\n\n")
        
        # Average response time
        response_times = [r['pds_status'].get('response_time', 0) for r in results if r['pds_status'].get('response_time')]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            f.write(f"Average response time: {avg_response_time:.3f} seconds\n\n")
        
        # AT Protocol request statistics
        total_requests = sum(r['summary']['total_requests'] for r in results)
        successful_requests = sum(r['summary']['successful_requests'] for r in results)
        overall_success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        
        f.write(f"Total AT Protocol requests: {total_requests}\n")
        f.write(f"Successful requests: {successful_requests}\n")
        f.write(f"Overall success rate: {overall_success_rate:.2f}%\n\n")
        
        # Recent status
        latest_result = results[-1]
        f.write("Latest Check:\n")
        f.write(f"  Timestamp: {latest_result['timestamp']}\n")
        f.write(f"  PDS Status: {latest_result['pds_status']['status']}\n")
        f.write(f"  Response Time: {latest_result['pds_status'].get('response_time', 'N/A')} seconds\n")
        f.write(f"  AT Protocol Success Rate: {latest_result['summary']['success_rate']}%\n")
    
    print(f"Summary report saved to {output_file}")

def main():
    """Main function to run all analyses"""
    print("Loading monitoring results...")
    results = load_results()
    
    if not results:
        print("No monitoring results found in the results/ directory")
        return
    
    print(f"Loaded {len(results)} monitoring results")
    
    # Create output directory for visualizations
    os.makedirs("analysis", exist_ok=True)
    
    # Generate all visualizations and reports
    print("\nGenerating visualizations and reports...")
    
    create_uptime_graph(results, "analysis/uptime_graph.png")
    create_success_rate_graph(results, "analysis/success_rate_graph.png")
    create_calendar_heatmap(results, "analysis/calendar_heatmap.png")
    create_endpoint_analysis(results, "analysis/endpoint_analysis.png")
    generate_summary_report(results, "analysis/summary_report.txt")
    
    print("\nAnalysis complete! Check the 'analysis/' directory for results.")

if __name__ == "__main__":
    main()
