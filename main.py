import random
import asyncio
import json
import os
import discord
from discord import app_commands 
from discord.ext import commands
from pymongo import MongoClient

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ==========================================
# KHO TỪ ĐIỂN TIẾNG VIỆT
# ==========================================
VIETNAMESE_DICTIONARY = set()

def load_dictionary():
    global VIETNAMESE_DICTIONARY
    base_words = [
        "học tập", "tập thể", "thể thao", "ao hồ", "hổ báo", "báo chí", "chỉ số", "số má", 
        "máy bay", "bay lượn", "nước non", "non sông", "sông ngòi", "ngòi bút", "bút mực",
        "mực tàu", "tàu thủy", "thủy tinh", "tinh tú", "túi xách", "xách tay", "tay chân", 
        "chân thành", "thành phố", "phố phường", "phường xã", "xã hội", "hội hè", "hè phố", 
        "thời gian", "gian nan", "nan giải", "giải quyết", "quyết tâm", "tâm sự", "sự nghiệp", 
        "nghiệp dư", "dư dả", "đất nước", "trước sau", "sau cùng", "cùng chung", "chung thủy", 
        "thủy chung", "thiên nhiên", "yêu thương", "thương nhớ", "nhớ mong", "mong mỏi", 
        "mỏi mệt", "mệt mỏi", "bầu trời", "mây gió", "hoa quả", "cây cối", "cối xay", 
        "xay lúa", "lúa gạo", "gạo nếp", "nếp sống", "sống còn", "còn lại", "lại qua", 
        "qua lại", "lời nói", "nói năng", "năng lực", "lực lượng", "lượng từ", "từ ngữ", 
        "ngữ pháp", "pháp luật", "luật sư", "sư phạm", "phạm vi", "vi tính", "tính toán", 
        "toán học", "học sinh", "sinh viên", "viên bi", "bi a", "a dua", "dua nịnh", 
        "nịnh hót", "hót hay", "hay ho", "ho hen", "hen suyễn", "suyễn thở", "thở dài",
        "thời điểm", "điểm số", "số lượng", "lượng mưa", "mưa gió", "gió bão", "bão lũ",
        "lũ lụt", "lụt lội", "lội bùn", "bùn đất", "đất cát", "cát bụi", "bụi đời", "đời sống"
    ]
    
    for w in base_words:
        VIETNAMESE_DICTIONARY.add(w.lower().strip())

    if os.path.exists("tudien.txt"):
        try:
            with open("tudien.txt", "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip().lower()
                    if word:
                        VIETNAMESE_DICTIONARY.add(word)
            print(f"✅ Đã nạp thành công từ điển từ file! Tổng số từ: {len(VIETNAMESE_DICTIONARY)}")
        except Exception as e:
            print(f"⚠️ Không đọc được file tudien.txt: {e}")
    else:
        print(f"📌 Đang dùng từ điển mặc định với {len(VIETNAMESE_DICTIONARY)} từ.")

load_dictionary()

# ==========================================
# QUẢN LÝ KINH TẾ & DATABASE
# ==========================================
MONGO_URI = "mongodb+srv://longbebe2405_db_user:rp8!kdiphTjukf7@cluster0.ahor027.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["discord_bot_db"]

users_collection = db["economy_users"]      
config_collection = db["guild_configs"]     
game_collection = db["word_chain_state"]    

def save_game_state(channel_id, game_data):
    game_collection.update_one(
        {"channel_id": str(channel_id)},
        {"$set": game_data},
        upsert=True
    )

def get_game_state(channel_id):
    return game_collection.find_one({"channel_id": str(channel_id)})

def delete_game_state(channel_id):
    game_collection.delete_one({"channel_id": str(channel_id)})

def get_balance(user_id):
    user_id_str = str(user_id)
    user_data = users_collection.find_one({"user_id": user_id_str})
    if not user_data:
        users_collection.insert_one({"user_id": user_id_str, "balance": 0})
        return 0
    return user_data["balance"]

def update_balance(user_id, amount):
    user_id_str = str(user_id)
    user_data = users_collection.find_one({"user_id": user_id_str})
    
    if not user_data:
        current_bal = 0
    else:
        current_bal = user_data["balance"]
        
    new_bal = current_bal + amount
    if new_bal < 0:
        new_bal = 0
        
    users_collection.update_one(
        {"user_id": user_id_str},
        {"$set": {"balance": new_bal}},
        upsert=True
    )
    return new_bal

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f"✅ Đã đồng bộ thành công {len(synced)} lệnh slash!")
    except Exception as e:
        print(f"⚠️ Lỗi đồng bộ lệnh: {e}")

