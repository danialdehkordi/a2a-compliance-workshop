package policy

import (
	"fmt"
	"strings"
)

func GenerateAuditCertificateHTML(caseID, vendorName, verdict string, violations []string) string {
	passed := (verdict == "PASS")
	statusClass := "approved"
	verdictText := "PASSED COMPLIANCE"
	verdictCaption := "Zero policy threshold exceptions identified."
	badgeBorder := "var(--success)"
	stampHTML := `<div class="stamp approved-stamp">Approved Safe</div>`

	if !passed {
		statusClass = "flagged"
		verdictText = "FLAGGED FOR REVIEW"
		count := len(violations)
		plural := "s"
		if count == 1 {
			plural = ""
		}
		verdictCaption = fmt.Sprintf("%d policy exception%s require legal review.", count, plural)
		badgeBorder = "var(--error)"
		stampHTML = `<div class="stamp rejected-stamp">Review Required</div>`
	}

	var violationsLI string
	if passed {
		violationsLI = `<li><span>Clear</span><strong>Zero policy threshold exceptions identified.</strong></li>`
	} else {
		var items []string
		for idx, v := range violations {
			items = append(items, fmt.Sprintf(`<li><span>Exception %d</span><strong>%s</strong></li>`, idx+1, v))
		}
		violationsLI = strings.Join(items, "\n")
	}

	return fmt.Sprintf(`<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Compliance Certificate - %s</title>
    <style>
      :root {
        --bg: #121212;
        --card: #181818;
        --card-soft: #1f1f1f;
        --ink: #ffffff;
        --muted: #b3b3b3;
        --quiet: #7c7c7c;
        --line: #4d4d4d;
        --success: #1ed760;
        --success-ink: #121212;
        --error: #f3727f;
        --amber: #ffa42b;
        --shadow-heavy: rgba(0, 0, 0, 0.5) 0px 8px 24px;
        --shadow-card: rgba(0, 0, 0, 0.3) 0px 8px 8px;
        --font-title: SpotifyMixUITitle, CircularSp-Arab, CircularSp-Hebr, "Helvetica Neue", Helvetica, Arial, sans-serif;
        --font-ui: SpotifyMixUI, CircularSp-Arab, CircularSp-Hebr, "Helvetica Neue", Helvetica, Arial, sans-serif;
      }
      body {
        margin: 0;
        padding: 24px 16px;
        color: var(--ink);
        font-family: var(--font-ui);
        background: var(--bg);
      }
      main {
        max-width: 720px;
        margin: 0 auto;
        padding: 28px 24px;
        border-radius: 8px;
        background: var(--card);
        box-shadow: var(--shadow-heavy);
      }
      h1 {
        margin: 0 0 6px;
        font-family: var(--font-title);
        font-size: 22px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        line-height: 1.15;
      }
      h2 {
        margin: 22px 0 10px;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: var(--quiet);
        border-bottom: 1px solid var(--line);
        padding-bottom: 6px;
      }
      p, li {
        font-size: 13px;
        line-height: 1.5;
        color: var(--muted);
      }
      .badge-strip {
        border: 1px solid var(--line);
        padding: 16px;
        border-radius: 8px;
        margin: 18px 0;
        text-align: center;
        background: var(--card-soft);
        box-shadow: var(--shadow-card);
      }
      .badge-strip.approved {
        border-color: var(--success);
        color: var(--success);
      }
      .badge-strip.flagged {
        border-color: var(--error);
        color: var(--error);
      }
      .badge-strip strong {
        display: block;
        font-size: 24px;
        font-weight: 700;
        letter-spacing: 1.2px;
        margin-bottom: 4px;
      }
      .badge-strip span {
        display: block;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
      }
      .exception-count {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 28px;
        height: 24px;
        margin-right: 8px;
        border-radius: 999px;
        background: var(--card-soft);
        color: var(--error);
        font-weight: 700;
        font-size: 11px;
      }
      .exception-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 0;
        list-style: none;
      }
      .exception-list li {
        border: 1px solid var(--line);
        border-left: 4px solid %s;
        border-radius: 8px;
        background: var(--card-soft);
        padding: 10px 12px;
      }
      .exception-list span {
        display: block;
        margin-bottom: 3px;
        color: var(--quiet);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
      }
      .exception-list strong {
        color: var(--ink);
        font-size: 13px;
        line-height: 1.4;
      }
      .cert-meta {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 16px;
        align-items: center;
        margin-top: 24px;
        padding-top: 16px;
        border-top: 1px solid var(--line);
        font-size: 11px;
        color: var(--quiet);
      }
      .stamp {
        border: 2px dashed var(--line);
        padding: 8px 16px;
        text-align: center;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: bold;
        text-transform: uppercase;
      }
      .stamp.approved-stamp {
        border-color: var(--success);
        color: var(--success);
      }
      .stamp.rejected-stamp {
        border-color: var(--error);
        color: var(--error);
      }
    </style>
  </head>
  <body>
    <main>
      <div style="text-align: center; margin-bottom: 12px;">
        <h1 style="color: var(--quiet); font-size: 11px; margin-bottom: 4px; font-weight: 700;">Contract Compliance Engine</h1>
        <h1>A2A Audit Certificate</h1>
      </div>
      
      <div class="badge-strip %s">
        <strong>%s</strong>
        <span>%s</span>
      </div>
      
      <h2>Validation Diagnostics Summary</h2>
      <p>
        Contract compliance validation conducted by <strong>compliance-governance-agent</strong> running compiled Go deterministic policy rules.
      </p>
      
      <h2>Policy Threshold Findings</h2>
      <ul class="exception-list">
        %s
      </ul>
      
      <div class="cert-meta">
        <div>
          <strong>Case ID:</strong> %s<br />
          <strong>Vendor Name:</strong> %s<br />
          <strong>Protocol:</strong> A2A JSON-RPC 2.0 (message/send)
        </div>
        <div>
          %s
        </div>
      </div>
    </main>
  </body>
</html>`, vendorName, badgeBorder, statusClass, verdictText, verdictCaption, violationsLI, caseID, vendorName, stampHTML)
}
