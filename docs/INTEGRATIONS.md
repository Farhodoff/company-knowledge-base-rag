# 🔌 Enterprise Integrations Guide

Connect your **Company Knowledge Base RAG** to team communication channels.

---

## 1. 💬 Slack Bot Integration

The Slack bot uses **Slack Socket Mode** (powered by `slack_bolt`), which works behind enterprise firewalls without exposing public incoming webhooks or IP addresses.

### Setup Steps:
1. Go to [api.slack.com/apps](https://api.slack.com/apps) and click **Create New App** -> **From an app manifest**.
2. Paste the following manifest:
   ```yaml
   display_information:
     name: KnowledgeBot
     description: Grounded internal knowledge assistant
   features:
     bot_user:
       display_name: KnowledgeBot
       always_online: true
   oauth_config:
     scopes:
       bot:
         - app_mentions:read
         - chat:write
         - channels:history
   settings:
     socket_mode_enabled: true
   ```
3. Generate an **App-Level Token** with `connections:write` scope (`xapp-...`).
4. Install the app to your workspace and copy the **Bot User OAuth Token** (`xoxb-...`).
5. Add tokens to `.env`:
   ```ini
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_APP_TOKEN=xapp-your-app-token
   ```
6. Start the Slack bot:
   ```bash
   python src/integrations/slack_bot.py
   ```
7. In any channel, invite `@KnowledgeBot` and ask:
   > `@KnowledgeBot How many vacation days do full-time employees get?`

---

## 2. 🎮 Discord Bot Integration

Allows teams in Discord servers to query internal engineering docs via the `!ask` command.

### Setup Steps:
1. Navigate to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application**, name it **KnowledgeBot**, and go to the **Bot** tab.
3. Enable **Message Content Intent** under Privileged Gateway Intents.
4. Copy the **Bot Token** and add to `.env`:
   ```ini
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   ```
5. Invite the bot to your Discord server via OAuth2 URL Generator (`bot` scope with `Send Messages` and `Embed Links` permissions).
6. Start the Discord bot:
   ```bash
   python src/integrations/discord_bot.py
   ```
7. Test in any text channel:
   ```
   !ask What are our backend coding standards for PR reviews?
   ```

---

## 3. 🌐 Universal REST API / Webhook Server

For custom intranet portals, Zapier, Make, or CI/CD pipelines:

### Start the Server:
```bash
python src/integrations/webhook_server.py --port 8000
```

### Query Endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the policy on 2FA and remote work?"}'
```

**Response:**
```json
{
  "question": "What is the policy on 2FA and remote work?",
  "answer": "Two-Factor Authentication (2FA) is mandatory across all accounts using hardware keys or TOTP apps...",
  "sources": [
    {
      "filename": "sample_it_security_policy.md",
      "page": 1,
      "excerpt": "Two-Factor Authentication (2FA) is mandatory on all company accounts..."
    }
  ]
}
```
