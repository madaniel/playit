#!/usr/bin/env python3
import http.server
import socketserver
import subprocess
import json
import os
import sys

PORT = 8080

class PlayitHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Fetch tunnel info
            tunnel_info = self.get_tunnel_info()
            html = self.generate_html(tunnel_info)
            self.wfile.write(html.encode())
        else:
            self.send_error(404)

    def get_tunnel_info(self):
        secret_key = os.environ.get("SECRET_KEY")
        if not secret_key:
            return {"error": "SECRET_KEY not found in environment"}

        try:
            # Run playit tunnels list
            # We use the secret key to query the running agent or API
            # Note: playit CLI might need the agent to be running
            cmd = ["playit", "--secret", secret_key, "tunnels", "list"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"error": f"Failed to fetch tunnels: {result.stderr}"}
            
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"error": f"Invalid JSON output: {result.stdout}"}
                
        except Exception as e:
            return {"error": str(e)}

    def generate_html(self, data):
        content = ""
        
        if "error" in data:
            content = f"""
            <div class="card error">
                <h2>Error Fetching Status</h2>
                <p>{data['error']}</p>
            </div>
            """
        elif not data.get("tunnels"):
            content = """
            <div class="card warning">
                <h2>No Tunnels Found</h2>
                <p>The agent is running but no tunnels are active yet.</p>
            </div>
            """
        else:
            for tunnel in data["tunnels"]:
                if not tunnel.get("active"):
                    continue
                    
                alloc = tunnel.get("alloc", {}).get("data", {})
                name = tunnel.get("name", "Unknown Tunnel")
                domain = alloc.get("assigned_domain", "N/A")
                ip = alloc.get("tunnel_ip", "N/A")
                port = alloc.get("port_start", "N/A")
                tunnel_type = tunnel.get("tunnel_type", "Unknown")
                
                content += f"""
                <div class="card">
                    <div class="status-badge">Active</div>
                    <h2>{name}</h2>
                    <div class="detail-row">
                        <span class="label">Domain</span>
                        <span class="value copyable">{domain}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Direct IP</span>
                        <span class="value copyable">{ip}:{port}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Type</span>
                        <span class="value">{tunnel_type}</span>
                    </div>
                </div>
                """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Playit Status</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    background-color: #f0f2f5;
                    margin: 0;
                    padding: 20px;
                    display: flex;
                    justify_content: center;
                    align_items: center;
                    min-height: 100vh;
                }}
                .container {{
                    width: 100%;
                    max_width: 600px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #1a1a1a;
                    margin: 0;
                }}
                .card {{
                    background: white;
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                    position: relative;
                }}
                .card.error {{ border-left: 5px solid #dc3545; }}
                .card.warning {{ border-left: 5px solid #ffc107; }}
                
                .status-badge {{
                    position: absolute;
                    top: 24px;
                    right: 24px;
                    background: #d4edda;
                    color: #155724;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 0.85em;
                    font-weight: 600;
                }}
                
                h2 {{
                    margin-top: 0;
                    color: #333;
                    font-size: 1.25em;
                }}
                
                .detail-row {{
                    display: flex;
                    justify_content: space-between;
                    align_items: center;
                    padding: 12px 0;
                    border-bottom: 1px solid #eee;
                    gap: 20px;
                }}
                .detail-row:last-child {{ border-bottom: none; }}
                
                .label {{ color: #666; }}
                .value {{ 
                    font-weight: 500; 
                    color: #1a1a1a;
                    font-family: monospace;
                    font-size: 1.1em;
                }}
                
                .copyable {{ cursor: pointer; }}
                .copyable:active {{ color: #0056b3; }}
                
                .footer {{
                    text-align: center;
                    color: #888;
                    font-size: 0.85em;
                    margin-top: 40px;
                }}
            </style>
            <script>
                // Auto-refresh every 30 seconds
                setTimeout(function() {{
                    location.reload();
                }}, 30000);
            </script>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Playit Status</h1>
                </div>
                {content}
                <div class="footer">
                    Auto-refreshing every 30s
                </div>
            </div>
        </body>
        </html>
        """

if __name__ == "__main__":
    # Ensure we are in the right directory or just run
    print(f"Starting web server on port {PORT}...", file=sys.stderr)
    with socketserver.TCPServer(("", PORT), PlayitHandler) as httpd:
        httpd.serve_forever()
