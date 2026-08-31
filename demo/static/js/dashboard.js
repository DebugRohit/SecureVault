"use strict";

/*
 * =========================================================
 * SecureVault Recruiter Demo — Dashboard
 * =========================================================
 *
 * Presentation and interaction layer for the recruiter demo.
 *
 * The dashboard communicates exclusively with the
 * SecureVault demonstration API.
 *
 * The finalized login page is not modified by this file.
 * =========================================================
 */


/* =========================================================
   API CONFIGURATION
   ========================================================= */

const API_BASE = "/securevault/api";


/* =========================================================
   DOM REFERENCES
   ========================================================= */

const credentialCountElement =
    document.getElementById("credentialCount");

const backupCountElement =
    document.getElementById("backupCount");

const credentialListElement =
    document.getElementById("credentialList");

const activityListElement =
    document.getElementById("activityList");

const refreshVaultButton =
    document.getElementById("refreshVault");

const backupButton =
    document.getElementById("backupButton");

const addCredentialButton =
    document.getElementById("addCredentialButton");

const securityButton =
    document.getElementById("securityButton");

const logoutButton =
    document.getElementById("logoutButton");


/* =========================================================
   APPLICATION STATE
   ========================================================= */

const dashboardState = {
    credentials: [],
    backupAvailable: false,
    loaded: false,
    deleteInProgress: false
};


/* =========================================================
   API HELPER
   ========================================================= */

async function apiRequest(
    endpoint,
    options = {}
) {
    const response = await fetch(
        `${API_BASE}${endpoint}`,
        {
            ...options,

            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            }
        }
    );

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        const error = new Error(
            data?.message ||
            data?.error ||
            `Request failed with status ${response.status}.`
        );

        error.status = response.status;
        error.data = data;

        throw error;
    }

    return data;
}


/* =========================================================
   ACTIVITY LOG
   ========================================================= */

function addActivity(
    title,
    description
) {
    if (!activityListElement) {
        return;
    }

    const item =
        document.createElement("div");

    item.className =
        "activity-item";

    item.innerHTML = `
        <span class="activity-marker"></span>

        <div>
            <strong>
                ${escapeHtml(title)}
            </strong>

            <small>
                ${escapeHtml(description)}
            </small>
        </div>
    `;

    activityListElement.prepend(item);

    const items =
        activityListElement.querySelectorAll(
            ".activity-item"
        );

    if (items.length > 5) {
        items[items.length - 1].remove();
    }
}


/* =========================================================
   HTML ESCAPING
   ========================================================= */

