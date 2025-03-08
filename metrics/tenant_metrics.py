import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os
import uuid

class TenantMetrics:
    """
    Tracks and analyzes usage metrics for different tenants.
    Provides insights into resource consumption, performance, and utilization.
    """
    
    def __init__(self, metrics_dir: str = 'metrics/tenant_logs'):
        """
        Initialize TenantMetrics.
        
        :param metrics_dir: Directory to store tenant usage metrics
        """
        self.metrics_dir = metrics_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure metrics directory exists
        os.makedirs(metrics_dir, exist_ok=True)
    
    def record_resource_usage(
        self, 
        tenant_id: str, 
        resource_type: str, 
        usage_amount: float,
        additional_metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record resource usage for a specific tenant.
        
        :param tenant_id: Unique tenant identifier
        :param resource_type: Type of resource used
        :param usage_amount: Amount of resource consumed
        :param additional_metadata: Optional additional context for the usage
        """
        try:
            # Prepare usage record
            usage_record = {
                'id': str(uuid.uuid4()),
                'tenant_id': tenant_id,
                'resource_type': resource_type,
                'usage_amount': usage_amount,
                'timestamp': datetime.now().isoformat(),
                'metadata': additional_metadata or {}
            }
            
            # Create tenant-specific log file
            tenant_log_path = os.path.join(
                self.metrics_dir, 
                f'{tenant_id}_usage_log.jsonl'
            )
            
            # Append to log file
            with open(tenant_log_path, 'a') as log_file:
                log_file.write(json.dumps(usage_record) + '\n')
            
            self.logger.info(
                f"Recorded {usage_amount} {resource_type} usage for tenant {tenant_id}"
            )
        
        except Exception as e:
            self.logger.error(f"Error recording resource usage: {e}")
    
    def get_tenant_usage_summary(
        self, 
        tenant_id: str, 
        start_time: Optional[datetime] = None, 
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate a summary of resource usage for a tenant.
        
        :param tenant_id: Unique tenant identifier
        :param start_time: Optional start time for usage calculation
        :param end_time: Optional end time for usage calculation
        :return: Dictionary with usage summary
        """
        try:
            tenant_log_path = os.path.join(
                self.metrics_dir, 
                f'{tenant_id}_usage_log.jsonl'
            )
            
            if not os.path.exists(tenant_log_path):
                return {}
            
            # Initialize usage summary
            usage_summary = {
                'total_usage_by_resource': {},
                'usage_count_by_resource': {},
                'first_usage': None,
                'last_usage': None
            }
            
            # Read and process log file
            with open(tenant_log_path, 'r') as log_file:
                for line in log_file:
                    record = json.loads(line)
                    
                    # Apply time filtering if specified
                    record_time = datetime.fromisoformat(record['timestamp'])
                    if (start_time and record_time < start_time) or \
                       (end_time and record_time > end_time):
                        continue
                    
                    # Update usage summary
                    resource_type = record['resource_type']
                    usage_amount = record['usage_amount']
                    
                    # Aggregate total usage
                    if resource_type not in usage_summary['total_usage_by_resource']:
                        usage_summary['total_usage_by_resource'][resource_type] = 0
                        usage_summary['usage_count_by_resource'][resource_type] = 0
                    
                    usage_summary['total_usage_by_resource'][resource_type] += usage_amount
                    usage_summary['usage_count_by_resource'][resource_type] += 1
                    
                    # Track first and last usage
                    if not usage_summary['first_usage'] or record_time < datetime.fromisoformat(usage_summary['first_usage']):
                        usage_summary['first_usage'] = record['timestamp']
                    
                    if not usage_summary['last_usage'] or record_time > datetime.fromisoformat(usage_summary['last_usage']):
                        usage_summary['last_usage'] = record['timestamp']
            
            return usage_summary
        
        except Exception as e:
            self.logger.error(f"Error generating tenant usage summary: {e}")
            return {}
    
    def analyze_resource_efficiency(
        self, 
        tenant_id: str, 
        time_window: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Analyze resource efficiency and potential optimization opportunities.
        
        :param tenant_id: Unique tenant identifier
        :param time_window: Time window for analysis
        :return: Dictionary with efficiency insights
        """
        try:
            # Get usage summary for the specified time window
            end_time = datetime.now()
            start_time = end_time - time_window
            
            usage_summary = self.get_tenant_usage_summary(
                tenant_id, 
                start_time, 
                end_time
            )
            
            # Prepare efficiency analysis
            efficiency_report = {
                'resource_efficiency': {},
                'recommendations': []
            }
            
            # Calculate efficiency for each resource type
            for resource_type, total_usage in usage_summary.get('total_usage_by_resource', {}).items():
                usage_count = usage_summary.get('usage_count_by_resource', {}).get(resource_type, 0)
                
                # Basic efficiency calculation
                avg_usage = total_usage / usage_count if usage_count > 0 else 0
                
                efficiency_report['resource_efficiency'][resource_type] = {
                    'total_usage': total_usage,
                    'usage_count': usage_count,
                    'average_usage': avg_usage
                }
                
                # Generate recommendations based on usage patterns
                if avg_usage < 0.2:  # Low utilization threshold
                    efficiency_report['recommendations'].append(
                        f"Consider downsizing {resource_type} allocation for tenant {tenant_id}"
                    )
                elif avg_usage > 0.8:  # High utilization threshold
                    efficiency_report['recommendations'].append(
                        f"Consider upgrading {resource_type} for tenant {tenant_id}"
                    )
            
            return efficiency_report
        
        except Exception as e:
            self.logger.error(f"Error analyzing resource efficiency: {e}")
            return {}
    
    def prune_old_logs(self, retention_days: int = 90):
        """
        Remove log files older than specified retention period.
        
        :param retention_days: Number of days to retain log files
        """
        try:
            retention_threshold = datetime.now() - timedelta(days=retention_days)
            
            for filename in os.listdir(self.metrics_dir):
                if filename.endswith('_usage_log.jsonl'):
                    filepath = os.path.join(self.metrics_dir, filename)
                    
                    # Check file modification time
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if file_mtime < retention_threshold:
                        os.remove(filepath)
                        self.logger.info(f"Pruned old log file: {filename}")
        
        except Exception as e:
            self.logger.error(f"Error pruning old logs: {e}")