# ==========================================
# HỆ THỐNG CÀI ĐẶT KÊNH (CHỈ ADMIN)
# ==========================================
@bot.tree.command(name="nsetnoitu", description="Cài đặt kênh riêng để chơi Nối Từ")
@app_commands.checks.has_permissions(administrator=True)
async def nsetnoitu_command(interaction: discord.Interaction, channel: discord.TextChannel):
    config_collection.update_one(
        {"guild_id": str(interaction.guild_id)},
        {"$set": {"noitu_channel": str(channel.id)}},
        upsert=True
    )
    await interaction.response.send_message(f"✅ Đã cài đặt kênh {channel.mention} làm kênh chơi **Nối Từ**!", ephemeral=True)

@bot.tree.command(name="nsettaixiu", description="Cài đặt kênh riêng để chơi Tài Xỉu")
@app_commands.checks.has_permissions(administrator=True)
async def nsettaixiu_command(interaction: discord.Interaction, channel: discord.TextChannel):
    config_collection.update_one(
        {"guild_id": str(interaction.guild_id)},
        {"$set": {"taixiu_channel": str(channel.id)}},
        upsert=True
    )
    await interaction.response.send_message(f"✅ Đã cài đặt kênh {channel.mention} làm kênh chơi **Tài Xỉu**!", ephemeral=True)

# ==========================================
# LỆNH THÊM TỪ MỚI
# ==========================================
@bot.tree.command(name="hthemtu", description="Đóng góp cụm từ mới 2 tiếng vào kho từ điển")
@app_commands.describe(tu="Nhập cụm từ 2 tiếng cần thêm (Ví dụ: thông minh)")
async def hthemtu_command(interaction: discord.Interaction, tu: str):
    clean_tu = tu.strip().lower()
    words = clean_tu.split()
    
    if len(words) != 2:
        await interaction.response.send_message("⚠️ Từ thêm vào phải là cụm **2 tiếng** (Ví dụ: `học tập`)!", ephemeral=True)
        return
        
    formatted_word = f"{words[0]} {words[1]}"
    
    if formatted_word in VIETNAMESE_DICTIONARY:
        await interaction.response.send_message(f"⚠️ Cụm từ **'{formatted_word.upper()}'** đã có sẵn trong từ điển rồi!", ephemeral=True)
        return
        
    VIETNAMESE_DICTIONARY.add(formatted_word)
    
    try:
        with open("dictionary.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{formatted_word}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Lỗi ghi file từ điển: {e}", ephemeral=True)
        return

    await interaction.response.send_message(
        f"✅ **{interaction.user.display_name}** đã đóng góp thành công từ mới: **{formatted_word.upper()}** vào kho từ điển!",
        ephemeral=False
    )