function escapeHtml(value) {
    const text =
        String(value ?? "");

    return text
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* =========================================================
   LOAD VAULT STATUS
   ========================================================= */

async function loadVaultStatus() {
    try {
        const data =
            await apiRequest("/status");

        const count =
            data?.credential_count ??
            data?.credentials_count ??
            data?.count ??
            dashboardState.credentials.length;

        dashboardState.backupAvailable =
            Boolean(
                data?.backup_available ??
                data?.has_backup ??
                false
            );

        if (credentialCountElement) {
            credentialCountElement.textContent =
                String(count);
        }

        if (backupCountElement) {
            backupCountElement.textContent =
                dashboardState.backupAvailable
                    ? "1"
                    : "0";
        }

        dashboardState.loaded = true;

    } catch (error) {
        console.error(
            "Unable to load vault status:",
            error
        );

        if (credentialCountElement) {
            credentialCountElement.textContent = "—";
        }

        if (backupCountElement) {
            backupCountElement.textContent = "—";
        }
    }
}


/* =========================================================
   LOAD CREDENTIALS
   ========================================================= */

async function loadCredentials() {
    if (!credentialListElement) {
        return;
    }

    credentialListElement.innerHTML = `
        <div class="loading-state">
            Loading secure credentials...
        </div>
    `;

    try {
        const data =
            await apiRequest("/credentials");

        const credentials =
            Array.isArray(data)
                ? data
                : (
                    Array.isArray(data?.credentials)
                        ? data.credentials
                        : []
                );

        dashboardState.credentials =
            credentials;

        renderCredentials(
            credentials
        );

        if (credentialCountElement) {
            credentialCountElement.textContent =
                String(credentials.length);
        }

    } catch (error) {
        console.error(
            "Unable to load credentials:",
            error
        );

        if (
            error.status === 401 ||
            error.status === 423
        ) {
            handleLockedSession(
                error.data?.message ||
                "SecureVault session has been locked."
            );

            return;
        }

        credentialListElement.innerHTML = `
            <div class="loading-state">
                Unable to load secure credentials.
            </div>
        `;
    }
}


/* =========================================================
   RENDER CREDENTIALS
   ========================================================= */

function renderCredentials(
    credentials
) {
    if (!credentialListElement) {
        return;
    }

    if (!credentials.length) {
        credentialListElement.innerHTML = `
            <div class="loading-state">
                No credentials are currently stored.
            </div>
        `;

        return;
    }

    credentialListElement.innerHTML =
        credentials
            .map(
                (
                    credential,
                    index
                ) => createCredentialMarkup(
                    credential,
                    index
                )
            )
            .join("");

    attachCredentialActions();
}


/* =========================================================
   CREDENTIAL MARKUP
   ========================================================= */

function createCredentialMarkup(
    credential,
    index
) {
    const id =
        credential?.id ??
        credential?.credential_id ??
        index;

    const service =
        credential?.service ??
        credential?.name ??
        "Unknown Service";

    const username =
        credential?.username ??
        credential?.user ??
        credential?.email ??
        "Protected";

    return `
        <div
            class="credential-item"
            data-credential-id="${escapeHtml(id)}"
        >

            <input
                type="checkbox"
                class="credential-select"
                data-id="${escapeHtml(id)}"
                aria-label="Select ${escapeHtml(service)}"
            >

            <div class="credential-service">
                ${escapeHtml(service)}
            </div>

            <div class="credential-username">
                ${escapeHtml(username)}
            </div>

            <div class="credential-password">
                ••••••••••
            </div>

            <div class="credential-actions">

                <button
                    type="button"
                    class="credential-action"
                    data-action="view"
                    data-id="${escapeHtml(id)}"
                >
                    VIEW
                </button>

            </div>

        </div>
    `;
}


/* =========================================================
   CREDENTIAL ACTIONS
   ========================================================= */

function attachCredentialActions() {
    const buttons =
        document.querySelectorAll(
            ".credential-action"
        );

    buttons.forEach(
        (button) => {
            button.addEventListener(
                "click",
                handleCredentialAction
            );
        }
    );

    const selectors =
        document.querySelectorAll(
            ".credential-select"
        );

    selectors.forEach(
        (selector) => {
            selector.addEventListener(
                "change",
                updateDeleteButtonState
            );
        }
    );

    updateDeleteButtonState();
}


async function handleCredentialAction(
    event
) {
    const button =
        event.currentTarget;

    const credentialId =
        button.dataset.id;

    if (!credentialId) {
        return;
    }

    button.disabled = true;

    try {
        const data =
            await apiRequest(
                `/credentials/${encodeURIComponent(credentialId)}`
            );

        const credential =
            data?.credential ??
            data;

        showCredentialDetails(
            credential
        );

        addActivity(
            "Credential accessed",
            "Protected credential details requested"
        );

    } catch (error) {
        console.error(
            "Unable to access credential:",
            error
        );

        if (
            error.status === 401 ||
            error.status === 423
        ) {
            handleLockedSession(
                error.data?.message ||
                "SecureVault session has been locked."
            );

            return;
        }

        showDashboardMessage(
            error.message
        );

    } finally {
        button.disabled = false;
    }
}


/* =========================================================
   SELECTED CREDENTIALS
   ========================================================= */

function getSelectedCredentialIds() {
    return Array.from(
        document.querySelectorAll(
            ".credential-select:checked"
        )
    )
        .map(
            (selector) =>
                selector.dataset.id
        )
        .filter(
            (id) => Boolean(id)
        );
}


function updateDeleteButtonState() {
    const deleteButton =
        findDeleteCredentialButton();

    if (!deleteButton) {
        return;
    }

    const selectedIds =
        getSelectedCredentialIds();

    deleteButton.disabled =
        selectedIds.length === 0 ||
        dashboardState.deleteInProgress;
}


function findDeleteCredentialButton() {
    const knownButton =
        document.getElementById(
            "deleteCredentialButton"
        );

    if (knownButton) {
        return knownButton;
    }

    const actionButtons =
        document.querySelectorAll(
            ".quick-action"
        );

    for (const button of actionButtons) {
        const text =
            button.textContent
                .trim()
                .toUpperCase();

        if (
            text.includes(
                "DELETE CREDENTIAL"
            )
        ) {
            return button;
        }
    }

    return null;
}


/* =========================================================
   DELETE CREDENTIAL DIALOG
   ========================================================= */

function openDeleteCredentialDialog() {
    const selectedIds =
        getSelectedCredentialIds();

    if (!selectedIds.length) {
        showDashboardMessage(
            "Select at least one credential to delete."
        );

        return;
    }

    const selectedCredentials =
        dashboardState.credentials.filter(
            (credential, index) => {
                const id =
                    String(
                        credential?.id ??
                        credential?.credential_id ??
                        index
                    );

                return selectedIds.includes(id);
            }
        );

    const serviceNames =
        selectedCredentials
            .map(
                (credential) =>
                    credential?.service ??
                    credential?.name ??
                    "Credential"
            );

    const existing =
        document.getElementById(
            "deleteCredentialOverlay"
        );

    if (existing) {
        existing.remove();
    }

    const overlay =
        document.createElement("div");

    overlay.id =
        "deleteCredentialOverlay";

    overlay.className =
        "credential-detail-overlay";

    const credentialCount =
        selectedIds.length;

    const summary =
        serviceNames.length <= 3
            ? serviceNames.join(", ")
            : `${serviceNames
                .slice(0, 3)
                .join(", ")} and ${
                    serviceNames.length - 3
                } more`;

    overlay.innerHTML = `
        <div
            class="credential-detail-card"
            role="dialog"
            aria-modal="true"
            aria-label="Delete credentials"
        >

            <div class="panel-kicker">
                PROTECTED OPERATION
            </div>

            <h2>
                Delete Credential${credentialCount === 1 ? "" : "s"}
            </h2>

            <div class="credential-detail-row">
                <span>
                    SELECTED
                </span>

                <strong>
                    ${credentialCount}
                </strong>
            </div>

            <div class="credential-detail-row">
                <span>
                    SERVICES
                </span>

                <strong>
                    ${escapeHtml(summary)}
                </strong>
            </div>

            <div
                class="delete-password-note"
                style="
                    margin-top: 18px;
                    color: rgba(255, 255, 255, 0.62);
                    font-size: 12px;
                    line-height: 1.5;
                "
            >
                Re-authentication is required before
                permanently deleting the selected credential${credentialCount === 1 ? "" : "s"}.
            </div>

            <label
                class="dialog-field"
                style="display:block; margin-top:18px;"
            >
                <span>
                    DEMO MASTER PASSWORD
                </span>

                <input
                    type="password"
                    id="deletePassword"
                    autocomplete="current-password"
                    placeholder="Enter demo password"
                    required
                >
            </label>

            <div
                id="deletePasswordMessage"
                style="
                    min-height: 20px;
                    margin-top: 10px;
                    color: rgba(255, 255, 255, 0.72);
                    font-size: 11px;
                    line-height: 1.4;
                "
            ></div>

            <div class="dialog-actions">

                <button
                    type="button"
                    class="credential-detail-close"
                    id="cancelDeleteCredential"
                >
                    CANCEL
                </button>

                <button
                    type="button"
                    class="credential-detail-submit"
                    id="confirmDeleteCredential"
                >
                    DELETE
                </button>

            </div>

        </div>
    `;

    document.body.appendChild(
        overlay
    );

    document
        .getElementById(
            "cancelDeleteCredential"
        )
        ?.addEventListener(
            "click",
            () => overlay.remove()
        );

    document
        .getElementById(
            "confirmDeleteCredential"
        )
        ?.addEventListener(
            "click",
            () => handleDeleteCredentials(
                selectedIds,
                overlay
            )
        );

    document
        .getElementById(
            "deletePassword"
        )
        ?.addEventListener(
            "keydown",
            (event) => {
                if (
                    event.key === "Enter"
                ) {
                    event.preventDefault();

                    handleDeleteCredentials(
                        selectedIds,
                        overlay
                    );
                }
            }
        );

    overlay.addEventListener(
        "click",
        (event) => {
            if (
                event.target === overlay
            ) {
                overlay.remove();
            }
        }
    );

    document
        .getElementById(
            "deletePassword"
        )
        ?.focus();
}


/* =========================================================
   DELETE CREDENTIALS
   ========================================================= */

async function handleDeleteCredentials(
    credentialIds,
    overlay
) {
    if (
        dashboardState.deleteInProgress
    ) {
        return;
    }

    const passwordInput =
        document.getElementById(
            "deletePassword"
        );

    const password =
        passwordInput?.value ?? "";

    const messageElement =
        document.getElementById(
            "deletePasswordMessage"
        );

    if (!password) {
        if (messageElement) {
            messageElement.textContent =
                "Demo master password is required.";
        }

        passwordInput?.focus();

        return;
    }

    const confirmButton =
        document.getElementById(
            "confirmDeleteCredential"
        );

    dashboardState.deleteInProgress =
        true;

    if (confirmButton) {
        confirmButton.disabled = true;
        confirmButton.textContent =
            "VERIFYING...";
    }

    try {
        const data =
            await apiRequest(
                "/credentials/delete",
                {
                    method: "POST",

                    body: JSON.stringify({
                        credential_ids:
                            credentialIds,
                        password
                    })
                }
            );

        overlay.remove();

        const deletedIds =
            Array.isArray(
                data?.deleted_ids
            )
                ? data.deleted_ids
                : credentialIds;

        deletedIds.forEach(
            (id) => {
                const selector =
                    document.querySelector(
                        `.credential-select[data-id="${CSS.escape(String(id))}"]`
                    );

                if (selector) {
                    selector.checked = false;
                }
            }
        );

        addActivity(
            "Credential deleted",
            data?.message ||
            "Selected credential removed from protected vault"
        );

        await refreshDashboard();

        showDashboardMessage(
            data?.message ||
            "Credential deleted successfully."
        );

    } catch (error) {
        console.error(
            "Unable to delete credentials:",
            error
        );

        if (
            error.status === 423 ||
            error.data?.locked
        ) {
            if (overlay) {
                overlay.remove();
            }

            handleLockedSession(
                error.data?.message ||
                "SecureVault has been locked."
            );

            return;
        }

        if (
            error.status === 401
        ) {
            const attemptsRemaining =
                error.data?.attempts_remaining;

            if (messageElement) {
                messageElement.textContent =
                    attemptsRemaining === 1
                        ? "Incorrect password. 1 attempt remaining."
                        : "Incorrect demo password.";
            }

            if (confirmButton) {
                confirmButton.disabled = false;
                confirmButton.textContent =
                    "DELETE";
            }

            passwordInput?.select();

            return;
        }

        if (messageElement) {
            messageElement.textContent =
                error.message;
        }

        if (confirmButton) {
            confirmButton.disabled = false;
            confirmButton.textContent =
                "DELETE";
        }

    } finally {
        dashboardState.deleteInProgress =
            false;
    }
}


/* =========================================================
   CREDENTIAL DETAIL PRESENTATION
   ========================================================= */

function showCredentialDetails(
    credential
) {
    const service =
        credential?.service ??
        credential?.name ??
        "Credential";

    const username =
        credential?.username ??
        credential?.user ??
        credential?.email ??
        "Protected";

    const password =
        credential?.password ??
        "Protected";

    const existing =
        document.getElementById(
            "credentialDetailOverlay"
        );

    if (existing) {
        existing.remove();
    }

    const overlay =
        document.createElement("div");

    overlay.id =
        "credentialDetailOverlay";

    overlay.className =
        "credential-detail-overlay";

    overlay.innerHTML = `
        <div
            class="credential-detail-card"
            role="dialog"
            aria-modal="true"
            aria-label="Credential details"
        >

            <div class="panel-kicker">
                PROTECTED CREDENTIAL
            </div>

            <h2>
                ${escapeHtml(service)}
            </h2>

            <div class="credential-detail-row">
                <span>
                    USERNAME
                </span>

                <strong>
                    ${escapeHtml(username)}
                </strong>
            </div>

            <div class="credential-detail-row">
                <span>
                    PASSWORD
                </span>

                <strong
                    class="revealed-password"
                >
                    ${escapeHtml(password)}
                </strong>
            </div>

            <button
                type="button"
                class="credential-detail-close"
                id="closeCredentialDetail"
            >
                CLOSE
            </button>

        </div>
    `;

    document.body.appendChild(
        overlay
    );

    document
        .getElementById(
            "closeCredentialDetail"
        )
        ?.addEventListener(
            "click",
            () => overlay.remove()
        );

    overlay.addEventListener(
        "click",
        (event) => {
            if (
                event.target === overlay
            ) {
                overlay.remove();
            }
        }
    );
}


/* =========================================================
   CREATE BACKUP
   ========================================================= */

async function createBackup() {
    if (!backupButton) {
        return;
    }

    const originalText =
        backupButton.textContent;

    backupButton.disabled = true;

    backupButton.textContent =
        "CREATING...";

    try {
        await apiRequest(
            "/backup",
            {
                method: "POST"
            }
        );

        dashboardState.backupAvailable =
            true;

        if (backupCountElement) {
            backupCountElement.textContent =
                "1";
        }

        addActivity(
            "Encrypted backup created",
            "Secure vault backup completed"
        );

        showDashboardMessage(
            "Encrypted backup created successfully."
        );

    } catch (error) {
        console.error(
            "Backup creation failed:",
            error
        );

        if (
            error.status === 401 ||
            error.status === 423
        ) {
            handleLockedSession(
                error.data?.message ||
                "SecureVault session has been locked."
            );

            return;
        }

        showDashboardMessage(
            error.message
        );

    } finally {
        backupButton.disabled = false;

        backupButton.textContent =
            originalText;
    }
}


/* =========================================================
   ADD CREDENTIAL
   ========================================================= */

function openAddCredentialDialog() {
    const existing =
        document.getElementById(
            "addCredentialOverlay"
        );

    if (existing) {
        existing.remove();
    }

    const overlay =
        document.createElement("div");

    overlay.id =
        "addCredentialOverlay";

    overlay.className =
        "credential-detail-overlay";

    overlay.innerHTML = `
        <div
            class="credential-detail-card"
            role="dialog"
            aria-modal="true"
            aria-label="Add credential"
        >

            <div class="panel-kicker">
                SECURE CREDENTIAL
            </div>

            <h2>
                Add Credential
            </h2>

            <form id="addCredentialForm">

                <label class="dialog-field">
                    <span>
                        SERVICE
                    </span>

                    <input
                        type="text"
                        id="newService"
                        name="service"
                        autocomplete="off"
                        required
                    >
                </label>

                <label class="dialog-field">
                    <span>
                        USERNAME
                    </span>

                    <input
                        type="text"
                        id="newUsername"
                        name="username"
                        autocomplete="off"
                        required
                    >
                </label>

                <label class="dialog-field">
                    <span>
                        PASSWORD
                    </span>

                    <input
                        type="password"
                        id="newPassword"
                        name="password"
                        autocomplete="new-password"
                        required
                    >
                </label>

                <div class="dialog-actions">

                    <button
                        type="button"
                        class="credential-detail-close"
                        id="cancelAddCredential"
                    >
                        CANCEL
                    </button>

                    <button
                        type="submit"
                        class="credential-detail-submit"
                    >
                        SAVE CREDENTIAL
                    </button>

                </div>

            </form>

        </div>
    `;

    document.body.appendChild(
        overlay
    );

    const form =
        document.getElementById(
            "addCredentialForm"
        );

    const cancelButton =
        document.getElementById(
            "cancelAddCredential"
        );

    cancelButton?.addEventListener(
        "click",
        () => overlay.remove()
    );

    overlay.addEventListener(
        "click",
        (event) => {
            if (
                event.target === overlay
            ) {
                overlay.remove();
            }
        }
    );

    form?.addEventListener(
        "submit",
        handleAddCredential
    );

    document
        .getElementById(
            "newService"
        )
        ?.focus();
}


/* =========================================================
   SAVE NEW CREDENTIAL
   ========================================================= */

async function handleAddCredential(
    event
) {
    event.preventDefault();

    const form =
        event.currentTarget;

    const service =
        document
            .getElementById(
                "newService"
            )
            ?.value
            .trim();

    const username =
        document
            .getElementById(
                "newUsername"
            )
            ?.value
            .trim();

    const password =
        document
            .getElementById(
                "newPassword"
            )
            ?.value;

    if (
        !service ||
        !username ||
        !password
    ) {
        showDashboardMessage(
            "Service, username and password are required."
        );

        return;
    }

    const submitButton =
        form.querySelector(
            ".credential-detail-submit"
        );

    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent =
            "SAVING...";
    }

    try {
        const data =
            await apiRequest(
                "/credentials",
                {
                    method: "POST",

                    body: JSON.stringify({
                        service,
                        username,
                        password
                    })
                }
            );

        document
            .getElementById(
                "addCredentialOverlay"
            )
            ?.remove();

        addActivity(
            "Credential added",
            `${service} added to protected vault`
        );

        await refreshDashboard();

        showDashboardMessage(
            data?.message ||
            "Credential added successfully."
        );

    } catch (error) {
        console.error(
            "Unable to add credential:",
            error
        );

        if (
            error.status === 401 ||
            error.status === 423
        ) {
            handleLockedSession(
                error.data?.message ||
                "SecureVault session has been locked."
            );

            return;
        }

        showDashboardMessage(
            error.message
        );

    } finally {
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent =
                "SAVE CREDENTIAL";
        }
    }
}


