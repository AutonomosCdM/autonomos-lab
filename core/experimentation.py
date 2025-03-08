from typing import Dict, Any, Optional, List, Callable, Union
import uuid
import json
import random
from datetime import datetime
from core.error_handler import AgentError, ErrorSeverity
from core.structured_logger import StructuredLogger

class ExperimentationError(AgentError):
    """Exception raised for experimentation-related errors."""
    pass

class ABTestVariant:
    """
    Represents a single variant in an A/B test.
    """
    def __init__(
        self, 
        name: str, 
        configuration: Dict[str, Any],
        weight: float = 1.0
    ):
        """
        Initialize an A/B test variant.
        
        :param name: Unique name for the variant
        :param configuration: Configuration specific to this variant
        :param weight: Relative weight for variant selection
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.configuration = configuration
        self.weight = weight

class ABTest:
    """
    Manages A/B testing for comparing different configurations or approaches.
    """
    def __init__(
        self, 
        name: str,
        variants: List[ABTestVariant],
        logger: Optional[StructuredLogger] = None
    ):
        """
        Initialize an A/B test.
        
        :param name: Unique name for the A/B test
        :param variants: List of test variants
        :param logger: Optional structured logger
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self._variants = {variant.name: variant for variant in variants}
        self._logger = logger or StructuredLogger()
        
        # Validate variant weights
        total_weight = sum(variant.weight for variant in variants)
        if abs(total_weight - 1.0) > 1e-6:
            raise ExperimentationError(
                "Variant weights must sum to 1.0",
                severity=ErrorSeverity.ERROR
            )
        
        # Tracking
        self._assignments: Dict[str, str] = {}
        self._results: Dict[str, List[Dict[str, Any]]] = {
            variant_name: [] for variant_name in self._variants
        }

    def select_variant(self, subject_id: Optional[str] = None) -> ABTestVariant:
        """
        Select a variant for a given subject based on configured weights.
        
        :param subject_id: Optional identifier to ensure consistent variant assignment
        :return: Selected ABTestVariant
        """
        # Use consistent assignment if subject_id is provided
        if subject_id:
            if subject_id in self._assignments:
                return self._variants[self._assignments[subject_id]]
            
            # Deterministic variant selection based on subject_id
            random.seed(hash(subject_id))
        
        # Select variant based on weights
        variants = list(self._variants.values())
        selected_variant = random.choices(
            variants, 
            weights=[v.weight for v in variants]
        )[0]
        
        # Record assignment if subject_id is provided
        if subject_id:
            self._assignments[subject_id] = selected_variant.name
        
        # Log variant selection
        self._logger.track_event(
            'variant_selected', 
            {
                'test_name': self.name,
                'variant_name': selected_variant.name,
                'variant_id': selected_variant.id
            }
        )
        
        return selected_variant

    def record_result(
        self, 
        variant_name: str, 
        result: Dict[str, Any]
    ):
        """
        Record a result for a specific test variant.
        
        :param variant_name: Name of the variant
        :param result: Result data to record
        """
        if variant_name not in self._variants:
            raise ExperimentationError(
                f"Unknown variant: {variant_name}",
                severity=ErrorSeverity.ERROR
            )
        
        # Add timestamp to result
        result['timestamp'] = datetime.now().isoformat()
        
        # Store result
        self._results[variant_name].append(result)
        
        # Log result
        self._logger.track_event(
            'experiment_result', 
            {
                'test_name': self.name,
                'variant_name': variant_name,
                'result': result
            }
        )

    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze and compare results across variants.
        
        :return: Analysis of experiment results
        """
        analysis = {
            'test_name': self.name,
            'total_subjects': len(self._assignments),
            'variant_performance': {}
        }
        
        for variant_name, results in self._results.items():
            variant_analysis = {
                'total_results': len(results),
                'metrics': self._compute_metrics(results)
            }
            analysis['variant_performance'][variant_name] = variant_analysis
        
        # Log analysis
        self._logger.track_event(
            'experiment_analysis', 
            analysis
        )
        
        return analysis

    def _compute_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compute basic statistical metrics for a set of results.
        
        :param results: List of result dictionaries
        :return: Computed metrics
        """
        if not results:
            return {}
        
        # Assume results contain numeric metrics
        metrics = {}
        
        # Find all numeric metrics
        numeric_keys = [
            key for key in results[0].keys() 
            if isinstance(results[0][key], (int, float))
        ]
        
        for key in numeric_keys:
            values = [result[key] for result in results]
            
            metrics[key] = {
                'mean': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }
        
        return metrics

    def to_json(self) -> str:
        """
        Serialize the A/B test configuration and results.
        
        :return: JSON string representation
        """
        return json.dumps({
            'id': self.id,
            'name': self.name,
            'variants': [
                {
                    'name': variant.name,
                    'id': variant.id,
                    'weight': variant.weight,
                    'configuration': variant.configuration
                }
                for variant in self._variants.values()
            ],
            'assignments': self._assignments,
            'results': self._results
        }, indent=2)

class ExperimentTracker:
    """
    Centralized tracker for managing multiple A/B tests.
    """
    def __init__(self, logger: Optional[StructuredLogger] = None):
        """
        Initialize the experiment tracker.
        
        :param logger: Optional structured logger
        """
        self._tests: Dict[str, ABTest] = {}
        self._logger = logger or StructuredLogger()

    def create_test(
        self, 
        name: str, 
        variants: List[ABTestVariant]
    ) -> ABTest:
        """
        Create a new A/B test.
        
        :param name: Unique name for the test
        :param variants: List of test variants
        :return: Created ABTest instance
        """
        if name in self._tests:
            raise ExperimentationError(
                f"Test '{name}' already exists",
                severity=ErrorSeverity.WARNING
            )
        
        test = ABTest(name, variants, self._logger)
        self._tests[name] = test
        
        # Log test creation
        self._logger.track_event(
            'experiment_created', 
            {
                'test_name': name,
                'variant_names': [v.name for v in variants]
            }
        )
        
        return test

    def get_test(self, name: str) -> ABTest:
        """
        Retrieve an existing A/B test.
        
        :param name: Name of the test
        :return: ABTest instance
        """
        if name not in self._tests:
            raise ExperimentationError(
                f"Test '{name}' not found",
                severity=ErrorSeverity.ERROR
            )
        
        return self._tests[name]

    def list_tests(self) -> List[str]:
        """
        List all registered A/B tests.
        
        :return: List of test names
        """
        return list(self._tests.keys())
