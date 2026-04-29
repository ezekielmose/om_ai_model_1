import instaloader


USERNAME = "gen.esis025"
PASSWORD = "GenesisDigital@2025"

L = instaloader.Instaloader()

# Login
L.login(USERNAME, PASSWORD)

# Save session
L.save_session_to_file()

print("✅ Session saved successfully")