/* =========================================================
   SECURITY STATUS
   ========================================================= */

async function showSecurityStatus() {
    try {
        const data =
            await apiRequest("/status");

        const credentialCount =
            data?.credential_count ??
            data?.credentials_count ??
            dashboardState.credentials.length;

        const backupAvailable =
            data?.backup_available ??
            data?.has_backup ??
            dashboardState.backupAvailable;

        showSecurityDialog({
            credentialCount,
            backupAvailable
        });

        addActivity(
            "Security status checked",
            "Vault protection state verified"
        );

    } catch (error) {
        console.error(
            "Unable to retrieve security status:",
            error
        );

        if (
            error.status === 401 ||
            error.status === 423
        ) {
            handleLockedSession(
                error.data?.message ||
                "SecureVault session has been locked."
            );

            return;
        }

        showDashboardMessage(
            error.message
        );
    }
}


/* =========================================================
   SECURITY STATUS DIALOG
   ========================================================= */

function showSecurityDialog(
    status
) {
    const existing =
        document.getElementById(
            "securityStatusOverlay"
        );

    if (existing) {
        existing.remove();
    }

    const overlay =
        document.createElement("div");

    overlay.id =
        "securityStatusOverlay";

    overlay.className =
        "credential-detail-overlay";

    const backupText =
        status.backupAvailable
            ? "AVAILABLE"
            : "NOT CREATED";

    overlay.innerHTML = `
        <div
            class="credential-detail-card"
            role="dialog"
            aria-modal="true"
            aria-label="Security status"
        >

            <div class="panel-kicker">
                SECURITY VERIFICATION
            </div>

            <h2>
                Vault Security
            </h2>

            <div class="security-status-list">

                <div class="security-status-row">
                    <span>
                        AUTHENTICATION
                    </span>

                    <strong>
                        VERIFIED
                    </strong>
                </div>

                <div class="security-status-row">
                    <span>
                        ENCRYPTED STORAGE
                    </span>

                    <strong>
                        ACTIVE
                    </strong>
                </div>

                <div class="security-status-row">
                    <span>
                        CREDENTIALS
                    </span>

                    <strong>
                        ${escapeHtml(
                            status.credentialCount
                        )}
                    </strong>
                </div>

                <div class="security-status-row">
                    <span>
                        BACKUP
                    </span>

                    <strong>
                        ${backupText}
                    </strong>
                </div>

            </div>

            <button
                type="button"
                class="credential-detail-close"
                id="closeSecurityStatus"
            >
                CLOSE
            </button>

        </div>
    `;

    document.body.appendChild(
        overlay
    );

    document
        .getElementById(
            "closeSecurityStatus"
        )
        ?.addEventListener(
            "click",
            () => overlay.remove()
        );

    overlay.addEventListener(
        "click",
        (event) => {
            if (
                event.target === overlay
            ) {
                overlay.remove();
            }
        }
    );
}


