# SecureVault
### Secure Password & Credential Management System

SecureVault is a Python-based credential management application focused on authentication, Fernet encryption, protected vault storage, password security, encrypted backup and restore, and controlled destructive operations.

The project contains two environments:

- **Core SecureVault** — the primary Python/CLI application.
- **Recruiter Demonstration** — an isolated Flask web application for interactive browser-based evaluation.

The demonstration uses controlled sample data and does not connect to real production credentials or external services.

---
## Project Highlights

- Master-password authentication
- Protected vault access
- Fernet-based encryption
- Encrypted credential storage
- Add, view, reveal, edit and delete credentials
- Multi-credential selection and deletion in the web demo
- Password generation
- Password-strength analysis and feedback
- Encrypted backup and restore
- Password re-authentication before destructive deletion
- Two failed deletion-password attempts lock the demo session
- Flask API and interactive dashboard
- Automated regression testing
- Sensitive runtime artifacts excluded from Git

---
## Core Features
### Authentication

SecureVault provides:

- Master-password setup and verification
- Protected vault access
- Authentication failure handling
- Explicit vault locking
- Session-based authentication in the web demonstration
### Credential Management

The core application supports:

- Adding credentials
- Viewing credential information
- Revealing protected passwords
- Editing credentials
- Deleting credentials

The recruiter demonstration additionally supports:

- Selecting one or more credentials
- Deleting selected credentials
- Re-authentication before deletion
### Password Security

SecureVault includes:

- Secure password generation
- Manual password entry
- Password-strength analysis
- Password-strength feedback
### Encryption and Storage

Sensitive vault information is protected using:

- Fernet symmetric encryption
- A dedicated cryptography layer
- Encrypted vault storage
- Protected handling of credential data
### Backup and Recovery

The project includes:

- Encrypted vault backup
- Backup snapshot creation
- Backup validation
- Restore functionality
- Protection around replacing the active vault

---
## Recruiter Demonstration

The isolated Flask demonstration provides a browser-based way to evaluate the project without requiring real credentials.

The demonstration includes:

1. SecureVault login
2. Demo authentication
3. Interactive security dashboard
4. Credential Vault
5. View Credential
6. Add Credential
7. Select one or more credentials
8. Delete Credential
9. Password re-authentication for deletion
10. Two-attempt deletion lockout
11. Create Backup
12. Security Status
13. Lock Vault / logout

The demonstration is separated from the core application so the underlying functionality remains independently testable.
### Demonstration Data

The demo starts with controlled sample credentials representing:

- GitHub
- AWS Console
- PostgreSQL
- Jira

Additional demonstration credentials can be added during a session.

**Do not enter real passwords, API keys, cloud credentials, database credentials, or corporate credentials into the demonstration.**

---
## Demonstration Security Control

Credential deletion is treated as a sensitive operation.

When a credential is selected for deletion:

1. The user selects one or more credentials.
2. The deletion operation is requested.
3. The demo password must be entered again.
4. A correct password allows the deletion.
5. An incorrect password consumes an attempt.
6. After two incorrect attempts, the demonstration session is cleared and the vault is locked.
7. The user must authenticate again.

The lockout behavior is enforced by the application backend and is not dependent only on frontend JavaScript.

---
## Technology Stack

### Core
- **Language:** Python 3.13
- **Core Application:** Python
- **Encryption:** Fernet / cryptography

### Web Demonstration
- **Backend:** Flask 3.1.2
- **Frontend:** HTML5, CSS3, JavaScript

### Quality and Tooling
- **Testing:** pytest
- **Formatting:** Black
- **Linting:** Flake8
- **Import Sorting:** isort
- **Type Checking:** mypy
- **Version Control:** Git
- **Development:** VS Code / Python virtual environment

---
## Project Structure

The repository is organized into separate areas for the core application, the isolated Flask demonstration, automated tests, runtime data, logs, and project configuration.

---
## Application Architecture
The project is organized into focused layers:

- **Authentication** — master-password configuration, verification and access control.
- **Cryptography** — encryption-key handling and credential encryption/decryption.
- **Models** — credential and vault data representations.
- **Services** — credential, vault, backup and restore operations.
- **Utilities** — shared helpers and logging.
- **Demo** — isolated Flask interface, API routes and controlled demonstration data.

This separation keeps the core application independently testable while allowing the Flask demonstration to provide a richer evaluation experience.

---
## Security Design

SecureVault uses multiple security controls rather than relying on encryption alone.
### Authentication

Protected vault operations require successful authentication.
### Encryption

Sensitive vault information is protected using Fernet symmetric encryption.
### Protected Storage

Credentials are designed to remain encrypted rather than being maintained as ordinary plaintext vault data.
### Destructive Operation Protection

Credential deletion in the demonstration requires password re-authentication.
### Failed Attempt Protection

Two failed deletion-password attempts lock the demonstration session.
### Runtime Secret Protection

Sensitive runtime artifacts are excluded from source control, including:

```text
secret.key
master.hash
vault.json
__pycache__/
*.pyc
```

The repository does not track these runtime artifacts.
### Backup Protection

Backup creation and restoration operate through the protected vault workflow.

---
## Installation
### Requirements

Recommended development environment:

