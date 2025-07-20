#!/usr/bin/env python3
"""
scAgent Data Cleaning Framework
==============================

A comprehensive framework for cleaning and filtering genomic datasets
with intelligent multi-stage filtering and quality assessment.

Key Features:
- Multi-stage filtering (Critical -> Confidence -> AI-assisted)
- Field mapping for different data sources (GEO vs SRA)
- Conservative fallback when AI is unavailable
- Detailed reporting and statistics
- Download link generation
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ScAgentDataCleaningFramework:
    """
    Comprehensive data cleaning framework for scAgent.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the framework with configuration."""
        self.config = self._get_default_config()
        if config:
            self.config.update(config)
        
        self.stats = {
            "total_processed": 0,
            "phase1_passed": 0,
            "phase2_passed": 0,
            "phase3_passed": 0,
            "final_passed": 0,
            "rejection_reasons": {},
            "processing_time": 0
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for data cleaning."""
        return {
            # Species filtering
            "required_species": ["Homo sapiens", "human"],
            "species_confidence_threshold": 0.6,  # Lowered from 0.7
            
            # Database requirements
            "require_database_id": True,
            "database_id_confidence_threshold": 0.8,
            
            # Cell line filtering
            "exclude_cell_lines": True,
            "cell_line_confidence_threshold": 0.8,
            
            # Quality thresholds
            "min_overall_score": 3,  # Lowered from 4
            "conservative_score_threshold": 5,  # Accept without AI if score >= 5
            
            # AI settings
            "use_ai_when_available": True,
            "ai_confidence_threshold": 0.6,  # Lowered from 0.7
            "ai_batch_size": 10,
            
            # Conservative fallback settings
            "conservative_fallback": True,
            "conservative_acceptance_threshold": 4,  # Accept if score >= 4 when no AI
            
            # Optional requirements (set to False for more lenient filtering)
            "require_publication": False,
            "require_sample_size": False,
            "require_country_info": False,
            "require_age_info": False,
            "require_tumor_annotation": False,
            "require_sequencing_method": False,
            "require_tissue_source": False
        }
    
    def clean_datasets(
        self, 
        records: List[Dict[str, Any]], 
        use_ai: bool = True
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Main entry point for dataset cleaning.
        
        Args:
            records: List of dataset records to clean
            use_ai: Whether to use AI assistance (if available)
            
        Returns:
            Tuple of (cleaned_records, cleaning_report)
        """
        start_time = datetime.now()
        logger.info(f"Starting comprehensive data cleaning for {len(records)} records")
        
        # Phase 1: Critical Filters (Hard Requirements)
        phase1_results = self._apply_critical_filters(records)
        logger.info(f"Phase 1: {len(phase1_results)} / {len(records)} passed critical filters")
        
        # Phase 2: Confidence-based Filters
        phase2_results = self._apply_confidence_filters(phase1_results)
        logger.info(f"Phase 2: {len(phase2_results['high_confidence'])} high-confidence, "
                   f"{len(phase2_results['uncertain'])} uncertain")
        
        # Phase 3: AI-assisted or Conservative Filtering
        if use_ai and self._ai_available():
            phase3_results = self._apply_ai_filtering(phase2_results['uncertain'])
            logger.info(f"Phase 3: AI processed {len(phase2_results['uncertain'])} uncertain records")
        else:
            phase3_results = self._apply_conservative_filtering(phase2_results['uncertain'])
            logger.info(f"Phase 3: Conservative filtering processed {len(phase2_results['uncertain'])} uncertain records")
        
        # Combine results
        final_results = phase2_results['high_confidence'] + phase3_results
        
        # Update statistics
        self.stats.update({
            "total_processed": len(records),
            "phase1_passed": len(phase1_results),
            "phase2_passed": len(phase2_results['high_confidence']),
            "phase3_passed": len(phase3_results),
            "final_passed": len(final_results),
            "processing_time": (datetime.now() - start_time).total_seconds()
        })
        
        # Generate comprehensive report
        report = self._generate_cleaning_report(records, final_results)
        
        logger.info(f"Data cleaning completed: {len(final_results)} / {len(records)} records retained "
                   f"({len(final_results)/len(records)*100:.1f}%)")
        
        return final_results, report
    
    def _apply_critical_filters(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply critical filters that must pass."""
        passed_records = []
        
        for record in records:
            # Assess critical criteria
            db_assessment = self._assess_database_id(record)
            species_assessment = self._assess_species(record)
            cell_line_assessment = self._assess_cell_line(record)
            
            # Critical filter logic
            passes_critical = True
            rejection_reason = None
            
            # Must have valid database ID
            if self.config["require_database_id"] and db_assessment['score'] == 0:
                passes_critical = False
                rejection_reason = f"Missing database ID: {db_assessment['reason']}"
            
            # Must not be non-human (high confidence)
            elif (species_assessment['score'] == 0 and 
                  species_assessment['confidence'] >= self.config["species_confidence_threshold"]):
                passes_critical = False
                rejection_reason = f"Non-human species: {species_assessment['reason']}"
            
            # Must not be cell line (high confidence)
            elif (self.config["exclude_cell_lines"] and 
                  cell_line_assessment['score'] == 0 and 
                  cell_line_assessment['confidence'] >= self.config["cell_line_confidence_threshold"]):
                passes_critical = False
                rejection_reason = f"Cell line detected: {cell_line_assessment['reason']}"
            
            if passes_critical:
                # Add assessment results to record
                record['sc_eqtl_filter_result'] = {
                    'phase': 'critical_passed',
                    'database_id': db_assessment,
                    'species': species_assessment,
                    'cell_line': cell_line_assessment,
                    'passes_critical': True
                }
                passed_records.append(record)
            else:
                # Track rejection reason
                if rejection_reason not in self.stats["rejection_reasons"]:
                    self.stats["rejection_reasons"][rejection_reason] = 0
                self.stats["rejection_reasons"][rejection_reason] += 1
        
        return passed_records
    
    def _apply_confidence_filters(self, records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Apply confidence-based filtering to separate high-confidence from uncertain cases."""
        high_confidence = []
        uncertain = []
        
        for record in records:
            # Assess all criteria
            assessments = self._assess_all_criteria(record)
            overall_score = sum(assessment['score'] for assessment in assessments.values())
            
            # Add comprehensive assessment to record
            record['sc_eqtl_filter_result'].update({
                'filter_details': assessments,
                'overall_score': overall_score
            })
            
            # Determine confidence level
            if overall_score >= self.config["conservative_score_threshold"]:
                # High confidence acceptance
                record['sc_eqtl_filter_result'].update({
                    'phase': 'high_confidence',
                    'decision': 'accept_high_confidence',
                    'confidence_level': 'high'
                })
                high_confidence.append(record)
            
            elif overall_score >= self.config["min_overall_score"]:
                # Uncertain - needs further review
                record['sc_eqtl_filter_result'].update({
                    'phase': 'uncertain',
                    'confidence_level': 'medium'
                })
                uncertain.append(record)
            
            else:
                # Low score - likely reject but give AI a chance
                record['sc_eqtl_filter_result'].update({
                    'phase': 'uncertain',
                    'confidence_level': 'low'
                })
                uncertain.append(record)
        
        return {'high_confidence': high_confidence, 'uncertain': uncertain}
    
    def _apply_conservative_filtering(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply conservative filtering when AI is not available."""
        accepted_records = []
        
        for record in records:
            filter_result = record['sc_eqtl_filter_result']
            overall_score = filter_result['overall_score']
            
            # Conservative acceptance criteria
            if overall_score >= self.config["conservative_acceptance_threshold"]:
                filter_result.update({
                    'phase': 'conservative_accepted',
                    'decision': 'accept_conservative',
                    'reason': f'Score {overall_score} meets conservative threshold'
                })
                accepted_records.append(record)
            else:
                filter_result.update({
                    'phase': 'conservative_rejected',
                    'decision': 'reject_conservative',
                    'reason': f'Score {overall_score} below conservative threshold ({self.config["conservative_acceptance_threshold"]})'
                })
                # Track rejection
                reason = f"Conservative filter: score {overall_score} < {self.config['conservative_acceptance_threshold']}"
                if reason not in self.stats["rejection_reasons"]:
                    self.stats["rejection_reasons"][reason] = 0
                self.stats["rejection_reasons"][reason] += 1
        
        return accepted_records
    
    def _apply_ai_filtering(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply AI-assisted filtering (placeholder - would integrate with AI model)."""
        # For now, fall back to conservative filtering
        logger.warning("AI filtering not yet implemented, using conservative fallback")
        return self._apply_conservative_filtering(records)
    
    def _assess_database_id(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Assess database ID availability."""
        # Check for GEO IDs
        geo_accession = (record.get('gse') or record.get('geo_accession') or '').strip()
        
        # Check for SRA IDs
        sra_accession = (
            record.get('run_accession') or 
            record.get('sra_run_accession') or 
            record.get('study_accession') or 
            record.get('sra_study_accession') or 
            ''
        ).strip()
        
        if geo_accession and geo_accession.startswith('GSE'):
            return {"score": 2, "confidence": 1.0, "reason": f"Valid GEO ID: {geo_accession}", "evidence": geo_accession}
        elif sra_accession and (sra_accession.startswith(('SRR', 'SRP', 'ERR', 'DRR'))):
            return {"score": 2, "confidence": 1.0, "reason": f"Valid SRA ID: {sra_accession}", "evidence": sra_accession}
        else:
            return {"score": 0, "confidence": 1.0, "reason": "No valid database ID found", "evidence": f"geo:{geo_accession}, sra:{sra_accession}"}
    
    def _assess_species(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Assess species with improved field mapping."""
        # Check taxon_id first (highest confidence)
        taxon_id = str(record.get('taxon_id') or '').strip()
        if taxon_id == '9606':
            return {"score": 2, "confidence": 1.0, "reason": "Human taxon ID (9606)", "evidence": "taxon_id=9606"}
        
        # Check organism fields
        scientific_name = (record.get('scientific_name') or '').lower()
        organism = (record.get('organism') or record.get('geo_organism') or record.get('sra_organism') or '').lower()
        organism_ch1 = (record.get('organism_ch1') or '').lower()
        common_name = (record.get('common_name') or '').lower()
        
        for field in [scientific_name, organism, organism_ch1, common_name]:
            if field and 'homo sapiens' in field:
                return {"score": 2, "confidence": 1.0, "reason": "Explicit Homo sapiens", "evidence": field}
            elif field and field == 'human':
                return {"score": 2, "confidence": 0.9, "reason": "Human in organism field", "evidence": field}
        
        # Check text content
        title = (
            record.get('gse_title') or record.get('geo_title') or 
            record.get('study_title') or record.get('sra_study_title') or ''
        ).lower()
        summary = (
            record.get('summary') or record.get('geo_summary') or 
            record.get('study_abstract') or ''
        ).lower()
        
        text_content = f"{title} {summary}"
        
        if 'homo sapiens' in text_content:
            return {"score": 2, "confidence": 0.8, "reason": "Homo sapiens in text", "evidence": "Found in title/summary"}
        
        # Human indicators
        human_indicators = ['human', 'patient', 'clinical']
        for indicator in human_indicators:
            if indicator in text_content:
                return {"score": 2, "confidence": 0.6, "reason": f"Human indicator: {indicator}", "evidence": indicator}
        
        # Check for non-human indicators
        non_human = ['mouse', 'rat', 'drosophila', 'zebrafish']
        for indicator in non_human:
            if indicator in text_content:
                return {"score": 0, "confidence": 0.9, "reason": f"Non-human: {indicator}", "evidence": indicator}
        
        return {"score": 0, "confidence": 0.5, "reason": "No human indicators", "evidence": "No clear species information"}
    
    def _assess_cell_line(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Assess cell line status."""
        # Get text content
        title = (
            record.get('gse_title') or record.get('geo_title') or 
            record.get('study_title') or record.get('sra_study_title') or ''
        ).lower()
        summary = (
            record.get('summary') or record.get('geo_summary') or 
            record.get('study_abstract') or ''
        ).lower()
        
        text_content = f"{title} {summary}"
        
        # Cell line indicators
        cell_line_keywords = ['hela', 'hek293', '293t', 'jurkat', 'k562', 'cell line']
        for keyword in cell_line_keywords:
            if keyword in text_content:
                return {"score": 0, "confidence": 0.9, "reason": f"Cell line detected: {keyword}", "evidence": keyword}
        
        # Primary tissue indicators
        primary_indicators = ['primary', 'tissue', 'biopsy', 'patient', 'clinical']
        primary_count = sum(1 for indicator in primary_indicators if indicator in text_content)
        
        if primary_count >= 2:
            return {"score": 2, "confidence": 0.8, "reason": "Strong primary tissue indicators", "evidence": f"Primary indicators: {primary_count}"}
        elif primary_count == 1:
            return {"score": 1, "confidence": 0.6, "reason": "Some primary indicators", "evidence": f"Primary indicators: {primary_count}"}
        
        return {"score": 2, "confidence": 0.5, "reason": "No cell line indicators found", "evidence": "No cell line keywords detected"}
    
    def _assess_all_criteria(self, record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Assess all filtering criteria for a record."""
        assessments = {}
        
        # Core assessments (already done in critical phase)
        filter_result = record.get('sc_eqtl_filter_result', {})
        assessments['database_id'] = filter_result.get('database_id', self._assess_database_id(record))
        assessments['species'] = filter_result.get('species', self._assess_species(record))
        assessments['cell_line'] = filter_result.get('cell_line', self._assess_cell_line(record))
        
        # Additional assessments (simplified for now)
        assessments['publication'] = {"score": 1, "confidence": 0.5, "reason": "Publication assessment placeholder"}
        assessments['sample_size'] = {"score": 1, "confidence": 0.5, "reason": "Sample size assessment placeholder"}
        assessments['sequencing_method'] = {"score": 1, "confidence": 0.5, "reason": "Sequencing method placeholder"}
        assessments['tissue_source'] = {"score": 1, "confidence": 0.5, "reason": "Tissue source placeholder"}
        
        return assessments
    
    def _ai_available(self) -> bool:
        """Check if AI model is available."""
        # Placeholder - would check for actual AI model availability
        return False
    
    def _generate_cleaning_report(
        self, 
        original_records: List[Dict[str, Any]], 
        filtered_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive cleaning report."""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_input": len(original_records),
                "total_output": len(filtered_records),
                "retention_rate": (len(filtered_records) / len(original_records) * 100) if original_records else 0,
                "processing_time_seconds": self.stats["processing_time"]
            },
            "phase_statistics": {
                "phase1_critical": {
                    "input": self.stats["total_processed"],
                    "output": self.stats["phase1_passed"],
                    "retention_rate": (self.stats["phase1_passed"] / self.stats["total_processed"] * 100) if self.stats["total_processed"] else 0
                },
                "phase2_confidence": {
                    "input": self.stats["phase1_passed"],
                    "high_confidence_output": self.stats["phase2_passed"],
                    "uncertain_output": self.stats["phase1_passed"] - self.stats["phase2_passed"]
                },
                "phase3_final": {
                    "input": self.stats["phase1_passed"] - self.stats["phase2_passed"],
                    "output": self.stats["phase3_passed"]
                }
            },
            "rejection_reasons": self.stats["rejection_reasons"],
            "configuration": self.config,
            "quality_distribution": self._analyze_quality_distribution(filtered_records)
        }
        
        return report
    
    def _analyze_quality_distribution(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quality score distribution of filtered records."""
        if not records:
            return {}
        
        scores = []
        decisions = {}
        
        for record in records:
            filter_result = record.get('sc_eqtl_filter_result', {})
            score = filter_result.get('overall_score', 0)
            decision = filter_result.get('decision', 'unknown')
            
            scores.append(score)
            decisions[decision] = decisions.get(decision, 0) + 1
        
        return {
            "score_statistics": {
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0,
                "average": sum(scores) / len(scores) if scores else 0
            },
            "decision_distribution": decisions,
            "quality_grades": {
                "high_quality": sum(1 for s in scores if s >= 7),
                "medium_quality": sum(1 for s in scores if 4 <= s < 7),
                "low_quality": sum(1 for s in scores if s < 4)
            }
        }

# Usage example
if __name__ == "__main__":
    # Initialize framework
    framework = ScAgentDataCleaningFramework()
    
    # Example usage
    sample_records = [
        {
            "sra_run_accession": "SRR12345678",
            "study_title": "Human breast cancer single-cell RNA-seq",
            "taxon_id": "9606",
            "scientific_name": "Homo sapiens"
        }
    ]
    
    cleaned_records, report = framework.clean_datasets(sample_records, use_ai=False)
    print(f"Cleaned {len(cleaned_records)} records from {len(sample_records)} input records")
    print(f"Retention rate: {report['summary']['retention_rate']:.1f}%") 