/* =========================================================
   DASHBOARD MESSAGE
   ========================================================= */

function showDashboardMessage(
    message
) {
    const existing =
        document.getElementById(
            "dashboardToast"
        );

    if (existing) {
        existing.remove();
    }

    const toast =
        document.createElement("div");

    toast.id =
        "dashboardToast";

    toast.className =
        "dashboard-toast";

    toast.textContent =
        message;

    document.body.appendChild(
        toast
    );

    requestAnimationFrame(
        () => {
            toast.classList.add(
                "visible"
            );
        }
    );

    window.setTimeout(
        () => {
            toast.classList.remove(
                "visible"
            );

            window.setTimeout(
                () => toast.remove(),
                250
            );
        },
        3000
    );
}


/* =========================================================
   REFRESH DASHBOARD
   ========================================================= */

async function refreshDashboard() {
    await Promise.all([
        loadCredentials(),
        loadVaultStatus()
    ]);

    updateDeleteButtonState();
}


/* =========================================================
   LOCKED SESSION HANDLER
   ========================================================= */

function handleLockedSession(
    message
) {
    dashboardState.deleteInProgress =
        false;

    document
        .getElementById(
            "deleteCredentialOverlay"
        )
        ?.remove();

    document
        .getElementById(
            "credentialDetailOverlay"
        )
        ?.remove();

    document
        .getElementById(
            "securityStatusOverlay"
        )
        ?.remove();

    document
        .getElementById(
            "addCredentialOverlay"
        )
        ?.remove();

    showDashboardMessage(
        message
    );

    window.setTimeout(
        () => {
            window.location.href =
                "/securevault";
        },
        900
    );
}


