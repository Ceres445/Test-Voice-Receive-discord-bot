import discord
import os

from discord.ext import commands

from conf import token
from not_copy import args_to_filters, get_encoding


async def finished_callback(sink, channel, *args):
    # Note: sink.audio_data = {user_id: AudioData}
    recorded_users = [f" <@{str(user_id)}> ({os.path.split(audio.file)[1]}) " for user_id, audio in
                      sink.audio_data.items()]
    await channel.send(f"Finished! Recorded audio for {', '.join(recorded_users)}.")


class TestBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=kwargs.pop('commands_prefix', ['+']), *args, **kwargs)
        self.connections = {voice.guild.id: voice for voice in self.voice_clients}
        self.playlists = {}

    async def on_message(self, msg):
        if not msg.content:
            return
        if msg.author.bot:
            return
        await self.process_commands(msg)

    @commands.command()
    async def start_recording(self, ctx, *, args):
        filters = args_to_filters(args)
        if type(filters) == str:
            return await ctx.send(filters)
        encoding = get_encoding(args)
        if encoding is None:
            return await ctx.send("You must provide a valid output encoding.")
        vc = await self.get_vc(ctx.message)
        vc.start_recording(discord.Sink(encoding=encoding, filters=filters), finished_callback, ctx.channel)
        await ctx.send("The recording has started!")

    @commands.command()
    async def stop_recording(self, ctx):
        vc = await self.get_vc(ctx.message)
        vc.stop_recording()
        await ctx.send('stopped recording')

    async def on_voice_state_update(self, member, before, after):
        if member.id != self.user.id:
            return
        # Filter out updates other than when we leave a channel we're connected to
        if member.guild.id not in self.connections and (not before.channel and after.channel):
            return

        print("Disconnected")
        del self.connections[member.guild.id]

    async def get_vc(self, message):
        vc = message.author.voice
        if not vc:
            await message.channel.send("You're not in a vc right now")
            return
        connection = self.connections.get(message.guild.id)
        if connection:
            if connection.channel.id == message.author.voice.channel.id:
                return connection

            await connection.move_to(vc.channel)
            return connection
        else:
            vc = await vc.channel.connect()
            self.connections.update({message.guild.id: vc})
            return vc


client = TestBot()
client.run(token)
