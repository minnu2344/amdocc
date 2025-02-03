export function getSelectedText() {
    return window.getSelection()?.toString() || "";
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "getSelectedText") {
        sendResponse({ text: getSelectedText() });
    }
});
