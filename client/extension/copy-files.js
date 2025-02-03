const fs = require("fs");
const path = require("path");

// Ensure dist directory exists
if (!fs.existsSync("dist")) {
    fs.mkdirSync("dist");
}

// Copy CSS file
fs.copyFileSync(
    path.join(__dirname, "src/styles_extension.css"),
    path.join(__dirname, "dist/styles_extension.css")
);
