document
    .getElementById("getSelectedText")
    ?.addEventListener("click", async () => {
        const [tab] = await chrome.tabs.query({
            active: true,
            currentWindow: true,
        });

        if (tab.id) {
            chrome.scripting.executeScript(
                {
                    target: { tabId: tab.id },
                    func: () => {
                        const selection = window.getSelection()?.toString();
                        return selection || "No text selected";
                    },
                },
                (result) => {
                    if (result && result[0]?.result) {
                        (
                            document.getElementById(
                                "selectedText"
                            ) as HTMLTextAreaElement
                        ).value = result[0].result;
                    }
                }
            );
        }
    });

const showLoader = () => {
    const loader = document.getElementById("loaderContainer");
    if (loader) {
        loader.classList.add("active");
    }

    // Disable all buttons while loading
    document.querySelectorAll("button").forEach((button) => {
        button.disabled = true;
    });
};

const hideLoader = () => {
    const loader = document.getElementById("loaderContainer");
    if (loader) {
        loader.classList.remove("active");
    }

    // Re-enable all buttons after loading
    document.querySelectorAll("button").forEach((button) => {
        button.disabled = false;
    });
};

document.getElementById("submitText")?.addEventListener("click", async () => {
    const text = (
        document.getElementById("selectedText") as HTMLTextAreaElement
    ).value;

    if (!text || text === "No text selected") {
        alert("Please select text before submitting.");
        return;
    }

    try {
        showLoader();
        const response = await chrome.runtime.sendMessage({
            action: "submitText",
            text: text,
        });

        if (response.error) {
            alert(`Error: ${response.error}`);
        } else {
            displayResults(response);
        }
    } catch (error) {
        alert("Error submitting text. Please try again.");
    } finally {
        hideLoader();
    }
});

function displayResults(data: {
    original_statements: string[];
    truth_values: (boolean | null)[];
    explanations: string[];
    sources_list: string[][];
}) {
    console.log(data);
    const container = document.getElementById("resultsContainer");
    if (!container) return;

    container.innerHTML = "";
    const paragraph = document.createElement("p");

    data.original_statements.forEach((statement, index) => {
        const span = document.createElement("span");
        span.className = `statement ${
            data.truth_values[index]?.toString() ?? "null"
        }`;
        span.textContent = statement + " ";

        const explanation = document.createElement("span");
        explanation.className = "explanation";
        explanation.textContent = data.explanations[index];

        span.appendChild(explanation);
        paragraph.appendChild(span);
    });

    container.appendChild(paragraph);
}

document.getElementById("clearText")?.addEventListener("click", () => {
    const textArea = document.getElementById(
        "selectedText"
    ) as HTMLTextAreaElement;
    textArea.value = "";
});