# ==========================================
# LỆNH /HELP XEM HƯỚNG DẪN BOT
# ==========================================
@bot.tree.command(name="help", description="Xem danh sách toàn bộ tính năng và lệnh của bot")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 HỆ THỐNG TRỢ GIÚP - NHÀ CÁI HABIBI",
        description="Dưới đây là toàn bộ danh sách lệnh và trò chơi hiện có:",
        color=discord.Color.purple()
    )
    embed.add_field(
        name="🎮 Trò Chơi & Cày Tiền",
        value="• `/noitu` - Bắt đầu chơi Nối Từ\n"
              "• `/baucua` - Chơi Bầu Cua đổi thưởng\n"
              "• `/taixiu` - Sòng Tài Xỉu hấp dẫn",
        inline=False
    )
    embed.add_field(
        name="⚙️ Cài đặt kênh (Admin)",
        value="• `/nsetnoitu` - Set kênh chơi Nối Từ\n"
              "• `/nsettaixiu` - Set kênh chơi Tài Xỉu",
        inline=False
    )
    embed.add_field(
        name="💰 Tài Chính",
        value="• `/hcash` - Kiểm tra số dư vàng\n",
        inline=False
    )
    embed.set_footer(text="Chúc bro chơi game vui vẻ và không bị ra đảo! 🏝️")
    await interaction.response.send_message(embed=embed)

# ==========================================
# 1. LỆNH VÍ TIỀN (/hcash)
# ==========================================
@bot.tree.command(name="hcash", description="Kiểm tra số dư vàng trong ví của bạn")
async def hcash_command(interaction: discord.Interaction):
    bal = get_balance(interaction.user.id)
    embed = discord.Embed(
        title=f"💰 TÀI KHOẢN VÍ CỦA: {interaction.user.display_name}",
        description=f"🪙 Số dư hiện tại: **{bal:,} gold**\n\n"
                    f"👉 *Cách kiếm tiền:* Chơi Nối Từ (`/noitu`) để cày vốn.\n"
                    f"👉 *Cách giải trí:* Thử vận may tại Sòng Tài Xỉu (`/taixiu`) và Bầu Cua (`/baucua`).",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=False)

# ==========================================
# 2. HỆ THỐNG NỐI TỪ
# ==========================================
class WordGameUI(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="📖 Từ hiện tại", style=discord.ButtonStyle.blurple, custom_id="btn_noitu_info")
    async def info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = get_game_state(self.channel_id)
        if game:
            await interaction.response.send_message(
                f"🔗 **TRẠNG THÁI NỐI TỪ HIỆN TẠI:**\n"
                f"• Cụm từ mới nhất: **{game['last_word'].upper()}**\n"
                f"• Tiếng bắt buộc nối tiếp: **`{game['last_syllable'].upper()}`**\n"
                f"• Tổng số từ đã nối thành công: `{len(game['history'])}` từ",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("⚠️ Ván nối từ này đã kết thúc rồi!", ephemeral=True)

    @discord.ui.button(label="🏳️ Bí quá! Đổi từ mới", style=discord.ButtonStyle.secondary, custom_id="btn_noitu_skip")
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = get_game_state(self.channel_id)
        if not game:
            await interaction.response.send_message("⚠️ Không có ván nối từ nào đang chạy ở đây cả!", ephemeral=True)
            return
        
        random_start = random.choice(list(VIETNAMESE_DICTIONARY))
        words = random_start.split()
        full_word = f"{words[0]} {words[1]}"
        
        game["last_word"] = full_word
        game["last_syllable"] = words[1]
        game["history"].append(full_word)
        game["last_user_id"] = None
        save_game_state(self.channel_id, game)

        await interaction.response.send_message(
            f"🏳️ **{interaction.user.display_name}** tuyên bố đầu hàng vì quá khó!\n"
            f"🔄 Bot đã đổi sang từ khóa mới tinh: **{full_word.upper()}**\n"
            f"👉 Nối tiếp ngay từ: **`{words[1].upper()}`**",
            ephemeral=False
        )

    @discord.ui.button(label="🛑 Kết thúc ván", style=discord.ButtonStyle.red, custom_id="btn_noitu_stop")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = get_game_state(self.channel_id)
        if game:
            delete_game_state(self.channel_id)
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)
            await interaction.response.send_message(f"🛑 **{interaction.user.display_name}** đã dừng ván nối từ!", ephemeral=False)
        else:
            await interaction.response.send_message("⚠️ Không có ván nối từ nào đang chạy ở đây cả!", ephemeral=True)

