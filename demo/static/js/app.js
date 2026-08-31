"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const passwordInput = document.getElementById("demoPassword");
    const unlockButton = document.getElementById("unlockButton");
    const togglePassword = document.getElementById("togglePassword");
    const fillDemoPassword = document.getElementById("fillDemoPassword");
    const loginMessage = document.getElementById("loginMessage");

    if (!passwordInput || !unlockButton) {
        return;
    }

    const setMessage = (message, isError = true) => {
        loginMessage.textContent = message;
        loginMessage.style.color = isError
            ? "rgba(255, 119, 119, 0.95)"
            : "rgba(115, 229, 165, 0.95)";
    };

    togglePassword?.addEventListener("click", () => {
        const showingPassword =
            passwordInput.type === "text";

        passwordInput.type = showingPassword
            ? "password"
            : "text";

        togglePassword.textContent = showingPassword
            ? "SHOW"
            : "HIDE";
    });

    fillDemoPassword?.addEventListener("click", () => {
        passwordInput.value = "DebugRohit@1995";
        passwordInput.focus();

        setMessage(
            "Demo credentials loaded. Click Unlock.",
            false
        );
    });

    const unlock = async () => {
        const password = passwordInput.value;

        if (!password) {
            setMessage("Enter the demo master password.");
            passwordInput.focus();
            return;
        }

        unlockButton.disabled = true;
        unlockButton.querySelector("span").textContent =
            "AUTHENTICATING...";

        setMessage("");

        try {
            const response = await fetch(
                "/securevault/api/login",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        password,
                    }),
                }
            );

            const data = await response.json();

            if (!response.ok || !data.success) {
                setMessage(
                    "Authentication failed. Please try again."
                );

                return;
            }

            unlockButton.querySelector("span").textContent =
                "VAULT UNLOCKED";

            setMessage(
                "Authentication successful. Opening SecureVault...",
                false
            );

            window.setTimeout(() => {
                window.location.href = "/securevault";
            }, 500);
        } catch (error) {
            setMessage(
                "Unable to reach the SecureVault demo service."
            );
        } finally {
            unlockButton.disabled = false;

            if (
                unlockButton.querySelector("span").textContent ===
                "AUTHENTICATING..."
            ) {
                unlockButton.querySelector("span").textContent =
                    "UNLOCK SECUREVAULT";
            }
        }
    };

    unlockButton.addEventListener("click", unlock);

    passwordInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            unlock();
        }
    });
});