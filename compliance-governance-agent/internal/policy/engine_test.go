package policy

import (
	"strings"
	"testing"
)

func TestEvaluateContractPolicy_AllRulesPass(t *testing.T) {
	facts := ContractFacts{
		CaseID:          "case-pass-1",
		VendorName:      "Acme Cloud Solutions",
		ContractValue:   250000.0,
		TermYears:       2,
		LiabilityCap:    "limited",
		InsuranceAmount: 2000000.0,
	}
	variance := HistoricalVariance{
		VarianceFlagged:  false,
		LiabilitySpike:   false,
		ValueVariancePct: 0.0,
	}

	result := EvaluateContractPolicy(facts, variance)

	if result.Verdict != "PASS" {
		t.Fatalf("expected verdict PASS, got %s", result.Verdict)
	}
	if len(result.Violations) != 0 {
		t.Fatalf("expected 0 violations, got %d: %v", len(result.Violations), result.Violations)
	}
	if result.Status != "COMPLETED" {
		t.Fatalf("expected status COMPLETED, got %s", result.Status)
	}
	if result.CaseID != "case-pass-1" {
		t.Fatalf("expected case ID case-pass-1, got %s", result.CaseID)
	}
	if !strings.Contains(result.CertificateHTML, "PASSED COMPLIANCE") {
		t.Errorf("expected certificate HTML to contain 'PASSED COMPLIANCE'")
	}
}

func TestEvaluateContractPolicy_DefaultCaseID(t *testing.T) {
	facts := ContractFacts{
		CaseID:          "",
		VendorName:      "Acme Cloud",
		ContractValue:   100000.0,
		TermYears:       1,
		LiabilityCap:    "limited",
		InsuranceAmount: 1000000.0,
	}
	variance := HistoricalVariance{VarianceFlagged: false}

	result := EvaluateContractPolicy(facts, variance)
	if result.CaseID != "case-unknown" {
		t.Errorf("expected default case ID 'case-unknown', got %s", result.CaseID)
	}
}

func TestEvaluateContractPolicy_AllViolations(t *testing.T) {
	facts := ContractFacts{
		CaseID:          "case-review-99",
		VendorName:      "Risky Corp",
		ContractValue:   850000.0, // > 500k
		TermYears:       8,        // > 5 yrs
		LiabilityCap:    "Unlimited", // unlimited
		InsuranceAmount: 500000.0, // < 1M
	}
	variance := HistoricalVariance{
		VarianceFlagged:  true,
		LiabilitySpike:   true,
		ValueVariancePct: 45.5,
	}

	result := EvaluateContractPolicy(facts, variance)

	if result.Verdict != "REVIEW" {
		t.Fatalf("expected verdict REVIEW, got %s", result.Verdict)
	}
	// Violations:
	// 1. Contract value > 500k
	// 2. Term > 5 yrs
	// 3. Insurance < 1M
	// 4. Liability == unlimited
	// 5. VarianceFlagged (liability spike + value variance)
	if len(result.Violations) < 5 {
		t.Errorf("expected at least 5 violations, got %d: %v", len(result.Violations), result.Violations)
	}
	if !strings.Contains(result.CertificateHTML, "FLAGGED FOR REVIEW") {
		t.Errorf("expected certificate HTML to contain 'FLAGGED FOR REVIEW'")
	}
}

func TestEvaluateContractPolicy_InsuranceBoundary(t *testing.T) {
	// Exactly 1,000,000 should pass
	facts := ContractFacts{
		CaseID:          "case-boundary",
		VendorName:      "Standard Vendor",
		ContractValue:   500000.0, // exactly 500k <= 500k
		TermYears:       5,        // exactly 5 <= 5
		LiabilityCap:    "limited",
		InsuranceAmount: 1000000.0, // exactly 1M >= 1M
	}
	variance := HistoricalVariance{VarianceFlagged: false}

	result := EvaluateContractPolicy(facts, variance)
	if result.Verdict != "PASS" {
		t.Fatalf("expected boundary values (500k, 5yr, 1M ins) to PASS, got %s with violations: %v", result.Verdict, result.Violations)
	}
}
