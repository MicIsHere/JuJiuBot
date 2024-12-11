from discord_webhook import DiscordWebhook, DiscordEmbed

webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1236863853837553695/DqHt84ydV1bx_leb5j7WtTf-Yzm-5MDfsB3D5ERZa5f3HCV6Emzu4SEPchbwSIeLkB69", username="JuJiuBot")


def alert_call(title: str, description: str):
    embed = DiscordEmbed(title=title, description=description, color="03b2f8")
    embed.set_footer(text="Powered by 菊酒牛牛")
    embed.set_timestamp()

    webhook.add_embed(embed)
    webhook.execute()