- Windows 11
- Python 3.13+
- Git
- VS Code
### 1. Create the Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

Verify Python:

```powershell
python --version
```
### 2. Install Dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

Expected dependency result:

```text
No broken requirements found.
```

---
## Running SecureVault
### Core Application

Run the primary SecureVault CLI:

```powershell
python -m src.main
```

The CLI provides the core credential-management workflow.
### Recruiter Demonstration

Run the isolated Flask demonstration:

```powershell
python -m demo.app
```

Then open the local address displayed by the application.

---
## Demo Access

The recruiter demonstration uses a dedicated demonstration password configured for the isolated local demo environment.

Do not use real production credentials or reuse personal passwords in the demonstration.

> **Important:** The demo environment is intentionally separate from real SecureVault runtime credentials and should only be used with controlled demonstration data.

---
## Recruiter Evaluation

A technical reviewer can evaluate the project by following this sequence:

1. Start the Flask demonstration.
2. Authenticate through the SecureVault login page.
3. Review the security dashboard.
4. View an existing credential.
5. Add a new demonstration credential.
6. Select one or more credentials.
7. Attempt a protected deletion.
8. Re-authenticate for the destructive operation.
9. Create a backup.
10. Review Security Status.
11. Lock the vault.
12. Authenticate again if further evaluation is required.

This demonstrates authentication, credential management, encryption-focused storage, protected destructive operations, backup functionality and session management.

---
## Testing

SecureVault includes an automated regression test suite.

Current validated result:

**96 tests passed**

Run the complete test suite:

```powershell
python -m pytest -q
```

Expected result:

```text
96 passed
```

The test suite is intended to provide regression coverage for the existing application behavior.

---
## Additional Validation
### Dependency Validation

```powershell
python -m pip check
```
### Python Compilation

```powershell
python -m compileall src demo
```
### Git Whitespace Validation

```powershell
git diff --check
```

These checks complement the automated test suite by validating dependencies, Python compilation and repository hygiene.

---
## Security Verification
### Authentication Engine

```powershell
python -c "from demo.demo_security import authenticate_demo_user; assert authenticate_demo_user('DebugRohit@1995') is True; assert authenticate_demo_user('WrongPassword') is False; print('Authentication security: PASS')"
```

The command verifies both successful and failed demo authentication.
### Demo Vault Integrity

```powershell
python -c "from demo.demo_vault import DemoVault; from demo.demo_data import get_initial_credentials; v=DemoVault(get_initial_credentials()); assert v.credential_count == 4; assert len(v.create_backup()) == 4; print('Demo vault integrity: PASS')"
```

This verifies the default demonstration dataset and backup snapshot behavior.
### Sensitive-File Check

```powershell
git ls-files | Select-String -Pattern "secret\.key|master\.hash|vault\.json"
```

The command should produce no output.

---
## Git and Repository Hygiene

Before committing changes:

```powershell
git status
git diff --check
```

Review staged files:

```powershell
git diff --cached --name-only
```

Verify that sensitive runtime artifacts are not staged:

```powershell
git diff --cached --name-only | Select-String -Pattern "secret\.key|master\.hash|vault\.json|__pycache__|\.pyc$"
```

The sensitive-file check should produce no output.

---
## Current Project Status

SecureVault currently provides:

- Master-password authentication
- Password verification
- Protected vault access
- Fernet encryption
- Encrypted credential storage
- Credential creation
- Credential viewing
- Credential reveal
- Credential editing
- Credential deletion
- Multi-credential selection in the demo
- Protected credential deletion
- Deletion re-authentication
- Two-attempt deletion lockout in the demo
- Password generation
- Password-strength analysis
- Encrypted backup
- Backup restore
- Backup validation
- Flask recruiter demonstration
- Interactive login
- Interactive dashboard
- Security status
- Vault locking/logout
- Controlled demonstration data
- Automated regression testing
- Repository security checks

---
## Engineering Focus

SecureVault demonstrates practical engineering across:

- Python development
- Authentication
- Cryptography
- Secure storage
- Credential management
- Password security
- Backup and recovery
- API development
- Flask
- HTML/CSS/JavaScript
- Automated testing
- Git and repository hygiene

The project focuses on functionality that can be implemented, tested, demonstrated and validated rather than relying on unverifiable security claims.

---
## Future Improvements

Potential extensions include:

- Role-based access control
- Multi-user vaults
- Credential sharing
- Password expiration and rotation
- Persistent audit logging
- Advanced security analytics
- Hardware-backed key protection
- Secure synchronization
- Containerized deployment
- CI/CD security gates
- Expanded API documentation
- Independent security assessment

These capabilities are outside the current project scope.

---
## Disclaimer

SecureVault is a portfolio and educational project demonstrating secure application-development concepts.

It should not be considered a production-ready password manager without additional security architecture review, threat modeling, infrastructure hardening, production-grade key management, independent security testing, monitoring, auditing and operational security controls.

The recruiter demonstration is intended for controlled local evaluation and uses demonstration data.

---
## Integrated by:

### Rohit Pujari

SecureVault demonstrates practical application development with a focus on secure software design, Python development, authentication, cryptography, credential management, backup and recovery, API development, Flask, automated testing and security validation.

---
### Secure credentials. Protected storage. Demonstrable security.