/* =========================================================
   LOCK VAULT
   ========================================================= */

async function lockVault() {
    if (!logoutButton) {
        return;
    }

    const originalText =
        logoutButton.textContent;

    logoutButton.disabled = true;

    logoutButton.textContent =
        "LOCKING...";

    try {
        await apiRequest(
            "/logout",
            {
                method: "POST"
            }
        );

        window.location.href =
            "/securevault";

    } catch (error) {
        console.error(
            "Unable to lock vault:",
            error
        );

        showDashboardMessage(
            error.message
        );

        logoutButton.disabled = false;

        logoutButton.textContent =
            originalText;
    }
}


/* =========================================================
   EVENT LISTENERS
   ========================================================= */

refreshVaultButton?.addEventListener(
    "click",
    async () => {
        refreshVaultButton.disabled =
            true;

        const originalText =
            refreshVaultButton.textContent;

        refreshVaultButton.textContent =
            "LOADING...";

        try {
            await refreshDashboard();

            addActivity(
                "Vault refreshed",
                "Protected credential data reloaded"
            );

        } catch (error) {
            console.error(
                "Vault refresh failed:",
                error
            );

            showDashboardMessage(
                error.message
            );

        } finally {
            refreshVaultButton.disabled =
                false;

            refreshVaultButton.textContent =
                originalText;
        }
    }
);


backupButton?.addEventListener(
    "click",
    createBackup
);


addCredentialButton?.addEventListener(
    "click",
    openAddCredentialDialog
);


securityButton?.addEventListener(
    "click",
    showSecurityStatus
);


logoutButton?.addEventListener(
    "click",
    lockVault
);


/* =========================================================
   DELETE BUTTON LISTENER
   ========================================================= */

function attachDeleteButtonListener() {
    const deleteButton =
        findDeleteCredentialButton();

    if (!deleteButton) {
        return;
    }

    deleteButton.addEventListener(
        "click",
        openDeleteCredentialDialog
    );

    updateDeleteButtonState();
}


/* =========================================================
   INITIAL DASHBOARD LOAD
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {
        attachDeleteButtonListener();

        refreshDashboard();
    }
);