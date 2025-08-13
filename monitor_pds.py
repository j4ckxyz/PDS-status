#!/usr/bin/env python3
"""
AT Protocol PDS Status Monitor

This script monitors the status of an AT Protocol Personal Data Server (PDS)
and performs various AT Protocol requests to test functionality.

Configuration:
- PDS_URL: The URL of your PDS (default: https://jglypt.net)
- USER_HANDLE: Your AT Protocol handle (default: @j4ck.xyz)

Usage:
    python monitor_pds.py
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configuration - Change these values for your PDS
PDS_URL = "https://jglypt.net"
USER_HANDLE = "@j4ck.xyz"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDSMonitor:
    def __init__(self, pds_url: str, user_handle: str):
        self.pds_url = pds_url.rstrip('/')
        self.user_handle = user_handle
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PDS-Monitor/1.0',
            'Accept': 'application/json'
        })
        
    def check_pds_status(self) -> Dict[str, Any]:
        """Check basic PDS status and health"""
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'pds_url': self.pds_url,
            'status': 'unknown',
            'response_time': None,
            'error': None,
            'details': {}
        }
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.pds_url}/xrpc/com.atproto.server.describeServer", timeout=10)
            response_time = time.time() - start_time
            
            result['response_time'] = round(response_time, 3)
            
            if response.status_code == 200:
                result['status'] = 'online'
                try:
                    server_info = response.json()
                    result['details'] = {
                        'available_user_domains': server_info.get('availableUserDomains', []),
                        'invite_code_required': server_info.get('inviteCodeRequired', False),
                        'links': server_info.get('links', {})
                    }
                except json.JSONDecodeError:
                    result['details'] = {'raw_response': response.text[:500]}
            else:
                result['status'] = 'error'
                result['error'] = f"HTTP {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            result['status'] = 'offline'
            result['error'] = str(e)
            
        return result
    
    def perform_atproto_requests(self) -> List[Dict[str, Any]]:
        """Perform various AT Protocol requests to test functionality"""
        requests_results = []
        
        # List of AT Protocol endpoints to test
        endpoints = [
            {
                'name': 'get_profile',
                'url': f"{self.pds_url}/xrpc/app.bsky.actor.getProfile",
                'params': {'actor': self.user_handle}
            },
            {
                'name': 'get_author_feed',
                'url': f"{self.pds_url}/xrpc/app.bsky.feed.getAuthorFeed",
                'params': {'actor': self.user_handle, 'limit': 5}
            },
            {
                'name': 'get_timeline',
                'url': f"{self.pds_url}/xrpc/app.bsky.feed.getTimeline",
                'params': {'limit': 5}
            },
            {
                'name': 'get_post_thread',
                'url': f"{self.pds_url}/xrpc/app.bsky.feed.getPostThread",
                'params': {'uri': f"at://did:plc:example/app.bsky.feed.post/123"}
            },
            {
                'name': 'get_notifications',
                'url': f"{self.pds_url}/xrpc/app.bsky.notification.listNotifications",
                'params': {'limit': 5}
            },
            {
                'name': 'get_suggestions',
                'url': f"{self.pds_url}/xrpc/app.bsky.actor.getSuggestions",
                'params': {'limit': 5}
            },
            {
                'name': 'search_posts',
                'url': f"{self.pds_url}/xrpc/app.bsky.feed.searchPosts",
                'params': {'q': 'test', 'limit': 5}
            },
            {
                'name': 'get_follows',
                'url': f"{self.pds_url}/xrpc/app.bsky.graph.getFollows",
                'params': {'actor': self.user_handle, 'limit': 5}
            },
            {
                'name': 'get_followers',
                'url': f"{self.pds_url}/xrpc/app.bsky.graph.getFollowers",
                'params': {'actor': self.user_handle, 'limit': 5}
            },
            {
                'name': 'get_likes',
                'url': f"{self.pds_url}/xrpc/app.bsky.feed.getLikes",
                'params': {'uri': f"at://did:plc:example/app.bsky.feed.post/123", 'limit': 5}
            },
            {
                'name': 'get_reposts',
                'url': f"{self.pds_url}/xrpc/app.bsky.feed.getRepostedBy",
                'params': {'uri': f"at://did:plc:example/app.bsky.feed.post/123", 'limit': 5}
            },
            {
                'name': 'get_blocks',
                'url': f"{self.pds_url}/xrpc/app.bsky.graph.getBlocks",
                'params': {'limit': 5}
            },
            {
                'name': 'get_mutes',
                'url': f"{self.pds_url}/xrpc/app.bsky.graph.getMutes",
                'params': {'limit': 5}
            },
            {
                'name': 'get_list',
                'url': f"{self.pds_url}/xrpc/app.bsky.graph.getList",
                'params': {'list': 'at://did:plc:example/app.bsky.graph.list/123'}
            },
            {
                'name': 'get_lists',
                'url': f"{self.pds_url}/xrpc/app.bsky.graph.getLists",
                'params': {'actor': self.user_handle, 'limit': 5}
            },
            {
                'name': 'get_bookmarks',
                'url': f"{self.pds_url}/xrpc/app.bsky.feed.getBookmarks",
                'params': {'limit': 5}
            },
            {
                'name': 'get_preferences',
                'url': f"{self.pds_url}/xrpc/app.bsky.actor.getPreferences"
            },
            {
                'name': 'get_suggested_follows',
                'url': f"{self.pds_url}/xrpc/app.bsky.actor.getSuggestions",
                'params': {'limit': 5}
            },
            {
                'name': 'get_popular',
                'url': f"{self.pds_url}/xrpc/app.bsky.feed.getPopular",
                'params': {'limit': 5}
            },
            {
                'name': 'get_trending',
                'url': f"{self.pds_url}/xrpc/app.bsky.feed.getTrending",
                'params': {'limit': 5}
            }
        ]
        
        for endpoint in endpoints:
            result = {
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': endpoint['name'],
                'url': endpoint['url'],
                'status': 'unknown',
                'response_time': None,
                'error': None,
                'response_code': None
            }
            
            try:
                start_time = time.time()
                response = self.session.get(endpoint['url'], params=endpoint.get('params', {}), timeout=10)
                response_time = time.time() - start_time
                
                result['response_time'] = round(response_time, 3)
                result['response_code'] = response.status_code
                
                if response.status_code == 200:
                    result['status'] = 'success'
                elif response.status_code == 401:
                    result['status'] = 'unauthorized'
                elif response.status_code == 404:
                    result['status'] = 'not_found'
                else:
                    result['status'] = 'error'
                    result['error'] = f"HTTP {response.status_code}"
                    
            except requests.exceptions.RequestException as e:
                result['status'] = 'failed'
                result['error'] = str(e)
            
            requests_results.append(result)
            
        return requests_results
    
    def run_monitoring(self) -> Dict[str, Any]:
        """Run complete monitoring check"""
        logger.info(f"Starting PDS monitoring for {self.pds_url}")
        
        # Check basic PDS status
        status_result = self.check_pds_status()
        logger.info(f"PDS Status: {status_result['status']}")
        
        # Perform AT Protocol requests
        requests_results = self.perform_atproto_requests()
        successful_requests = sum(1 for r in requests_results if r['status'] == 'success')
        logger.info(f"AT Protocol Requests: {successful_requests}/{len(requests_results)} successful")
        
        # Compile final results
        monitoring_result = {
            'timestamp': datetime.utcnow().isoformat(),
            'pds_url': self.pds_url,
            'user_handle': self.user_handle,
            'pds_status': status_result,
            'atproto_requests': requests_results,
            'summary': {
                'total_requests': len(requests_results),
                'successful_requests': successful_requests,
                'success_rate': round(successful_requests / len(requests_results) * 100, 2) if requests_results else 0,
                'pds_online': status_result['status'] == 'online'
            }
        }
        
        return monitoring_result

def save_results(results: Dict[str, Any], output_dir: str = "results"):
    """Save monitoring results to file"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/pds_monitor_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {filename}")
    return filename

def main():
    """Main function"""
    # Create monitor instance
    monitor = PDSMonitor(PDS_URL, USER_HANDLE)
    
    # Run monitoring
    results = monitor.run_monitoring()
    
    # Save results
    filename = save_results(results)
    
    # Print summary
    summary = results['summary']
    print(f"\n=== PDS Monitoring Summary ===")
    print(f"PDS URL: {PDS_URL}")
    print(f"User Handle: {USER_HANDLE}")
    print(f"Timestamp: {results['timestamp']}")
    print(f"PDS Status: {'🟢 Online' if summary['pds_online'] else '🔴 Offline'}")
    print(f"AT Protocol Requests: {summary['successful_requests']}/{summary['total_requests']} successful ({summary['success_rate']}%)")
    print(f"Results saved to: {filename}")
    
    return results

if __name__ == "__main__":
    main()
