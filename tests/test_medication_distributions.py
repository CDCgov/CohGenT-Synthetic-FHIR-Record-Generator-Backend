"""
Test medication set distribution across a cohort.
Validates that weighted medication set selection produces expected distributions.
"""

import pytest
from collections import Counter
from api.models.cohort_settings import MedicationSet, Medication
from api.models.value_types import ValueCoding
from api.features.generation.weighted_values import select_medication_set


class TestMedicationSetDistributions:
    """Test medication set weighted selection distributions."""
    
    @pytest.fixture
    def medication_sets_equal_weight(self):
        """Two medication sets with equal weights (0.5 each)."""
        return [
            MedicationSet(
                weight=0.5,
                medications=[
                    Medication(
                        codeable_concept=ValueCoding(
                            system="http://www.nlm.nih.gov/research/umls/rxnorm",
                            code="1049221",
                            display="Amoxicillin 500 MG"
                        ),
                        dosage="500mg twice daily"
                    )
                ]
            ),
            MedicationSet(
                weight=0.5,
                medications=[
                    Medication(
                        codeable_concept=ValueCoding(
                            system="http://www.nlm.nih.gov/research/umls/rxnorm",
                            code="1668240",
                            display="Azithromycin 250 MG"
                        ),
                        dosage="250mg once daily"
                    )
                ]
            )
        ]
    
    @pytest.fixture
    def medication_sets_unequal_weight(self):
        """Three medication sets with different weights (0.6, 0.3, 0.1)."""
        return [
            MedicationSet(
                weight=0.6,
                medications=[
                    Medication(
                        codeable_concept=ValueCoding(
                            system="http://www.nlm.nih.gov/research/umls/rxnorm",
                            code="1049221",
                            display="Amoxicillin 500 MG"
                        )
                    )
                ]
            ),
            MedicationSet(
                weight=0.3,
                medications=[
                    Medication(
                        codeable_concept=ValueCoding(
                            system="http://www.nlm.nih.gov/research/umls/rxnorm",
                            code="1668240",
                            display="Azithromycin 250 MG"
                        )
                    )
                ]
            ),
            MedicationSet(
                weight=0.1,
                medications=[
                    Medication(
                        codeable_concept=ValueCoding(
                            system="http://www.nlm.nih.gov/research/umls/rxnorm",
                            code="1790533",
                            display="Doxycycline 100 MG"
                        )
                    )
                ]
            )
        ]
    
    def test_equal_weight_distribution(self, medication_sets_equal_weight):
        """Test that equal weights produce roughly 50/50 distribution."""
        sample_size = 1000
        selections = []
        
        for _ in range(sample_size):
            selected = select_medication_set(medication_sets_equal_weight)
            # Use first medication's display as identifier
            med_name = selected.medications[0].codeable_concept.display
            selections.append(med_name)
        
        counts = Counter(selections)
        
        # Should have exactly 2 different medications selected
        assert len(counts) == 2
        
        # Each should be approximately 50% (±5% tolerance for 1000 samples)
        amoxicillin_pct = counts["Amoxicillin 500 MG"] / sample_size
        azithromycin_pct = counts["Azithromycin 250 MG"] / sample_size
        
        assert 0.45 <= amoxicillin_pct <= 0.55, f"Amoxicillin: {amoxicillin_pct:.2%}"
        assert 0.45 <= azithromycin_pct <= 0.55, f"Azithromycin: {azithromycin_pct:.2%}"
    
    def test_unequal_weight_distribution(self, medication_sets_unequal_weight):
        """Test that unequal weights produce expected proportions."""
        sample_size = 1000
        selections = []
        
        for _ in range(sample_size):
            selected = select_medication_set(medication_sets_unequal_weight)
            med_name = selected.medications[0].codeable_concept.display
            selections.append(med_name)
        
        counts = Counter(selections)
        
        # Should have all 3 medications selected (with high probability)
        assert len(counts) == 3
        
        # Check proportions (with appropriate tolerances)
        amoxicillin_pct = counts["Amoxicillin 500 MG"] / sample_size
        azithromycin_pct = counts["Azithromycin 250 MG"] / sample_size
        doxycycline_pct = counts["Doxycycline 100 MG"] / sample_size
        
        # 60% ±5%
        assert 0.55 <= amoxicillin_pct <= 0.65, f"Amoxicillin: {amoxicillin_pct:.2%}"
        # 30% ±5%
        assert 0.25 <= azithromycin_pct <= 0.35, f"Azithromycin: {azithromycin_pct:.2%}"
        # 10% ±3% (smaller tolerance for smaller proportion)
        assert 0.07 <= doxycycline_pct <= 0.13, f"Doxycycline: {doxycycline_pct:.2%}"
    
    def test_reproducibility_with_seed(self, medication_sets_equal_weight):
        """Test that same seed produces same medication selections."""
        import random
        
        sample_size = 100
        
        # First run with seed
        random.seed(42)
        first_run = [
            select_medication_set(medication_sets_equal_weight).medications[0].codeable_concept.display
            for _ in range(sample_size)
        ]
        
        # Second run with same seed
        random.seed(42)
        second_run = [
            select_medication_set(medication_sets_equal_weight).medications[0].codeable_concept.display
            for _ in range(sample_size)
        ]
        
        assert first_run == second_run
    
    def test_single_medication_set(self):
        """Test that single medication set is always selected."""
        single_set = [
            MedicationSet(
                weight=1.0,
                medications=[
                    Medication(
                        codeable_concept=ValueCoding(
                            system="http://www.nlm.nih.gov/research/umls/rxnorm",
                            code="1049221",
                            display="Amoxicillin 500 MG"
                        )
                    )
                ]
            )
        ]
        
        # Should always return the same set
        for _ in range(100):
            selected = select_medication_set(single_set)
            assert selected.medications[0].codeable_concept.display == "Amoxicillin 500 MG"
    
    def test_medication_set_returns_correct_structure(self, medication_sets_equal_weight):
        """Test that selected medication set has expected structure."""
        selected = select_medication_set(medication_sets_equal_weight)
        
        # Should return a MedicationSet
        assert isinstance(selected, MedicationSet)
        
        # Should have medications list
        assert len(selected.medications) > 0
        
        # Each medication should have required fields
        for med in selected.medications:
            assert isinstance(med, Medication)
            assert med.codeable_concept.system
            assert med.codeable_concept.code
            assert med.codeable_concept.display