@bot.tree.command(name="noitu", description="Bắt đầu ván Nối Từ tự động bốc từ khóa khởi đầu")
async def noitu_command(interaction: discord.Interaction):
    # Kiểm tra cấu hình kênh Nối Từ
    config = config_collection.find_one({"guild_id": str(interaction.guild_id)})
    if config and config.get("noitu_channel"):
        required_ch = int(config["noitu_channel"])
        if interaction.channel.id != required_ch:
            await interaction.response.send_message(f"❌ Bạn chỉ được chơi Nối Từ tại kênh <#{required_ch}>!", ephemeral=True)
            return

    channel_id = interaction.channel.id
    random_start = random.choice(list(VIETNAMESE_DICTIONARY))
    words = random_start.split()
    
    full_word = f"{words[0]} {words[1]}"
    game_data = {
        "channel_id": str(channel_id),
        "last_word": full_word,
        "last_syllable": words[1],
        "history": [full_word],
        "last_user_id": None
    }
    save_game_state(channel_id, game_data)

    embed = discord.Embed(
        title="🔗 SÂN CHƠI NỐI TỪ CHUẨN TỪ ĐIỂN 🪙",
        description=f"Bot đã tự động bốc từ khóa khởi động!\nCụm từ gốc: **{full_word.upper()}**\n\n"
                    f"👉 *Luật chơi:* Nhắn trực tiếp cụm **2 tiếng** có nghĩa bắt đầu bằng tiếng: **`{words[1].upper()}`**\n"
                    f"💡 *Bí quá?* Nhấn nút **'🏳️ Bí quá! Đổi từ mới'** bên dưới để đổi ván khác!\n"
                    f"🎁 *Phần thưởng:* Mỗi từ đúng được cộng **2,000 gold** vào ví!",
        color=discord.Color.blue()
    )
    view = WordGameUI(channel_id)
    await interaction.response.send_message(embed=embed, view=view)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    channel_id = message.channel.id
    game = get_game_state(channel_id)
    
    if game:
        content = message.content.strip().lower()
        words = content.split()

        if len(words) == 2:
            user_id = message.author.id
            if user_id == game.get("last_user_id"):
                try:
                    await message.add_reaction("<:sai:1537531074329190540>")
                except Exception:
                    pass
                return

            required_syllable = game["last_syllable"]
            current_first_syllable = words[0]
            full_word = f"{words[0]} {words[1]}"

            if current_first_syllable == required_syllable and full_word not in game["history"]:
                if full_word in VIETNAMESE_DICTIONARY:
                    game["last_user_id"] = user_id
                    game["last_word"] = full_word
                    game["last_syllable"] = words[1]
                    game["history"].append(full_word)
                    
                    save_game_state(channel_id, game)
                    update_balance(user_id, 2000)
                    
                    try:
                        await message.add_reaction("<:tichxanh:1537528859858309191>")
                    except Exception:
                        pass
                else:
                    try:
                        await message.add_reaction("<:sai:1537531074329190540>")
                    except Exception:
                        pass
            else:
                try:
                    await message.add_reaction("<:sai:1537531074329190540>")
                except Exception:
                    pass

    await bot.process_commands(message)

# ==========================================
# LỆNH /HSTOP DỪNG VÁN NỐI TỪ (ĐÃ FIX CHUẨN)
# ==========================================
@bot.tree.command(name="hstop", description="Dừng ván nối từ đang diễn ra tại kênh hiện tại")
async def hstop_command(interaction: discord.Interaction):
    # Phản hồi ngay lập tức để tránh lỗi timeout từ Discord (chuyển sang dạng ẩn hoặc hiện tùy ý)
    await interaction.response.defer(ephemeral=False)

    # Kiểm tra xem kênh này có đang chạy ván nối từ nào không
    game = get_game_state(interaction.channel.id)
    if not game:
        await interaction.followup.send("⚠️ Hiện tại không có ván nối từ nào đang diễn ra ở kênh này cả!", ephemeral=True)
        return

    # Xóa trạng thái game khỏi database
    delete_game_state(interaction.channel.id)

    # Gửi thông báo thành công qua followup
    await interaction.followup.send(f"🛑 **{interaction.user.display_name}** đã dừng ván nối từ tại kênh này!")

