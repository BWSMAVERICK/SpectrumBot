import discord, json, requests, pymysql.cursors
from discord.ext import commands
from utils import rpc_module, mysql_module, parsing
import math

rpc = rpc_module.Rpc()
mysql = mysql_module.Mysql()


class Withdraw:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def withdraw(self, ctx, address: str, amount: float):
        """Withdraw coins from your account to any Bitcoin with Spectrum address"""
        snowflake = ctx.message.author.id    
        if amount <= 24.99:
            await self.bot.say("{} **:warning: Minimum withdrawal amount is 25 BWS :warning:**".format(ctx.message.author.mention))
            return

        abs_amount = abs(amount)
        if math.log10(abs_amount) > 8:
            await self.bot.say(":warning: **Invalid amount!** :warning:")
            return

        mysql.check_for_user(snowflake)

        conf = rpc.validateaddress(address)
        if not conf["isvalid"]:
            await self.bot.say("{} **:warning: Invalid address! :warning:**".format(ctx.message.author.mention))
            return

        ownedByBot = False
        for address_info in rpc.listreceivedbyaddess(0, True):
            if address_info["address"] == address:
                ownedByBot = True
                break

        if ownedByBot:
            await self.bot.say("{} **:warning: You cannot withdraw to an address owned by this bot! :warning:** Please use tip instead!".format(ctx.message.author.mention))
            return

        balance = mysql.get_balance(snowflake, check_update=True)
        if float(balance) < amount:
            await self.bot.say("{} **:warning: You cannot withdraw more money than you have! :warning:**".format(ctx.message.author.mention))
            return

        txid = mysql.create_withdrawal(snowflake, address, amount)
        if txid is None:
            await self.bot.say("{} your withdraw failed despite having the necessary balance! Please contact the bot owner".format(ctx.message.author.mention))
        else:
            await self.bot.say("{} **Withdrew {} BWS! <:blueore:424722137190760448>**{}.htm".format(ctx.message.author.mention, str(amount), txid))

def setup(bot):
    bot.add_cog(Withdraw(bot))
