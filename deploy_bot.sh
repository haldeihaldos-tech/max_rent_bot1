#!/bin/bash
set -e

# Install system dependencies
apt update
apt install -y python3 python3-pip python3-venv git

# Create project directory
mkdir -p /root/max_rent_bot
cd /root/max_rent_bot

# Clone the bot repository
git clone https://github.com/MultiTool-ai/max_rent_bot.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
ACCESS_TOKEN=f9LHodD0cOKau01XYAiAzxWyXVwL_Q0c4yHnPKRfjMRkZMuSmMVnjilAe2iArV4_vCHg1pJMgFpNbAiZSQbT
ADMIN_USER_ID=515597285
TARGET_CHANNEL_ID=-78791835305405
BOT_LINK=https://max.ru/se13354575_1_bot
CHANNEL_LINK=https://max.ru/channel_krasnodar_arenda
DB_PATH=data/bot.db
DEFAULT_DAILY_LIMIT=2
STRICT_SUBSCRIPTION_CHECK=false
PROFILE_LINK_TEMPLATE=https://max.ru/u{user_id}
EOF

# Create data directory
mkdir -p data

# Run the bot
echo "Starting MAX Rent Bot..."
source venv/bin/activate
python3 main.py