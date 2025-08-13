#!/usr/bin/env python3
"""
Simple PDS Monitoring Results Analyzer
"""

import json
import os
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List, Dict, Any

def load_results(results_dir: str = "results") -> List[Dict[str, Any]]:
    """Load all monitoring results from the results directory"""
    results = []
    
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

def create_uptime_graph(results: List[Dict[str, Any]], output_file: str = "analysis/uptime_graph.png"):
    """Create a graph showing PDS uptime over time"""
    if not results:
        print("No results to analyze")
        return
    
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
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    ax1.plot(timestamps, statuses, 'b-', linewidth=2, marker='o', markersize=4)
    ax1.set_ylabel('Status (1=Online, 0=Offline)')
    ax1.set_title('PDS Uptime Over Time')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-0.1, 1.1)
    
    ax2.plot(timestamps, response_times, 'r-', linewidth=2, marker='o', markersize=4)
    ax2.set_ylabel('Response Time (seconds)')
    ax2.set_xlabel('Time')
    ax2.set_title('PDS Response Time Over Time')
    ax2.grid(True, alpha=0.3)
    
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Uptime graph saved to {output_file}")

def create_endpoint_analysis(results: List[Dict[str, Any]], output_file: str = "analysis/endpoint_analysis.png"):
    """Create a bar chart showing success rates for different endpoints"""
    if not results:
        print("No results to analyze")
        return
    
    endpoint_stats = {}
    
    for result in results:
        for request in result['atproto_requests']:
            endpoint = request['endpoint']
            
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {'success': 0, 'total': 0}
            
            endpoint_stats[endpoint]['total'] += 1
            if request['status'] == 'success':
                endpoint_stats[endpoint]['success'] += 1
    
    endpoints = []
    success_rates = []
    
    for endpoint, stats in endpoint_stats.items():
        endpoints.append(endpoint)
        success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
        success_rates.append(success_rate)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    bars = ax.bar(endpoints, success_rates, color='skyblue', alpha=0.7)
    
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom')
    
    ax.set_xlabel('AT Protocol Endpoint')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Success Rates by AT Protocol Endpoint')
    ax.set_ylim(0, 100)
    
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Endpoint analysis saved to {output_file}")

def generate_summary_report(results: List[Dict[str, Any]], output_file: str = "analysis/summary_report.txt"):
    """Generate a text summary report"""
    if not results:
        print("No results to analyze")
        return
    
    with open(output_file, 'w') as f:
        f.write("PDS Monitoring Summary Report\n")
        f.write("=" * 50 + "\n\n")
        
        total_checks = len(results)
        online_checks = sum(1 for r in results if r['pds_status']['status'] == 'online')
        uptime_percentage = (online_checks / total_checks) * 100 if total_checks > 0 else 0
        
        f.write(f"Total monitoring checks: {total_checks}\n")
        f.write(f"Online checks: {online_checks}\n")
        f.write(f"Overall uptime: {uptime_percentage:.2f}%\n\n")
        
        response_times = [r['pds_status'].get('response_time', 0) for r in results if r['pds_status'].get('response_time')]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            f.write(f"Average response time: {avg_response_time:.3f} seconds\n\n")
        
        total_requests = sum(r['summary']['total_requests'] for r in results)
        successful_requests = sum(r['summary']['successful_requests'] for r in results)
        overall_success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        
        f.write(f"Total AT Protocol requests: {total_requests}\n")
        f.write(f"Successful requests: {successful_requests}\n")
        f.write(f"Overall success rate: {overall_success_rate:.2f}%\n\n")
        
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
    
    os.makedirs("analysis", exist_ok=True)
    
    print("\nGenerating visualizations and reports...")
    
    create_uptime_graph(results, "analysis/uptime_graph.png")
    create_endpoint_analysis(results, "analysis/endpoint_analysis.png")
    generate_summary_report(results, "analysis/summary_report.txt")
    
    print("\nAnalysis complete! Check the 'analysis/' directory for results.")

if __name__ == "__main__":
    main()
