"""
Tests for patient distribution generation.
Verifies that demographic distributions (gender, race, ethnicity) 
are generated according to specified weights.
"""
import pytest
from collections import Counter
from api.features.generation.generation import setup_patient_distributions, generate_entities, parse_default_settings
from api.utilities.file_reader import get_use_case_by_id
from api.models.cohort_settings import CohortSettings
import api.features.generation.constants as C


class TestPatientDistributions:
    """Test patient demographic distribution generation."""
    
    @pytest.fixture
    def use_case(self):
        """Load the condition-based-record use case."""
        return get_use_case_by_id("condition-based-record")
    
    @pytest.fixture
    def entities(self, use_case):
        """Generate entities from use case."""
        return generate_entities(use_case)
    
    @pytest.fixture
    def default_settings(self, use_case):
        """Parse default settings from use case."""
        if use_case.form_rules is None:
            pytest.fail("No form rules found in use case")
        return parse_default_settings(use_case.form_rules)
    
    @pytest.fixture
    def cohort_config(self):
        """Create cohort configuration with known distributions."""
        from api.models.cohort_settings import EventPeriod, Setting
        from api.models.value_types import ValueWeights
        
        # Use model_construct to bypass count validation (le=50) for statistical testing
        return CohortSettings.model_construct(
            useCaseId="condition-based-record",
            count=1000,  # Large sample for statistical testing (bypasses le=50 constraint)
            seed=12345,
            eventPeriod=EventPeriod.model_validate({
                "start": "2026-01-01",
                "end": "2026-12-31"
            }),
            userResponses=[
                Setting.model_validate({
                    "ruleId": "patient-sex",
                    "value": ValueWeights.model_validate({
                        "values": [
                            {"value": "Male", "weight": 0.5},
                            {"value": "Female", "weight": 0.5},
                            {"value": "Unknown", "weight": 0.0}
                        ]
                    })
                }),
                Setting.model_validate({
                    "ruleId": "patient-race",
                    "value": ValueWeights.model_validate({
                        "values": [
                            {"value": "White", "weight": 0.64},
                            {"value": "Black or African American", "weight": 0.15},
                            {"value": "Asian", "weight": 0.08},
                            {"value": "Other Race", "weight": 0.08},
                            {"value": "Native Hawaiian or Other Pacific Islander", "weight": 0.03},
                            {"value": "American Indian or Native Alaskan", "weight": 0.02},
                            {"value": "Unknown", "weight": 0.0}
                        ]
                    })
                }),
                Setting.model_validate({
                    "ruleId": "patient-ethnicity",
                    "value": ValueWeights.model_validate({
                        "values": [
                            {"value": "Not Hispanic or Latino", "weight": 0.8},
                            {"value": "Hispanic or Latino", "weight": 0.2},
                            {"value": "Unknown", "weight": 0.0}
                        ]
                    })
                })
            ]
        )
    
    def test_distribution_count(self, entities, cohort_config, default_settings):
        """Test that distributions generate the correct number of values."""
        distributions = setup_patient_distributions(entities, cohort_config, default_settings)
        
        assert C.PatientDistributionFields.GENDER.value in distributions
        assert C.PatientDistributionFields.RACE.value in distributions
        assert C.PatientDistributionFields.ETHNICITY.value in distributions
        
        assert len(distributions[C.PatientDistributionFields.GENDER.value]) == cohort_config.count
        assert len(distributions[C.PatientDistributionFields.RACE.value]) == cohort_config.count
        assert len(distributions[C.PatientDistributionFields.ETHNICITY.value]) == cohort_config.count
    
    def test_gender_distribution(self, entities, cohort_config, default_settings):
        """Test gender distribution matches expected proportions."""
        distributions = setup_patient_distributions(entities, cohort_config, default_settings)
        gender_values = distributions[C.PatientDistributionFields.GENDER.value]
        
        counts = Counter(gender_values)
        total = len(gender_values)
        
        # Expected: 50% Male, 50% Female, 0% Unknown
        male_pct = counts.get("Male", 0) / total
        female_pct = counts.get("Female", 0) / total
        unknown_count = counts.get("Unknown", 0)
        
        # Allow 5% tolerance for randomization (with 1000 samples this is reasonable)
        assert 0.45 <= male_pct <= 0.55, f"Male percentage {male_pct:.2%} outside expected range"
        assert 0.45 <= female_pct <= 0.55, f"Female percentage {female_pct:.2%} outside expected range"
        assert unknown_count == 0, "Unknown gender should not appear (weight=0)"
    
    def test_race_distribution(self, entities, cohort_config, default_settings):
        """Test race distribution matches expected proportions."""
        distributions = setup_patient_distributions(entities, cohort_config, default_settings)
        race_values = distributions[C.PatientDistributionFields.RACE.value]
        
        counts = Counter(race_values)
        total = len(race_values)
        
        expected_distributions = {
            "White": (0.64, 0.05),  # (expected, tolerance)
            "Black or African American": (0.15, 0.03),
            "Asian": (0.08, 0.02),
            "Other Race": (0.08, 0.02),
            "Native Hawaiian or Other Pacific Islander": (0.03, 0.02),
            "American Indian or Native Alaskan": (0.02, 0.02),
        }
        
        for race, (expected, tolerance) in expected_distributions.items():
            actual = counts.get(race, 0) / total
            assert expected - tolerance <= actual <= expected + tolerance, \
                f"{race}: {actual:.2%} outside expected {expected:.2%} ± {tolerance:.2%}"
        
        assert counts.get("Unknown", 0) == 0, "Unknown race should not appear (weight=0)"
    
    def test_ethnicity_distribution(self, entities, cohort_config, default_settings):
        """Test ethnicity distribution matches expected proportions."""
        distributions = setup_patient_distributions(entities, cohort_config, default_settings)
        ethnicity_values = distributions[C.PatientDistributionFields.ETHNICITY.value]
        
        counts = Counter(ethnicity_values)
        total = len(ethnicity_values)
        
        # Expected: 80% Not Hispanic, 20% Hispanic, 0% Unknown
        not_hispanic_pct = counts.get("Not Hispanic or Latino", 0) / total
        hispanic_pct = counts.get("Hispanic or Latino", 0) / total
        unknown_count = counts.get("Unknown", 0)
        
        assert 0.75 <= not_hispanic_pct <= 0.85, f"Not Hispanic percentage {not_hispanic_pct:.2%} outside expected range"
        assert 0.15 <= hispanic_pct <= 0.25, f"Hispanic percentage {hispanic_pct:.2%} outside expected range"
        assert unknown_count == 0, "Unknown ethnicity should not appear (weight=0)"
    
    def test_reproducibility_with_seed(self, entities, cohort_config, default_settings):
        """Test that same seed produces identical distributions."""
        import random
        from faker import Faker
        
        # Generate distributions twice with same seed
        Faker.seed(cohort_config.seed)
        random.seed(cohort_config.seed)
        distributions1 = setup_patient_distributions(entities, cohort_config, default_settings)
        
        Faker.seed(cohort_config.seed)
        random.seed(cohort_config.seed)
        distributions2 = setup_patient_distributions(entities, cohort_config, default_settings)
        
        # Should be identical
        for field in C.PATIENT_DIST_FIELDS_SET:
            assert distributions1[field] == distributions2[field], \
                f"Distributions for {field} not reproducible with same seed"
    
    def test_values_consumed_correctly(self, entities, cohort_config, default_settings):
        """Test that values can be popped from distribution in order."""
        distributions = setup_patient_distributions(entities, cohort_config, default_settings)
        
        gender_dist = distributions[C.PatientDistributionFields.GENDER.value].copy()
        initial_count = len(gender_dist)
        
        # Pop 10 values
        for i in range(10):
            value = gender_dist.pop()
            assert value in ["Male", "Female"], f"Unexpected value: {value}"
        
        assert len(gender_dist) == initial_count - 10, "Values not being consumed correctly"
    
    def test_empty_use_case_distributions(self, cohort_config, default_settings):
        """Test that function handles use cases without patient distribution fields gracefully."""
        # Create entities list without Patient entity
        entities = []
        
        distributions = setup_patient_distributions(entities, cohort_config, default_settings)
        
        # Should return empty dict without crashing
        assert isinstance(distributions, dict)
        assert len(distributions) == 0