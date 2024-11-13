from flask import Flask, redirect, request
import requests

app = Flask(__name__)

# Secret key for session management
app.secret_key = "6312Rosales"

# Discord OAuth2 details (hardcoded for simplicity)
DISCORD_CLIENT_ID = "1248835438362234952"
DISCORD_CLIENT_SECRET = "n1-4lGsvHY0uKLY1zQw4zqBSp4CGiCtg"  # Replace with actual client secret from the Discord Developer Portal
DISCORD_REDIRECT_URI = "http://localhost:5000/callback"
DISCORD_OAUTH_URL = "https://discord.com/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_SCOPE = "identify guilds"
DISCORD_API_BASE = "https://discord.com/api"

# Helper function to exchange code for access token
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

# Helper function to fetch data from Discord API using the access token
def get_discord_user_data(access_token, endpoint):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{DISCORD_API_BASE}/{endpoint}", headers=headers)
    return response.json()

# Route to homepage
@app.route("/")
def index():
    return """
    <h1>Welcome to the Bot Dashboard</h1>
    <a href="/login">Log in with Discord</a>
    """

# Route to initiate login (redirect to Discord OAuth2 page)
@app.route("/login")
def login():
    return redirect(
        f"{DISCORD_OAUTH_URL}?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope={DISCORD_SCOPE}"
    )

# Callback route for Discord OAuth2
@app.route("/callback")
def callback():
    # Retrieve authorization code from query string
    code = request.args.get("code")
    
    # Exchange authorization code for access token
    access_token = get_token(code)
    if not access_token:
        return "Error retrieving access token"

    # Fetch user and guild data
    user_data = get_discord_user_data(access_token, "users/@me")
    guild_data = get_discord_user_data(access_token, "users/@me/guilds")

    # Filter guilds where the user has admin or mod permissions
    mod_guilds = [
        {"name": guild["name"], "id": guild["id"]}
        for guild in guild_data
        if guild["permissions"] & (1 << 3) or guild["permissions"] & (1 << 4)  # Admin or Manage Server
    ]

    # Render response with user and guild information
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
