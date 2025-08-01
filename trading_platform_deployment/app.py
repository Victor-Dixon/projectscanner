from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

TRADING_CONFIG = {
    "platform_name": "TradingRobotPlugWeb",
    "version": "1.0.0",
    "features": ["Automated Trading", "Portfolio Management", "Risk Analysis"]
}

@app.route('/')
def dashboard():
    return render_template('dashboard.html', config=TRADING_CONFIG)

@app.route('/api/trading/status')
def trading_status():
    return jsonify({
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "active_strategies": 3,
        "portfolio_value": 125000.00
    })

@app.route('/api/trading/execute', methods=['POST'])
def execute_trade():
    data = request.json
    return jsonify({
        "status": "executed",
        "order_id": "TR" + str(int(datetime.now().timestamp())),
        "symbol": data.get("symbol"),
        "quantity": data.get("quantity"),
        "price": data.get("price")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