# ==========================================
# 3. SÒNG BẦU CUA
# ==========================================
active_baucua_bets = {}
BAU_CUA_ITEMS = {
    "nai": {"name": "Nai", "emoji": "🦌"},
    "bau": {"name": "Bầu", "emoji": "🍐"},
    "ga": {"name": "Gà", "emoji": "🐔"},
    "ca": {"name": "Cá", "emoji": "🐟"},
    "cua": {"name": "Cua", "emoji": "🦀"},
    "tom": {"name": "Tôm", "emoji": "🦐"}
}

class BauCuaModal(discord.ui.Modal):
    def __init__(self, choice_key, choice_name, message_id):
        super().__init__(title=f'Cược Bầu Cua: {choice_name}')
        self.choice_key = choice_key
        self.choice_name = choice_name
        self.message_id = message_id
        self.bet_amount = discord.ui.TextInput(
            label='Nhập số gold muốn cược',
            style=discord.TextStyle.short,
            placeholder='Ví dụ: 10000',
            required=True,
            max_length=7
        )
        self.add_item(self.bet_amount)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            money = int(self.bet_amount.value)
            if money <= 0: raise ValueError
        except ValueError:
            await interaction.response.send_message("⚠️ Số tiền cược không hợp lệ!", ephemeral=True)
            return

        user_id = interaction.user.id
        current_bal = get_balance(user_id)
        if current_bal < money:
            await interaction.response.send_message(f"❌ **Ví không đủ tiền!** Bạn đang có **{current_bal:,} gold**.", ephemeral=True)
            return

        update_balance(user_id, -money)
        if self.message_id not in active_baucua_bets:
            active_baucua_bets[self.message_id] = []
        
        active_baucua_bets[self.message_id].append({
            "user_id": user_id,
            "username": interaction.user.display_name,
            "choice_key": self.choice_key,
            "choice_name": self.choice_name,
            "money": money
        })
        await interaction.response.send_message(f"✅ Đã cược **{money:,} gold** vào **{self.choice_name}**!", ephemeral=True, delete_after=5)

class BauCuaUI(discord.ui.View):
    def __init__(self, message_id):
        super().__init__(timeout=None)
        self.message_id = message_id
        buttons_row1 = [("Nai", "nai", "🦌"), ("Bầu", "bau", "🍐"), ("Gà", "ga", "🐔")]
        for label, key, emoji in buttons_row1:
            btn = discord.ui.Button(label=label, emoji=emoji, style=discord.ButtonStyle.blurple, custom_id=f"bc_{key}", row=0)
            btn.callback = self.make_callback(label, key)
            self.add_item(btn)

        buttons_row2 = [("Cá", "ca", "🐟"), ("Cua", "cua", "🦀"), ("Tôm", "tom", "🦐")]
        for label, key, emoji in buttons_row2:
            btn = discord.ui.Button(label=label, emoji=emoji, style=discord.ButtonStyle.blurple, custom_id=f"bc_{key}", row=1)
            btn.callback = self.make_callback(label, key)
            self.add_item(btn)

    def make_callback(self, choice_name, choice_key):
        async def callback(interaction: discord.Interaction):
            await interaction.response.send_modal(BauCuaModal(choice_key, choice_name, self.message_id))
        return callback

