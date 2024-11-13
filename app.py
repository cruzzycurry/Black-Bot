from flask import Flask, redirect, request, session, url_for, jsonify
import requests
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in a production environment

# Discord OAuth2 configuration
DISCORD_CLIENT_ID = "YOUR_DISCORD_CLIENT_ID"
DISCORD_CLIENT_SECRET = "YOUR_DISCORD_CLIENT_SECRET"
DISCORD_REDIRECT_URI = "http://localhost:5000/callback"  # Update with your hosted URL
DISCORD_API_BASE = "https://discord.com/api"
DISCORD_OAUTH_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_SCOPE = "identify guilds"

# Helper function to get access token
def get_token(code):
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "scope": DISCORD_SCOPE
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(DISCORD_TOKEN_URL, data=data, headers=headers)
    return response.json().get("access_token")

# Helper function to get data from Discord API
def get_discord_user_data(access_token, endpoint):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{DISCORD_API_BASE}/{endpoint}", headers=headers)
    return response.json()

# Routes
@app.route("/")
def index():
    return """
    <h1>Welcome to the Bot Dashboard</h1>
    <a href="/login">Log in with Discord</a>
    """

@app.route("/login")
def login():
    # Redirect user to Discord's OAuth2 authorization page
    return redirect(
        f"{DISCORD_OAUTH_URL}?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope={DISCORD_SCOPE}"
    )

@app.route("/callback")
def callback():
    # Retrieve access token
    code = request.args.get("code")
    access_token = get_token(code)

    # Get user and guild data
    user_data = get_discord_user_data(access_token, "users/@me")
    guild_data = get_discord_user_data(access_token, "users/@me/guilds")

    # Filter servers where user is an admin or mod
    mod_guilds = [
        {"name": guild["name"], "id": guild["id"]}
        for guild in guild_data
        if guild["permissions"] & (1 << 3) or guild["permissions"] & (1 << 4)  # Admin or Manage Server
    ]

    # Check if bot is in user's mod servers
    bot_in_guilds = []  # Populate with IDs of guilds where bot is present

    # Render response
    return f"""
    <h1>Welcome, {user_data['username']}#{user_data['discriminator']}!</h1>
    <p>Servers where you have admin/mod permissions:</p>
    <ul>
        {''.join([f'<li>{guild["name"]} (ID: {guild["id"]})</li>' for guild in mod_guilds])}
    </ul>
    """

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
