import pandas as pd
import requests
import time
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

# Put your Etherscan API key here
API_KEY = "RQKE5XBV24E9AY16ZZ79HDZSC1DWBH9XNZ"

# Compound protocol addresses
COMPOUND_ADDRESSES = {
    '0x3d9819210a31b4961b30ef54be2aed79b9c9cd3b',  # Comptroller V2
    '0x39aa39c021dfbae8fac545936693ac917d5e7563',  # cUSDC
    '0x5d3a536e4d6dbd6114cc1ead35777bab948e3643',  # cDAI
    '0x4ddc2d193948926d02f9b1fe9e1daa0718270ed5',  # cETH
    '0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9',  # cUSDT
    '0xc11b1268c1a384e55c48c2391d8d480264a3a7f4',  # cWBTC
    '0xc3d688b66703497daa19211eedff47f25384cdc3',  # Compound V3 USDC
    '0xa17581a9e3356d9a858b789d68b4d866e593ae94'   # Compound V3 ETH
}

def get_transactions(address, api_key):
    """Get all transactions for a wallet"""
    url = "https://api.etherscan.io/api"
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'desc',
        'apikey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data['status'] == '1':
            return data['result']
        else:
            print(f"Error for {address}: {data.get('message', 'Unknown error')}")
            return []
    except:
        return []

