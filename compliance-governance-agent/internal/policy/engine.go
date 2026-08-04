/*
===============================================================================
🏛️ WORKSHOP EXERCISES: Group B (Stage 2) - Go Deterministic Policy Engine
===============================================================================
Welcome Group B Developers!

Your hands-on mission in this file:
  • Exercise 3: Implement `EvaluateContractPolicy()` with deterministic rules

Complete working solutions are available in:
  `solutions/compliance-governance-agent/internal/policy/engine.go`
===============================================================================
*/

package policy

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
TODO (Group B / Stage 2 - Exercise 3): Deterministic Policy Rule Evaluator
===========================================================================
Evaluates incoming facts & historical variance against corporate policies:

Rules to Implement:
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
	// TODO (Group B / Stage 2 - Exercise 3): Implement your policy rules here!
	// -------------------------------------------------------------------------

	caseID := facts.CaseID
	if caseID == "" {
		caseID = "case-unknown"
	}

	// Default Exercise Stub Output
	violations = append(violations, "TODO (Group B / Stage 2 - Exercise 3): Implement policy rules in internal/policy/engine.go")

	certHTML := GenerateAuditCertificateHTML(caseID, facts.VendorName, "REVIEW", violations)

	return PolicyCheckResult{
		CaseID:          caseID,
		Status:          "EXERCISE_STUB",
		Verdict:         "UNKNOWN",
		Violations:      violations,
		CertificateHTML: certHTML,
	}
}
