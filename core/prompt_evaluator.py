import logging
import logging
from typing import Dict, Any, List, Optional
import json
import os
import uuid
from datetime import datetime, timedelta
import numpy as np
import re

class PromptEvaluator:
    """
    Evaluates and scores prompts based on multiple quality metrics.
    Provides comprehensive analysis of prompt effectiveness and performance.
    """
    
    def __init__(
        self, 
        evaluation_dir: str = 'data/prompt_evaluations',
        ab_test_manager: Optional['ABTestManager'] = None
    ):
        """
        Initialize PromptEvaluator.
        
        :param evaluation_dir: Directory to store prompt evaluation results
        :param ab_test_manager: Optional ABTestManager for experimental tracking
        """
        self.evaluation_dir = evaluation_dir
        self.ab_test_manager = ab_test_manager
        self.logger = logging.getLogger(__name__)
        
        # Ensure evaluation directory exists
        os.makedirs(evaluation_dir, exist_ok=True)
        os.makedirs(os.path.join(evaluation_dir, 'metrics'), exist_ok=True)
        os.makedirs(os.path.join(evaluation_dir, 'reports'), exist_ok=True)
    
    def evaluate_prompt(
        self, 
        prompt: str, 
        evaluation_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a prompt based on multiple quality metrics.
        
        :param prompt: Prompt text to evaluate
        :param evaluation_criteria: Optional custom evaluation criteria
        :return: Dictionary with prompt evaluation metrics
        """
        try:
            # Generate unique evaluation ID
            evaluation_id = str(uuid.uuid4())
            
            # Default evaluation criteria
            default_criteria = {
                'clarity': self._evaluate_clarity,
                'specificity': self._evaluate_specificity,
                'complexity': self._evaluate_complexity,
                'instruction_quality': self._evaluate_instruction_quality,
                'context_relevance': self._evaluate_context_relevance
            }
            
            # Merge default and custom criteria
            criteria = {**default_criteria, **(evaluation_criteria or {})}
            
            # Prepare evaluation results
            evaluation_results = {
                'id': evaluation_id,
                'prompt': prompt,
                'timestamp': datetime.now().isoformat(),
                'metrics': {}
            }
            
            # Evaluate prompt using each criterion
            for metric_name, evaluation_func in criteria.items():
                try:
                    metric_score = evaluation_func(prompt)
                    evaluation_results['metrics'][metric_name] = metric_score
                except Exception as metric_error:
                    self.logger.warning(
                        f"Error evaluating {metric_name} metric: {metric_error}"
                    )
                    evaluation_results['metrics'][metric_name] = None
            
            # Calculate overall prompt quality score
            valid_metrics = [
                score for score in evaluation_results['metrics'].values() 
                if score is not None
            ]
            
            evaluation_results['overall_quality_score'] = (
                np.mean(valid_metrics) if valid_metrics else None
            )
            
            # Save evaluation results
            results_path = os.path.join(
                self.evaluation_dir, 
                'metrics', 
                f'{evaluation_id}_evaluation.json'
            )
            
            with open(results_path, 'w') as f:
                json.dump(evaluation_results, f, indent=2)
            
            # Optional: Log to ABTestManager if available
            if self.ab_test_manager:
                self.ab_test_manager.record_interaction(
                    'prompt_evaluation', 
                    'system', 
                    {
                        'overall_quality_score': evaluation_results['overall_quality_score'],
                        **{
                            f'{k}_score': v 
                            for k, v in evaluation_results['metrics'].items()
                        }
                    }
                )
            
            return evaluation_results
        
        except Exception as e:
            self.logger.error(f"Error evaluating prompt: {e}")
            return {}
    
    def _evaluate_clarity(self, prompt: str) -> float:
        """
        Evaluate prompt clarity based on sentence structure and readability.
        
        :param prompt: Prompt text to evaluate
        :return: Clarity score (0-1)
        """
        # Analyze sentence length and complexity
        sentences = re.split(r'[.!?]', prompt)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Calculate average sentence length
        avg_sentence_length = np.mean([len(s.split()) for s in sentences]) if sentences else 0
        
        # Penalize very long or very short sentences
        clarity_score = 1 - min(abs(avg_sentence_length - 15) / 15, 1)
        
        # Check for clear instructions
        has_clear_instruction = any(
            keyword in prompt.lower() 
            for keyword in ['please', 'provide', 'explain', 'describe']
        )
        
        return (clarity_score * 0.7) + (0.3 if has_clear_instruction else 0)
    
    def _evaluate_specificity(self, prompt: str) -> float:
        """
        Evaluate prompt specificity by analyzing detail and precision.
        
        :param prompt: Prompt text to evaluate
        :return: Specificity score (0-1)
        """
        # Count specific nouns, verbs, and quantitative terms
        specific_nouns = len(re.findall(r'\b[A-Z][a-z]+\b', prompt))
        quantitative_terms = len(re.findall(r'\b\d+\b|\b\d+\.\d+\b', prompt))
        
        # Analyze verb specificity
        specific_verbs = len(re.findall(
            r'\b(analyze|calculate|determine|evaluate|compare|contrast)\b', 
            prompt.lower()
        ))
        
        # Combine metrics
        specificity_score = min(
            (specific_nouns * 0.3 + specific_verbs * 0.4 + quantitative_terms * 0.3) / 10, 
            1
        )
        
        return specificity_score
    
    def _evaluate_complexity(self, prompt: str) -> float:
        """
        Evaluate prompt complexity and sophistication.
        
        :param prompt: Prompt text to evaluate
        :return: Complexity score (0-1)
        """
        # Analyze vocabulary complexity
        unique_words = set(prompt.lower().split())
        total_words = len(prompt.split())
        
        # Calculate lexical diversity
        lexical_diversity = len(unique_words) / total_words if total_words > 0 else 0
        
        # Check for complex sentence structures
        complex_structures = len(re.findall(r'\b(while|although|despite|however)\b', prompt.lower()))
        
        # Combine metrics
        complexity_score = min(
            (lexical_diversity * 0.6 + complex_structures * 0.4), 
            1
        )
        
        return complexity_score
    
    def _evaluate_instruction_quality(self, prompt: str) -> float:
        """
        Evaluate the quality of instructions in the prompt.
        
        :param prompt: Prompt text to evaluate
        :return: Instruction quality score (0-1)
        """
        # Check for clear, actionable instructions
        instruction_keywords = [
            'explain', 'describe', 'analyze', 'compare', 'contrast', 
            'provide details', 'break down', 'elaborate on'
        ]
        
        instruction_count = sum(
            keyword in prompt.lower() 
            for keyword in instruction_keywords
        )
        
        # Check for context or constraints
        context_indicators = [
            'given', 'considering', 'based on', 'in the context of', 
            'taking into account', 'with respect to'
        ]
        
        context_count = sum(
            indicator in prompt.lower() 
            for indicator in context_indicators
        )
        
        # Combine metrics
        instruction_score = min(
            (instruction_count * 0.6 + context_count * 0.4) / 3, 
            1
        )
        
        return instruction_score
    
    def _evaluate_context_relevance(self, prompt: str) -> float:
        """
        Evaluate the relevance and specificity of context in the prompt.
        
        :param prompt: Prompt text to evaluate
        :return: Context relevance score (0-1)
        """
        # Check for domain-specific terminology
        domain_keywords = {
            'technical': ['algorithm', 'architecture', 'optimization', 'framework'],
            'scientific': ['hypothesis', 'experiment', 'methodology', 'research'],
            'business': ['strategy', 'market', 'competitive', 'innovation'],
            'creative': ['narrative', 'character', 'theme', 'perspective']
        }
        
        domain_scores = {
            domain: sum(keyword in prompt.lower() for keyword in keywords)
            for domain, keywords in domain_keywords.items()
        }
        
        # Find the most relevant domain
        most_relevant_domain = max(domain_scores, key=domain_scores.get)
        
        # Check for specific context references
        context_score = domain_scores[most_relevant_domain] / len(domain_keywords[most_relevant_domain])
        
        return min(context_score, 1)
    
    def compare_prompts(
        self, 
        prompts: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple prompts across different evaluation metrics.
        
        :param prompts: List of prompts to compare
        :return: Comparative analysis of prompts
        """
        try:
            # Evaluate each prompt
            prompt_evaluations = [
                self.evaluate_prompt(prompt) 
                for prompt in prompts
            ]
            
            # Prepare comparative analysis
            comparison_results = {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'prompts': prompts,
                'metric_comparisons': {}
            }
            
            # Compare metrics across prompts
            for metric_name in prompt_evaluations[0]['metrics']:
                metric_values = [
                    eval['metrics'][metric_name] 
                    for eval in prompt_evaluations
                ]
                
                comparison_results['metric_comparisons'][metric_name] = {
                    'values': metric_values,
                    'best_prompt_index': metric_values.index(max(metric_values))
                }
            
            # Calculate overall best prompt
            overall_scores = [
                eval.get('overall_quality_score', 0) 
                for eval in prompt_evaluations
            ]
            
            comparison_results['best_overall_prompt_index'] = overall_scores.index(max(overall_scores))
            
            # Save comparison results
            results_path = os.path.join(
                self.evaluation_dir, 
                'reports', 
                f'{comparison_results["id"]}_comparison.json'
            )
            
            with open(results_path, 'w') as f:
                json.dump(comparison_results, f, indent=2)
            
            return comparison_results
        
        except Exception as e:
            self.logger.error(f"Error comparing prompts: {e}")
            return {}
