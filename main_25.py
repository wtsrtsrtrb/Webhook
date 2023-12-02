import aiohttp
import discord
import os
import asyncio
from discord.ext import commands
from discord.app_commands import CommandTree
from webserver import keep_alive

secret_bot = os.environ['MTE4MDQ1NjAxNDU1NDg2NTc4NA.GAmzQa.oAHaRcIrQ539hF7R3VBfbmxqg2cE_z_pNSIXlU']

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(command_prefix="-", intents=intents)
tree = CommandTree(client)

async def gen_channels_and_webhooks(guild, num):
    api = "https://discord.com/api/v9"
    header = {"Authorization": f"Bot {byAaAJZTYzDOnoqv7pFVzq1tqqiZkc6_}"}
    hooks = []

    async with aiohttp.ClientSession() as session:
        for category_name, channel_names in [("💸Exotic - Visit💸", ["exotic┊👋 visit"]),
                                            ("💸Exotic - Unverified💸", ["exotic┊😋unverified-nbc", "exotic┊😋unverified-unpremium"]),
                                            ("💸Exotic - Verified💸", ["exotic┊🔒verified-nbc", "exotic┊🔒verified-premium"]),
                                            ("💸Exotic - Success & Failed💸", ["exotic┊✅success", "exotic┊❌failed"])]:
            # Create category
            async with session.post(f'{api}/guilds/{guild.id}/channels', headers=header, json={"name": category_name, "type": 4}) as category_result:
                try:
                    category_id = (await category_result.json())['id']
                except KeyError as e:
                    return f"Failed creating {category_name} category! Error -> {e}"

                # Generate channels within the category
                for channel_name in channel_names:
                    async with session.post(f'{api}/guilds/{guild.id}/channels', headers=header, json={"name": channel_name, "type": 0, "parent_id": category_id}) as channelids:
                        try:
                            channel_id = (await channelids.json())['id']
                        except KeyError as e:
                            return f"Failed generating {channel_name} channel! Error -> {e}"

                        # Generate webhooks
                        async with session.post(f'{api}/channels/{channel_id}/webhooks', headers=header, json={"name": f"Kim Generator"}) as webhook_result:
                            try:
                                webhook_raw = await webhook_result.json()
                                hook_url = f"https://discord.com/api/webhooks/{webhook_raw['id']}/{webhook_raw['token']}"
                                hooks.append((category_name, channel_name, hook_url))
                            except KeyError as e:
                                return f"Failed generating {channel_name} webhook! Error -> {e}"

    return hooks

async def delete_channels_except_general(guild):
    # Find the "general" category
    general_category = discord.utils.get(guild.channels, name="general", type=discord.ChannelType.category)

    # Delete all channels and categories except "general"
    for channel in guild.channels:
        if channel.category != general_category or channel.name != "general":
            await channel.delete()

    for category in guild.categories:
        if category != general_category:
            await category.delete()

@client.event
async def on_ready():
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    print(f"We have logged in as {client.user.name}")
    print("Logged in")
    print("------")

@tree.command(name="gen", description="Generates channels and webhooks")
async def gen_channels_command(int: discord.Interaction):
    try:
        await int.response.defer()
        hooks = await asyncio.create_task(gen_channels_and_webhooks(int.guild, 1))

        embed = discord.Embed(title="Successfully Generated Channel And Webhooks", colour=discord.Colour.green())

        for category_name, channel_name, hook_url in hooks:
            category = discord.utils.get(int.guild.channels, name=category_name, type=discord.ChannelType.category)
            channel = discord.utils.get(int.guild.channels, name=channel_name, type=discord.ChannelType.text, category=category)

            if category and channel:
                embed.add_field(name=f"{category.mention} - {channel.mention}", value=f"Webhook: {hook_url}", inline=False)

        await int.followup.send(embed=embed)
    except KeyError as e:
        await int.followup.send(content=f"Error -> {e}")

@tree.command(name="delete_channels_except_general", description="Deletes all channels and categories except 'general'")
async def delete_channels_except_general_command(int: discord.Interaction):
    try:
        await int.response.defer()
        await delete_channels_except_general(int.guild)
        await int.followup.send("Successfully deleted all channels and categories except 'general'")
    except Exception as e:
        await int.followup.send(content=f"Error -> {e}")

keep_alive()
client.run(byAaAJZTYzDOnoqv7pFVzq1tqqiZkc6_)
