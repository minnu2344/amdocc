// (background.ts file you use TypeScript)
chrome.runtime.onInstalled.addListener(() => {
    console.log("Extension installed!");
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "submitText") {
        submitText(message.text)
            .then((response) => sendResponse(response))
            .catch((error) => sendResponse({ error: error.message }));
        return true; // Required for async response
    }
});

async function submitText(text: string) {
    try {
        const response = await fetch(
            "http://localhost:8000/api/v1/classify-text",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text }),
            }
        );
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error submitting text:", error);
        throw error;
    }
}
