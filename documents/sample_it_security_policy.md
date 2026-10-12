# Corporate IT Security & Data Protection Policy

## 1. Overview & Purpose
This policy sets forth mandatory security guidelines to safeguard confidential company data, intellectual property, and client information. Compliance is required for all employees, contractors, and partners.

## 2. Authentication & Password Standards
- **Two-Factor Authentication (2FA)**:
  - 2FA is mandatory on all company accounts (Google Workspace, GitHub, AWS, Slack).
  - Hardware security keys (YubiKey) or TOTP authenticator apps (1Password, Google Authenticator) are required. SMS-based 2FA is strictly disallowed.
- **Password Strength**:
  - Minimum 16 characters for corporate accounts.
  - Must be generated and stored inside the company 1Password team vault.
  - Never share credentials via Slack, email, or unencrypted text.

## 3. Device & Workstation Security
- Full-disk encryption (FileVault on macOS, BitLocker on Windows) must remain enabled at all times.
- Automatic screen lock must activate after 5 minutes of inactivity.
- Installing unauthorized torrent clients, pirated software, or unvetted browser extensions is prohibited.
- Lost or stolen devices must be reported to `security@company.com` within 1 hour for remote wiping.

## 4. Remote Work & Network Access
- Public Wi-Fi networks (cafes, airports, hotels) require connecting through the corporate WireGuard VPN before accessing internal servers or production databases.
- Direct SSH access to production environments from personal machines is prohibited; all access must traverse Tailscale / Cloudflare Zero Trust jump hosts with session recording.

## 5. Data Classification & Handling
- **Public**: Marketing content, public open-source repos.
- **Internal**: Standard documents, internal announcements.
- **Confidential**: Financial reports, employee PII, client agreements.
- **Restricted**: API keys, database credentials, cryptographic private keys.
  - Restricted data must never be committed to git repositories or pasted into public AI tools.
