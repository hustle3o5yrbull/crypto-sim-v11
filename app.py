from flask import Flask, render_template, request, jsonify
import json
import random
import os

app = Flask(__name__)

# Define defaults
wallet = {'usd': 500.0, 'pepe': 0.0, 'popcat': 0.0, 'turbo': 0.0}
trades = []
leaderboard = []
hit_counts = {'views': 0, 'plays': 0}

# Load existing data if files exist, then override wallet
try:
    with open('wallet.json', 'r') as f:
        json.load(f)  # Load but don’t use—keeps file fresh
except FileNotFoundError:
    with open('wallet.json', 'w') as f:
        json.dump(wallet, f)
wallet = {'usd': 500.0, 'pepe': 0.0, 'popcat': 0.0, 'turbo': 0.0}  # Force reset
with open('wallet.json', 'w') as f:
    json.dump(wallet, f)

try:
    with open('trades.json', 'r') as f:
        trades = json.load(f)
except FileNotFoundError:
    with open('trades.json', 'w') as f:
        json.dump(trades, f)

try:
    with open('leaderboard.json', 'r') as f:
        leaderboard = json.load(f)
except FileNotFoundError:
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard, f)

try:
    with open('hit_counts.json', 'r') as f:
        hit_counts = json.load(f)
except FileNotFoundError:
    with open('hit_counts.json', 'w') as f:
        json.dump(hit_counts, f)

@app.route('/')
def home():
    global hit_counts
    hit_counts['views'] = hit_counts.get('views', 0) + 1  # Increment views
    with open('hit_counts.json', 'w') as f:
        json.dump(hit_counts, f)
    print(f"Serving home page with wallet: {wallet} trades: {trades} views: {hit_counts['views']} plays: {hit_counts['plays']}")
    return render_template('index.html', wallet=wallet, hit_counts=hit_counts)

@app.route('/trade', methods=['POST'])
def trade():
    data = request.get_json()
    action = data['action']
    coin = data['coin']
    amount = float(data['amount'])
    price = float(data['price'])
    time = data['time']

    cost = amount * price
    if action == 'buy':
        if wallet['usd'] >= cost:
            wallet['usd'] -= cost
            wallet[coin] += amount
        else:
            print(f"Trade failed: Insufficient USD for {data}")
            return jsonify({'error': 'Insufficient USD'}), 400
    elif action == 'sell':
        if wallet[coin] >= amount:
            wallet['usd'] += cost
            wallet[coin] -= amount
        else:
            print(f"Trade failed: Insufficient {coin.upper()} for {data}")
            return jsonify({'error': f'Insufficient {coin.upper()}'}), 400

    trades.append(data)
    with open('trades.json', 'w') as f:
        json.dump(trades, f)
    with open('wallet.json', 'w') as f:
        json.dump(wallet, f)

    print(f"Trade executed: {data}")
    print(f"Updated wallet: {wallet}")
    return jsonify({'wallet': wallet, 'trades': trades})

@app.route('/trades', methods=['GET'])
def get_trades():
    return jsonify({'trades': trades})

@app.route('/submit_pnl', methods=['POST'])
def submit_pnl():
    data = request.get_json()
    nickname = data['nickname']
    pnl = float(data['pnl'])
    leaderboard.append({'nickname': nickname, 'pnl': pnl})
    leaderboard.sort(key=lambda x: x['pnl'], reverse=True)
    leaderboard[:] = leaderboard[:5]
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard, f)
    print(f"Leaderboard updated: {leaderboard}")
    return jsonify({'leaderboard': leaderboard})

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    return jsonify({'leaderboard': leaderboard})

@app.route('/reset', methods=['POST'])
def reset():
    global wallet, trades, hit_counts
    wallet = {'usd': 500.0, 'pepe': 0.0, 'popcat': 0.0, 'turbo': 0.0}
    trades = []
    hit_counts['plays'] = hit_counts.get('plays', 0) + 1  # Increment plays
    with open('wallet.json', 'w') as f:
        json.dump(wallet, f)
    with open('trades.json', 'w') as f:
        json.dump(trades, f)
    with open('hit_counts.json', 'w') as f:
        json.dump(hit_counts, f)
    print(f"Wallet and trades reset - Views: {hit_counts['views']} Plays: {hit_counts['plays']}")
    return jsonify({'wallet': wallet, 'trades': trades})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
