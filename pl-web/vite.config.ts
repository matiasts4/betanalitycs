import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";
import { execFile } from "child_process";

// Helper to run Python bridge script
function runPythonBridge(action: string, payload: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const isWindows = process.platform === "win32";
    const venvPath = isWindows
        ? "../archive/pl-predictor/venv/Scripts/python.exe"
        : "../archive/pl-predictor/.venv/bin/python";
    const pythonPath = path.resolve(__dirname, venvPath);
    const scriptPath = path.resolve(__dirname, "./src/lib/bridge.py");
    
    execFile(pythonPath, [scriptPath, action, JSON.stringify(payload)], {
      env: { ...process.env, PYTHONPATH: "", PYTHONHOME: "" },
    }, (error, stdout, stderr) => {
      if (error) {
        console.error(`[Bridge Error] action=${action}:`, stderr || error.message);
        reject(error);
      } else {
        try {
          resolve(JSON.parse(stdout));
        } catch (e) {
          console.error(`[Bridge JSON Parse Error] action=${action}:`, stdout);
          reject(e);
        }
      }
    });
  });
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    hmr: {
      overlay: false,
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      }
    }
  },
  preview: {
    host: "::",
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      }
    }
  },
  plugins: [
    react(), 
    mode === "development" && componentTagger(),
    {
      name: "python-bridge-middleware",
      configureServer(server) {
        server.middlewares.use(async (req, res, next) => {
          if (req.url && req.url.startsWith("/api/")) {
            const url = new URL(req.url, `http://${req.headers.host}`);
            const pathname = url.pathname;
            
            if (pathname === "/api/predict" && req.method === "POST") {
              let body = "";
              req.on("data", chunk => { body += chunk; });
              req.on("end", async () => {
                try {
                  const payload = JSON.parse(body);
                  const result = await runPythonBridge("predict", payload);
                  res.writeHead(200, { "Content-Type": "application/json" });
                  res.end(JSON.stringify(result));
                } catch (err) {
                  res.writeHead(500, { "Content-Type": "application/json" });
                  res.end(JSON.stringify({ error: err.message }));
                }
              });
              return;
            }
            
            if (pathname === "/api/simulate" && req.method === "POST") {
              let body = "";
              req.on("data", chunk => { body += chunk; });
              req.on("end", async () => {
                try {
                  const payload = JSON.parse(body);
                  const result = await runPythonBridge("simulate", payload);
                  res.writeHead(200, { "Content-Type": "application/json" });
                  res.end(JSON.stringify(result));
                } catch (err) {
                  res.writeHead(500, { "Content-Type": "application/json" });
                  res.end(JSON.stringify({ error: err.message }));
                }
              });
              return;
            }
            
            if (pathname === "/api/performance" && req.method === "GET") {
              try {
                const result = await runPythonBridge("performance", {});
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end(JSON.stringify(result));
              } catch (err) {
                res.writeHead(500, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ error: err.message }));
              }
              return;
            }
            
            if (pathname === "/api/detailed-history" && req.method === "GET") {
              try {
                const n = url.searchParams.get("n") || "100";
                const result = await runPythonBridge("detailed-history", { n: parseInt(n) });
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end(JSON.stringify(result));
              } catch (err) {
                res.writeHead(500, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ error: err.message }));
              }
              return;
            }

            if (pathname === "/api/seasons" && req.method === "GET") {
              try {
                const result = await runPythonBridge("seasons", {});
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end(JSON.stringify(result));
              } catch (err) {
                res.writeHead(500, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ error: err.message }));
              }
              return;
            }

            if (pathname === "/api/history" && req.method === "GET") {
              try {
                const n = url.searchParams.get("n") || "50";
                const season = url.searchParams.get("season") || "all";
                const result = await runPythonBridge("history", { n: parseInt(n), season });
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end(JSON.stringify(result));
              } catch (err) {
                res.writeHead(500, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ error: err.message }));
              }
              return;
            }

            if (pathname === "/api/stats" && req.method === "GET") {
              try {
                const result = await runPythonBridge("stats", {});
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end(JSON.stringify(result));
              } catch (err) {
                res.writeHead(500, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ error: err.message }));
              }
              return;
            }

            if (pathname === "/api/teams" && req.method === "GET") {
              try {
                const season = url.searchParams.get("season") || "all";
                const result = await runPythonBridge("teams", { season });
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end(JSON.stringify(result));
              } catch (err) {
                res.writeHead(500, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ error: err.message }));
              }
              return;
            }

            if (pathname === "/api/teams/list" && req.method === "GET") {
              try {
                const result = await runPythonBridge("teams-list", {});
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end(JSON.stringify(result));
              } catch (err) {
                res.writeHead(500, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ error: err.message }));
              }
              return;
            }

            if (pathname === "/api/matches/recent" && req.method === "GET") {
              try {
                const result = await runPythonBridge("recent-matches", {});
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end(JSON.stringify(result));
              } catch (err) {
                res.writeHead(500, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ error: err.message }));
              }
              return;
            }

            if (pathname === "/api/matches/upcoming" && req.method === "GET") {
              try {
                const result = await runPythonBridge("upcoming", {});
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end(JSON.stringify(result));
              } catch (err) {
                res.writeHead(500, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ error: err.message }));
              }
              return;
            }

            if (pathname === "/api/matches/upcoming/update" && req.method === "POST") {
              try {
                const result = await runPythonBridge("update-upcoming", {});
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end(JSON.stringify(result));
              } catch (err) {
                res.writeHead(500, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ error: err.message }));
              }
              return;
            }

            if (pathname === "/api/assistant/analyze-match" && req.method === "POST") {
              let body = "";
              req.on("data", chunk => { body += chunk; });
              req.on("end", async () => {
                try {
                  const payload = JSON.parse(body);
                  const result = await runPythonBridge("analyze-match", payload);
                  res.writeHead(200, { "Content-Type": "application/json" });
                  res.end(JSON.stringify(result));
                } catch (err) {
                  res.writeHead(500, { "Content-Type": "application/json" });
                  res.end(JSON.stringify({ error: err.message }));
                }
              });
              return;
            }

            if (pathname === "/api/play" && req.method === "POST") {
              let body = "";
              req.on("data", chunk => { body += chunk; });
              req.on("end", async () => {
                try {
                  const payload = JSON.parse(body);
                  const result = await runPythonBridge("play", payload);
                  res.writeHead(200, { "Content-Type": "application/json" });
                  res.end(JSON.stringify(result));
                } catch (err) {
                  res.writeHead(500, { "Content-Type": "application/json" });
                  res.end(JSON.stringify({ error: err.message }));
                }
              });
              return;
            }
          }
          next();
        });
      }
    }
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));

