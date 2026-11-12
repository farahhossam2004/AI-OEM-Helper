
const messageInput = document.getElementById("vehicle-message");
const searchButton = document.getElementById("search-button");
const buttonText = document.getElementById("button-text");

const resultSection = document.getElementById("result-section");
const resultStatus = document.getElementById("result-status");
const resultMessage = document.getElementById("result-message");
const partsList = document.getElementById("parts-list");

searchButton.addEventListener("click", searchCatalog);

messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        searchCatalog();
    }
});

async function searchCatalog() {
    const message = messageInput.value.trim();

    if (!message) {
        messageInput.focus();
        return;
    }

    setLoading(true);
    resultSection.classList.remove("hidden");
    resultStatus.textContent = "SEARCHING...";
    resultMessage.textContent = "Processing your request...";
    partsList.replaceChildren();

    try {
        const response = await fetch("/api/v1/lookup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "The request could not be processed."
            );
        }

        resultStatus.textContent = data.status.toUpperCase();
        resultMessage.textContent = data.response;

        const parts = data.catalog_result?.parts || [];

        parts.forEach((part) => {
            const card = document.createElement("div");
            card.className = "part-card";

            const number = document.createElement("div");
            number.className = "part-number";
            number.textContent = part.oem_number;

            const description = document.createElement("div");
            description.className = "part-description";

            const details = [
                part.description,
                part.manufacturer_name,
                `Verification: ${part.verification_status}`,
            ].filter(Boolean);

            description.textContent = details.join(" · ");

            card.append(number, description);
            partsList.appendChild(card);
        });

    } catch (error) {
        resultStatus.textContent = "ERROR";
        resultMessage.textContent = error.message;
    } finally {
        setLoading(false);
    }
}

function setLoading(isLoading) {
    searchButton.disabled = isLoading;
    buttonText.textContent = isLoading ? "Searching..." : "Search Catalog";
}