def get_token_transfers(address, api_key):
    """Get ERC20 token transfers"""
    url = "https://api.etherscan.io/api"
    params = {
        'module': 'account',
        'action': 'tokentx',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'desc',
        'apikey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data['status'] == '1':
            return data['result']
        else:
            return []
    except:
        return []

def calculate_features(address, transactions, token_transfers):
    """Calculate risk features for a wallet"""
    current_time = int(datetime.now().timestamp())
    
    # Basic stats
    total_txs = len(transactions)
    total_tokens = len(token_transfers)
    
    if total_txs == 0:
        return {
            'wallet_id': address,
            'total_transactions': 0,
            'compound_transactions': 0,
            'failed_tx_ratio': 0,
            'avg_gas_used': 0,
            'total_value_eth': 0,
            'account_age_days': 0,
            'days_since_last_tx': 999,
            'unique_contracts': 0,
            'high_value_txs': 0
        }
    
    # Filter Compound transactions
    compound_txs = []
    for tx in transactions:
        if tx.get('to', '').lower() in COMPOUND_ADDRESSES:
            compound_txs.append(tx)
    
    # Calculate metrics
    failed_txs = sum(1 for tx in transactions if tx.get('isError') == '1')
    failed_ratio = failed_txs / total_txs if total_txs > 0 else 0
    
    # Gas usage
    gas_used = [int(tx.get('gasUsed', 0)) for tx in transactions if tx.get('gasUsed')]
    avg_gas = np.mean(gas_used) if gas_used else 0
    
    # Value analysis
    values = []
    for tx in transactions:
        if tx.get('value'):
            value_wei = int(tx['value'])
            value_eth = value_wei / 1e18
            values.append(value_eth)
    
    total_value = sum(values) if values else 0
    high_value_txs = sum(1 for v in values if v > 1) if values else 0  # > 1 ETH
    
    # Time analysis
    timestamps = [int(tx['timeStamp']) for tx in transactions if tx.get('timeStamp')]
    if timestamps:
        timestamps.sort()
        first_tx = timestamps[0]
        last_tx = timestamps[-1]
        account_age = (current_time - first_tx) / 86400  # days
        days_since_last = (current_time - last_tx) / 86400
    else:
        account_age = 0
        days_since_last = 999
    
    # Unique contracts interacted with
    unique_contracts = len(set(tx.get('to', '').lower() for tx in transactions if tx.get('to')))
    
    return {
        'wallet_id': address,
        'total_transactions': total_txs,
        'compound_transactions': len(compound_txs),
        'failed_tx_ratio': failed_ratio,
        'avg_gas_used': avg_gas,
        'total_value_eth': total_value,
        'account_age_days': account_age,
        'days_since_last_tx': days_since_last,
        'unique_contracts': unique_contracts,
        'high_value_txs': high_value_txs
    }

def calculate_risk_score(features):
    """Calculate risk score from features"""
    
    # Risk weights (higher = more risk)
    risk_factors = {
        'failed_tx_ratio': 200,          # Failed transactions = high risk
        'days_since_last_tx': 1,         # Inactive accounts = medium risk  
        'low_activity': 100,             # Very few transactions = high risk
        'no_compound': 50,               # No DeFi usage = medium risk
        'high_gas': 30,                  # Unusual gas usage = low risk
    }
    
    # Protective factors (higher = lower risk)
    protective_factors = {
        'total_transactions': 0.5,       # More transactions = lower risk
        'account_age_days': 0.1,         # Older account = lower risk
        'compound_transactions': 2,      # DeFi usage = lower risk
        'unique_contracts': 5,           # More contract interactions = lower risk
        'total_value_eth': 1,            # Higher volume = lower risk
    }
    
    risk_score = 500  # Start at medium risk
    
    # Add risk factors
    risk_score += features['failed_tx_ratio'] * risk_factors['failed_tx_ratio']
    
    if features['days_since_last_tx'] > 90:  # Inactive for 3+ months
        risk_score += min(features['days_since_last_tx'], 365) * risk_factors['days_since_last_tx']
    
    if features['total_transactions'] < 10:  # Very low activity
        risk_score += risk_factors['low_activity']
    
    if features['compound_transactions'] == 0:  # No DeFi usage
        risk_score += risk_factors['no_compound']
    
    if features['avg_gas_used'] > 500000:  # Unusually high gas
        risk_score += risk_factors['high_gas']
    
    # Subtract protective factors
    risk_score -= min(features['total_transactions'] * protective_factors['total_transactions'], 100)
    risk_score -= min(features['account_age_days'] * protective_factors['account_age_days'], 100)
    risk_score -= min(features['compound_transactions'] * protective_factors['compound_transactions'], 150)
    risk_score -= min(features['unique_contracts'] * protective_factors['unique_contracts'], 100)
    risk_score -= min(features['total_value_eth'] * protective_factors['total_value_eth'], 200)
    
    # Ensure score is within 0-1000 range
    risk_score = max(0, min(1000, int(risk_score)))
    
    return risk_score

def main():
    print("Wallet Risk Scoring Started...")
    
    # Check API key
    if API_KEY == "YOUR_ETHERSCAN_API_KEY_HERE":
        print("ERROR: Please add your Etherscan API key to the script!")
        print("Get it from: https://etherscan.io/apis")
        return
    
    # Load wallet addresses
    try:
        df = pd.read_csv('wallet_addresses.csv')
        wallets = df['wallet_id'].tolist()
    except:
        print("ERROR: wallet_addresses.csv not found!")
        print("Save the wallet addresses CSV file in the same folder as this script")
        return
    
    print(f"Processing {len(wallets)} wallets...")
    
    results = []
    
    for i, wallet in enumerate(wallets):
        print(f"Processing {i+1}/{len(wallets)}: {wallet}")
        
        # Get transaction data
        transactions = get_transactions(wallet, API_KEY)
        token_transfers = get_token_transfers(wallet, API_KEY)
        
        # Calculate features
        features = calculate_features(wallet, transactions, token_transfers)
        
        # Calculate risk score
        risk_score = calculate_risk_score(features)
        
        results.append({
            'wallet_id': wallet,
            'score': risk_score
        })
        
        # Rate limiting - wait between requests
        time.sleep(0.2)
    
    # Save results
    output_df = pd.DataFrame(results)
    output_df.to_csv('wallet_risk_scores.csv', index=False)
    
    print(f"\n✅ COMPLETED!")
    print(f"Results saved to: wallet_risk_scores.csv")
    print(f"Average risk score: {output_df['score'].mean():.1f}")
    print(f"Score range: {output_df['score'].min()} - {output_df['score'].max()}")
    
    # Show risk distribution
    high_risk = (output_df['score'] > 700).sum()
    medium_risk = ((output_df['score'] >= 300) & (output_df['score'] <= 700)).sum()
    low_risk = (output_df['score'] < 300).sum()
    
    print(f"\nRisk Distribution:")
    print(f"High Risk (700-1000): {high_risk} wallets")
    print(f"Medium Risk (300-700): {medium_risk} wallets")
    print(f"Low Risk (0-300): {low_risk} wallets")

if __name__ == "__main__":
    main()