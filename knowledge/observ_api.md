# OBSERV 520x — Sylton Cloud API Integration Reference

## Overview
The OBSERV 520x is the skin analysis imaging system used at Treasury Aesthetics for baseline assessments and progress tracking. It is managed through the **Sylton Connect** platform at `connect.sylton.com`.

---

## OBSERV Imaging Modes

The OBSERV 520x captures skin analysis across multiple light modes:

| Mode | What it reveals |
|------|----------------|
| **Daylight** | Overall skin tone, texture, visible lesions |
| **True UV** | Sun damage, porphyrins (acne bacteria), pigmentation depth |
| **Cross-polarised** | Redness, vascularity, sub-surface pigment, rosacea |
| **Parallel-polarised** | Surface texture, pores, oiliness |
| **Simulated Wood's lamp** | Pigmentation type (epidermal vs dermal) |
| **Fluorescence** | Sebum distribution, comedone mapping |
| **3D Surface** | Wrinkle depth, skin texture relief |

### Clinical interpretation notes
- **Cross-polarised** is the primary mode for rosacea severity grading
- **True UV** reveals latent photodamage invisible under daylight — use to counsel sun-protective behaviour
- **Fluorescence** guides PlaDuo/acne treatment mapping
- **Simulated Wood's lamp** differentiates epidermal (brighter response = more treatable) from dermal pigment

---

## Sylton Connect — Platform Details

- **Portal URL:** `connect.sylton.com`
- **API region prefix:** Found in Company > API Keys (e.g., `ap-south-1`)
- **Base API URL:** `https://<region>.api.connect.sylton.com`
- **Swagger / interactive docs:** `https://<region>.api.connect.sylton.com/cloud-lambda/v1/swagger`

---

## Authentication

### Endpoint
```
POST https://<region>.api.connect.sylton.com/auth-lambda/v1/token
```

### Request body (JSON)
```json
{
  "username": "your_portal_username",
  "password": "your_portal_password",
  "apitoken": "your_api_key_from_portal"
}
```

### Finding your API key
1. Log in to `connect.sylton.com`
2. Navigate to **Company > API Keys**
3. The region code is the prefix of the API key (e.g., `ap-south-1_xxxx...`)

### Response
```json
{
  "access_token": "<bearer_token>",
  "token_type": "bearer",
  "refresh_token": "<refresh_token>",
  "expires_in": 3600,
  "refresh_token_expires_in": 86400
}
```

Use `Authorization: Bearer <access_token>` on all subsequent requests.

---

## Patient / Customer Endpoints

### Search for a patient
```
POST https://<region>.api.connect.sylton.com/cloud-lambda/v1/search_customers
```
Body:
```json
{
  "searchTerms": "Jane Smith"
}
```
Returns array of customer records including `accountId`.

### List sessions for a patient
```
GET https://<region>.api.connect.sylton.com/cloud-lambda/v1/customers/{accountId}/sessions
```
Returns all imaging sessions for the patient, ordered by date.

---

## Session URLs

Each session has two views:
- **Overview** (summary/report): URL ends in `/overview`
- **Analysis / edit screen**: Replace `/overview` with `/edit`

---

## Integration with Treatment Plans

### Recommended workflow at Treasury Aesthetics
1. **Before first treatment:** Run full OBSERV 520x baseline — capture all 7 modes
2. **Import session** into patient record via Phorest notes (paste Sylton session URL)
3. **Agent interpretation:** Paste OBSERV findings summary into the chat; agent will incorporate imaging data into the treatment plan
4. **Progress photos:** Re-image at 3-month intervals or after a full treatment course
5. **Comparison:** Use the OBSERV side-by-side comparison tool in the portal to document improvement

### Key findings to relay to the agent
When describing OBSERV results, include:
- Redness score / cross-polarised findings (rosacea grading)
- UV damage severity (mild / moderate / severe)
- Pigmentation type (epidermal / dermal / mixed)
- Sebum/acne bacterial load (fluorescence findings)
- Texture/pore score

---

## Data Export
- Sessions can be exported as **PDF reports** from the patient's session overview page
- PDF reports include all captured modes + auto-generated skin scores
- Export for patient records: download PDF → upload to Phorest patient file

---

*For Swagger/API explorer visit: `https://<region>.api.connect.sylton.com/cloud-lambda/v1/swagger`*
