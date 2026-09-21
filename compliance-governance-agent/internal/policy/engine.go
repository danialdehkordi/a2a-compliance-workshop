/*
===============================================================================
🏛️ STAGE 2 IMPLEMENTATION: Group B - Go Deterministic Policy Engine
===============================================================================
*/

package policy

import (
	"fmt"
	"strings"
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
	violations := make([]string, 0)

	// 1. Hard Rule: facts.ContractValue > 500,000.0 -> add violation
	if facts.ContractValue > 500000.0 {
		violations = append(violations, fmt.Sprintf("Contract value $%.2f exceeds hard policy cap of $500,000.00", facts.ContractValue))
	}

	// 2. Hard Rule: facts.TermYears > 5 -> add violation
	if facts.TermYears > 5 {
		violations = append(violations, fmt.Sprintf("Contract duration (%d years) exceeds maximum allowable term of 5 years", facts.TermYears))
	}

	// 3. Hard Rule: facts.InsuranceAmount < 1,000,000.0 -> add violation
	if facts.InsuranceAmount < 1000000.0 {
		violations = append(violations, fmt.Sprintf("Insurance coverage $%.2f is below the required minimum floor of $1,000,000.00", facts.InsuranceAmount))
	}

	// 4. Hard Rule: facts.LiabilityCap == "unlimited" -> add violation
	if strings.ToLower(strings.TrimSpace(facts.LiabilityCap)) == "unlimited" {
		violations = append(violations, "Prohibited clause: Unlimited liability is prohibited by corporate policy")
	}

	// 5. Variance Rule: variance.VarianceFlagged -> add historical spike violation (handle variance.LiabilitySpike)
	if variance.VarianceFlagged {
		if variance.LiabilitySpike {
			violations = append(violations, "Historical Variance Alert: Liability risk spike detected vs historical baseline")
		}
		if variance.ValueVariancePct != 0 || !variance.LiabilitySpike {
			violations = append(violations, fmt.Sprintf("Historical Variance Alert: Contract value is +%.1f%% above baseline benchmark", variance.ValueVariancePct))
		}
	}

	// 6. Verdict: "PASS" if len(violations) == 0 else "REVIEW"
	verdict := "PASS"
	if len(violations) > 0 {
		verdict = "REVIEW"
	}

	// 7. CaseID: default to "case-unknown" if facts.CaseID is empty
	caseID := facts.CaseID
	if caseID == "" {
		caseID = "case-unknown"
	}

	// 8. Generate audit certificate HTML using GenerateAuditCertificateHTML(caseID, facts.VendorName, verdict, violations)
	certificateHTML := GenerateAuditCertificateHTML(caseID, facts.VendorName, verdict, violations)

	// 9. Return PolicyCheckResult struct with CaseID, Status: "COMPLETED", Verdict, Violations, CertificateHTML
	return PolicyCheckResult{
		CaseID:          caseID,
		Status:          "COMPLETED",
		Verdict:         verdict,
		Violations:      violations,
		CertificateHTML: certificateHTML,
	}
}