@bot.tree.command(name="baucua", description="Mở sòng Bầu Cua lắc siêu mượt")
async def baucua_command(interaction: discord.Interaction):
    embed = discord.Embed(title="🦌 BẦU CUA HABIBI - NHÀ CÁI ĐỈNH CAO 🍐", description="Chọn cửa đặt cược bên dưới. Đang đếm ngược 30 giây.", color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    
    view = BauCuaUI(msg.id)
    await msg.edit(view=view)

    for t in range(30, 0, -1):
        embed.set_footer(text=f"⏳ Thời gian đặt cược Bầu Cua còn lại: {t} giây...")
        await msg.edit(embed=embed)
        await asyncio.sleep(1)

    for child in view.children: child.disabled = True
    embed.set_footer(text="🔒 Đã khóa sổ! Nhà cái đang lắc bầu cua...")
    await msg.edit(embed=embed, view=view)

    shake_frames = ["🎲 **Nhà cái đang lắc mạnh tay...**\n\n# 🌀 🌀 🌀", "🎲 **Xúc xắc đang xoay vòng...**\n\n# 🦌 🦐 🐟", "🎲 **Chuẩn bị lộ diện...**\n\n# ⚡ ⚡ ⚡"]
    for frame in shake_frames:
        await asyncio.sleep(0.6)
        anim_embed = discord.Embed(title="🎲 ĐANG LẮC BẦU CUA 🎲", description=frame, color=discord.Color.orange())
        await msg.edit(embed=anim_embed)

    keys_list = list(BAU_CUA_ITEMS.keys())
    roll1, roll2, roll3 = random.choice(keys_list), random.choice(keys_list), random.choice(keys_list)
    rolled_results = [roll1, roll2, roll3]

    bets_in_this_game = active_baucua_bets.get(msg.id, [])
    summary_results = []
    if not bets_in_this_game:
        summary_results.append("KHÔNG CÓ AI CƯỢC CẢ!")
    else:
        for bet in bets_in_this_game:
            user_id = bet["user_id"]
            choice_key = bet["choice_key"]
            money = bet["money"]
            match_count = rolled_results.count(choice_key)
            if match_count > 0:
                payout = money + (money * match_count)
                update_balance(user_id, payout)
                summary_results.append(f"<@{user_id}>: **Trúng x{match_count} húp {payout:,} 🪙** 🎉")
            else:
                summary_results.append(f"<@{user_id}>: **Toạch mất sạch** 😭")

    if msg.id in active_baucua_bets: del active_baucua_bets[msg.id]

    res_text = (
        f"### 🏆 KẾT QUẢ MỞ BÁT:\n"
        f"# {BAU_CUA_ITEMS[roll1]['emoji']}  {BAU_CUA_ITEMS[roll2]['emoji']}  {BAU_CUA_ITEMS[roll3]['emoji']}\n"
        f"*( {BAU_CUA_ITEMS[roll1]['name']} - {BAU_CUA_ITEMS[roll2]['name']} - {BAU_CUA_ITEMS[roll3]['name']} )*\n\n"
        f"**📊 TỔNG KẾT GIAO DỊCH:**\n" + "\n".join(summary_results)
    )
    result_embed = discord.Embed(title="🎲 KẾT QUẢ BẦU CUA 🎲", description=res_text, color=discord.Color.gold())
    result_embed.set_footer(text="Ván chơi đã kết thúc.")
    await msg.edit(embed=result_embed, view=None)

# ==========================================
# 4. SÒNG TÀI XỈU
# ==========================================
active_bets = {}

class BetModal(discord.ui.Modal):
    def __init__(self, choice_name, choice_value, message_id):
        super().__init__(title=f'Cược vào: {choice_name}')
        self.choice_value = choice_value
        self.choice_name = choice_name
        self.message_id = message_id
        self.bet_amount = discord.ui.TextInput(
            label='Nhập số gold muốn cược',
            style=discord.TextStyle.short,
            placeholder='Ví dụ: 10000',
            required=True,
            max_length=7
        )
        self.add_item(self.bet_amount)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            money = int(self.bet_amount.value)
            if money <= 0: raise ValueError
        except ValueError:
            await interaction.response.send_message("⚠️ Số tiền cược không hợp lệ!", ephemeral=True)
            return

        user_id = interaction.user.id
        current_bal = get_balance(user_id)
        if current_bal < money:
            await interaction.response.send_message(f"❌ **Ví không đủ tiền!** Bạn đang có **{current_bal:,} gold**.", ephemeral=True)
            return

        update_balance(user_id, -money)
        if self.message_id not in active_bets:
            active_bets[self.message_id] = []
       
        active_bets[self.message_id].append({
            "user_id": user_id,
            "username": interaction.user.display_name,
            "choice_value": self.choice_value,
            "choice_name": self.choice_name,
            "money": money
        })
        await interaction.response.send_message(f"✅ Đã cược **{money:,} gold** vào cửa **{self.choice_name}**!", ephemeral=True)

class TaiXiuUI(discord.ui.View):
    def __init__(self, message_id):
        super().__init__(timeout=None)
        self.message_id = message_id
        main_buttons = [
            ("Xỉu (3-10)", discord.ButtonStyle.green, "xiu"),
            ("Tài (11-18)", discord.ButtonStyle.green, "tai"),
            ("Chẵn", discord.ButtonStyle.red, "chan"),
            ("Lẻ", discord.ButtonStyle.red, "le")
        ]
        for label, style, val in main_buttons:
            btn = discord.ui.Button(label=label, style=style, custom_id=f"btn_{val}", row=0)
            btn.callback = self.make_callback(label, val)
            self.add_item(btn)

        for i in range(3, 19):
            row = ((i - 3) // 5) + 1
            btn = discord.ui.Button(label=f"Số {i}", style=discord.ButtonStyle.blurple, custom_id=f"btn_num_{i}", row=row)
            btn.callback = self.make_callback(f"Số {i}", f"so_{i}")
            self.add_item(btn)

    def make_callback(self, choice_name, choice_value):
        async def callback(interaction: discord.Interaction):
            await interaction.response.send_modal(BetModal(choice_name, choice_value, self.message_id))
        return callback

@bot.tree.command(name="taixiu", description="Mở sòng tài xỉu giao diện VIP, lắc xúc xắc động cực đẹp")
async def taixiu_command(interaction: discord.Interaction):
    # Thêm dòng defer này để chống lỗi 3 giây của Discord khi check database
    await interaction.response.defer(thinking=True)

    # Kiểm tra cấu hình kênh Tài Xỉu
    config = config_collection.find_one({"guild_id": str(interaction.guild_id)})
    if config and config.get("taixiu_channel"):
        required_ch = int(config["taixiu_channel"])
        if interaction.channel.id != required_ch:
            await interaction.followup.send(f"❌ Bạn chỉ được chơi Tài Xỉu tại kênh <#{required_ch}>!", ephemeral=True)
            return

    embed = discord.Embed(
        title="🎲 TÀI XỈU HABIBI - SÒNG BẠC ĐẲNG CẤP 🎲",
        description="🔥 **HƯỚNG DẪN THAM GIA:**\n"
                    "• Chọn cửa cược bên dưới để mở bảng nhập số gold.\n"
                    "• Tỉ lệ thưởng: **Tài/Xỉu/Chẵn/Lẻ (1:1)** | **Số cụ thể (1:10)**.\n"
                    "• Kết quả được niêm phong tuyệt đối và chỉ lộ diện khi hết giờ!\n\n"
                    "⏳ **Trò chơi bắt đầu đếm ngược 30 giây!**",
        color=discord.Color.blurple()
    )
   
    # Dùng followup.send vì đã defer ở trên để lấy message gốc chính xác
    msg = await interaction.followup.send(embed=embed, wait=True)
   
    view = TaiXiuUI(msg.id)
    await msg.edit(view=view)

    for t in range(30, 0, -1):
        embed.set_footer(text=f"⏳ Thời gian đặt cược còn lại: {t} giây...")
        await msg.edit(embed=embed)
        await asyncio.sleep(1)

    for child in view.children:
        child.disabled = True
    embed.set_footer(text="🔒 Đã khóa sổ! Nhà cái đang xóc đĩa...")
    await msg.edit(embed=embed, view=view)

    # Custom emoji của server cho Tài Xỉu
    c_1 = "<:1_:1537536772580319363>"
    c_2 = "<:2_:1537536744889651291>"
    c_3 = "<:3_:1537536722047467640>"
    c_4 = "<:4_:1537536698978934876>"
    c_5 = "<:5_:1537536672655347742>"
    c_6 = "<:6_:1537536622575358096>"

    tx_shake_frames = [
        f"🎲 **Nhà cái đang xóc đĩa...**\n# {c_1} {c_3} {c_5}",
        f"🎲 **Xúc xắc đang nhảy múa...**\n# {c_2} {c_4} {c_3}",
        f"🎲 **Chuẩn bị mở bát tài xỉu...**\n# {c_6} {c_2} {c_5}"
    ]

    for frame in tx_shake_frames:
        await asyncio.sleep(0.6)
        anim_embed = discord.Embed(title="🎲 ĐANG XÓC TÀI XỈU 🎲", description=frame, color=discord.Color.orange())
        await msg.edit(embed=anim_embed)

    # 1. TÍNH TOÁN KẾT QUẢ CHÍNH THỨC
    dice1, dice2, dice3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = dice1 + dice2 + dice3
    is_tai = total >= 11
    tai_xiu_str = "TÀI" if is_tai else "XỈU"
    chan_le_str = "CHẴN" if total % 2 == 0 else "LẺ"

    # 3. TÍNH TOÁN TIỀN THẮNG THUA CỦA NGƯỜI CHƠI
    bets_in_this_game = active_bets.get(msg.id, [])
   
    if msg.id in active_bets: del active_bets[msg.id]

    # 4. TẠO TỔNG KẾT CHI TIẾT (NGƯỜI CƯỢC, CỬA, THẮNG/THUA)
    summary_results = []
    if not bets_in_this_game:
        summary_results.append("🚫 Không có ai cược cả!")
    else:
        for bet in bets_in_this_game:
            user_id = bet["user_id"]
            choice = bet["choice_value"]
            money = bet["money"]
           
            win = (choice == "tai" and is_tai) or (choice == "xiu" and not is_tai) or \
                  (choice == "chan" and total % 2 == 0) or (choice == "le" and total % 2 != 0) or \
                  (choice.startswith("so_") and total == int(choice.split("_")[1]))

            if win:
                multiplier = 10 if choice.startswith("so_") else 2
                payout = money * multiplier
                update_balance(user_id, payout)
                summary_results.append(f"✅ <@{user_id}>: Cược **{bet['choice_name']}** ({money:,} 🪙) ➔ **Ăn {payout:,} 🪙**")
            else:
                summary_results.append(f"❌ <@{user_id}>: Cược **{bet['choice_name']}** ({money:,} 🪙) ➔ **Thua {money:,} 🪙**")

    # 5. HIỂN THỊ KẾT QUẢ
    result_embed = discord.Embed(title="🎲 KẾT QUẢ HABIBI 🎲", color=discord.Color.gold())
    result_embed.description = f"**Kết quả: {dice1} - {dice2} - {dice3} = {total}**\n📊 **{tai_xiu_str}** | **{chan_le_str}**"
   
    result_embed.add_field(name="📝 TỔNG KẾT GIAO DỊCH:", value="\n".join(summary_results), inline=False)
   
    await msg.edit(embed=result_embed, view=None, attachments=[])
import os
from dotenv import load_dotenv

# Khởi chạy bot an toàn bằng biến môi trường
load_dotenv()
bot.run(os.getenv('DISCORD_TOKEN'))