package main

import (
	"testing"

	"compliance-governance-agent/internal/policy"
)

func TestEvaluateContractPolicyPass(t *testing.T) {
	facts := policy.ContractFacts{
		CaseID:          "case-1",
		VendorName:      "Acme Corp",
		ContractValue:   450000.0,
		TermYears:       3,
		LiabilityCap:    "limited",
		InsuranceAmount: 2000000.0,
	}
	variance := policy.HistoricalVariance{VarianceFlagged: false}

	result := policy.EvaluateContractPolicy(facts, variance)
	if result.Verdict != "PASS" {
		t.Errorf("Expected PASS, got %s", result.Verdict)
	}
}

func TestEvaluateContractPolicyReview(t *testing.T) {
	facts := policy.ContractFacts{
		CaseID:          "case-2",
		VendorName:      "Acme Corp",
		ContractValue:   650000.0,
		TermYears:       3,
		LiabilityCap:    "unlimited",
		InsuranceAmount: 2000000.0,
	}
	variance := policy.HistoricalVariance{VarianceFlagged: true, LiabilitySpike: true}

	result := policy.EvaluateContractPolicy(facts, variance)
	if result.Verdict != "REVIEW" {
		t.Errorf("Expected REVIEW, got %s", result.Verdict)
	}
	if len(result.Violations) < 2 {
		t.Errorf("Expected at least 2 violations, got %d", len(result.Violations))
	}
}
