import { defineConfig } from "vite";
import { crx } from "@crxjs/vite-plugin";
import manifest from "./src/manifest.json";
import { resolve } from "path";

export default defineConfig({
    plugins: [crx({ manifest })],
    build: {
        rollupOptions: {
            input: {
                popup: resolve(__dirname, "src/popup.html"),
                background: resolve(__dirname, "src/background.ts"),
                content: resolve(__dirname, "src/content.ts"),
            },
            external: ["src/styles.css"],
        },
        outDir: "dist",
    },
    resolve: {
        alias: {
            "@": resolve(__dirname, "src"),
        },
    },
});
