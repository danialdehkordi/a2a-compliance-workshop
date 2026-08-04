/*
===============================================================================
🏛️ WORKSHOP EXERCISES: Group B - Go Deterministic Policy Engine
===============================================================================
Welcome to Group B's Core Policy Engine!

Your challenge in this file:
  • Exercise 3: Implement `EvaluateContractPolicy()` with deterministic rules

Complete solutions are available in `solutions/compliance-governance-agent/`
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

/*
===========================================================================
TODO (Group B - Exercise 3): Deterministic Policy Rule Evaluator
===========================================================================
Evaluates incoming facts & historical variance against corporate policies:

Rules to Evaluate:
  1. Contract Value > $500,000.00 -> Append Violation:
     "Contract value $X exceeds hard policy cap of $500,000.00"
  2. Term Length > 5 Years -> Append Violation:
     "Term length X years exceeds 5 year policy maximum"
  3. Insurance Amount < $1,000,000.00 -> Append Violation:
     "Insurance coverage $X is below minimum required $1,000,000.00"
  4. Liability Cap == "unlimited" -> Append Violation:
     "Prohibited clause: Unlimited liability is prohibited by corporate policy"
  5. Historical Variance Flagged -> Append Historical Variance Alert:
     - If LiabilitySpike: "Historical Variance Alert: Unprecedented liability clause escalation"
     - Else: "Historical Variance Alert: Contract value is +X% above baseline"

Verdict Logic:
  - If len(violations) > 0 -> Verdict = "REVIEW"
  - Else -> Verdict = "PASS"
===========================================================================
*/
func EvaluateContractPolicy(facts ContractFacts, variance HistoricalVariance) PolicyCheckResult {
	var violations []string

	// -------------------------------------------------------------------------
	// YOUR CODE HERE (Exercise 3)
	// Implement the policy rules above and populate the violations slice!
	// -------------------------------------------------------------------------

	// Starter Example Rule (Replace or expand during your exercise):
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
