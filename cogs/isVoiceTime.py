from disnake.ext import commands
import sqlite3
import asyncio
import disnake 
import time

from util.db import Data

class isVoiceTime(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cur = Data.getCur()
        self.heshmap = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        server_id = member.guild.id

        cur = Data.getCur()
        try:
            row = None
            
            if before.channel is None and after.channel is not None:
                cur.execute("""SELECT * FROM Users WHERE server_id = ? AND user_id = ?""", (server_id, member.id,))
                row = cur.fetchone()
                if row is None:
                    cur.execute("""INSERT INTO Users (server_id, user_id, voice_activ) VALUES (?, ?, ?)""",
                                (server_id, member.id, 0))
                    Data.commit()
                    cur.execute("""SELECT * FROM Users WHERE server_id = ? AND user_id = ?""", (server_id, member.id,))
                    row = cur.fetchone()

                self.heshmap[member.id] = time.time()

            elif before.channel is not None and after.channel is None:
                if member.id in self.heshmap:
                    start_time = self.heshmap.pop(member.id)
                    end_time = time.time()

                    if row is None:
                        cur.execute("""SELECT * FROM Users WHERE server_id = ? AND user_id = ?""", (server_id, member.id))
                        row = cur.fetchone()

                    if row:
                        voice_time = row[3] + (end_time - start_time)
                        cur.execute("""UPDATE Users SET voice_activ=? WHERE server_id=? AND user_id=?""",
                                    (voice_time, server_id, member.id,))
                        Data.commit()
        finally:
            cur.close()

def setup(bot):
    bot.add_cog(isVoiceTime(bot))
