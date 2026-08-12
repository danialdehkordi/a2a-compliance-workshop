/*
===============================================================================
🏛️ STAGE 2 IMPLEMENTATION: Group B - Go Deterministic Policy Engine
===============================================================================
*/

package policy

import (
	"fmt"
)

type ContractFacts struct {
	CaseID          string  `json:"case_id"`
	VendorName      string  `json:"vendor_name"`
	ContractValue   float64 `json:"contract_value"`
	TermYears       int     `json:"term_years"`
	LiabilityCap    string  `json:"liability_cap"`
	InsuranceAmount float64 `json:"insurance_amount"`
}

type HistoricalVariance struct {
	VendorName         string  `json:"vendor_name"`
	HistoricalAvgValue float64 `json:"historical_avg_value"`
	CurrentValue       float64 `json:"current_value"`
	ValueVariancePct   float64 `json:"value_variance_pct"`
	VarianceFlagged    bool    `json:"variance_flagged"`
	LiabilitySpike     bool    `json:"liability_spike"`
}

type PolicyCheckResult struct {
	CaseID          string   `json:"case_id"`
	Status          string   `json:"status"`
	Verdict         string   `json:"verdict"`
	Violations      []string `json:"violations"`
	CertificateHTML string   `json:"certificate_html"`
}

func EvaluateContractPolicy(facts ContractFacts, variance HistoricalVariance) PolicyCheckResult {
	var violations []string

	// 1. Hard Corporate Policy Rules
	if facts.ContractValue > 500000.0 {
		violations = append(violations, fmt.Sprintf("Contract value $%.2f exceeds hard policy cap of $500,000.00", facts.ContractValue))
	}

	if facts.TermYears > 5 {
		violations = append(violations, fmt.Sprintf("Term length %d years exceeds 5 year policy maximum", facts.TermYears))
	}

	if facts.InsuranceAmount < 1000000.0 {
		violations = append(violations, fmt.Sprintf("Insurance coverage $%.2f is below minimum required $1,000,000.00", facts.InsuranceAmount))
	}

	if facts.LiabilityCap == "unlimited" {
		violations = append(violations, "Prohibited clause: Unlimited liability is prohibited by corporate policy")
	}

	// 2. Historical Variance Rules
	if variance.VarianceFlagged {
		if variance.LiabilitySpike {
			violations = append(violations, "Historical Variance Alert: Unprecedented liability clause escalation compared to vendor history")
		} else {
			violations = append(violations, fmt.Sprintf("Historical Variance Alert: Contract value is +%.1f%% above historical vendor baseline ($%.2f)", variance.ValueVariancePct, variance.HistoricalAvgValue))
		}
	}

	verdict := "PASS"
	if len(violations) > 0 {
		verdict = "REVIEW"
	}

	caseID := facts.CaseID
	if caseID == "" {
		caseID = "case-unknown"
	}

	certHTML := GenerateAuditCertificateHTML(caseID, facts.VendorName, verdict, violations)

	return PolicyCheckResult{
		CaseID:          caseID,
		Status:          "COMPLETED",
		Verdict:         verdict,
		Violations:      violations,
		CertificateHTML: certHTML,
	}
}
