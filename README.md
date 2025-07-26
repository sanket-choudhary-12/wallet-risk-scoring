# Wallet Risk Scoring System
**Blockchain Transaction Analysis for Compound Protocol**

## Overview
This project implements a comprehensive wallet risk scoring system that analyzes Ethereum wallet addresses and their interactions with the Compound DeFi protocol. Each wallet receives a risk score from 0-1000, where lower scores indicate lower risk.

## Features
- **Comprehensive Data Collection**: Fetches complete transaction history via Etherscan API
- **Multi-dimensional Risk Analysis**: Evaluates 9+ risk factors including DeFi engagement, activity patterns, and transaction reliability
- **Compound Protocol Focus**: Specifically analyzes interactions with Compound V2/V3 lending markets
- **Scalable Architecture**: Efficient processing with rate limiting and error handling
- **Visual Analytics**: Generates comprehensive graphs and statistical analysis

## Quick Start

### Prerequisites
```bash
pip install pandas requests numpy matplotlib seaborn sklearn
```

### Usage
1. **Prepare Data**: Save wallet addresses in `wallet_addresses.csv` with column `wallet_id`
2. **Run Analysis**: 
   ```bash
   python main.py
   ```


### API Setup
Get your free Etherscan API key from [etherscan.io/apis](https://etherscan.io/apis) and update the `API_KEY` variable in `main.py`.



## Risk Scoring Methodology

### Score Calculation
- **Base Score**: 500 (medium risk)
- **Range**: 0-1000 (lower = better)
- **Method**: Base + Risk Penalties - Protective Benefits

### Key Risk Factors
| Factor | Weight | Description |
|--------|---------|-------------|
| Failed TX Ratio | 200 | Transaction failure rate |
| Inactivity | 1.0/day | Days since last transaction (>90 days) |
| Low Activity | 100 | Accounts with <10 transactions |
| No DeFi Usage | 50 | Zero Compound protocol interactions |
| High Gas Usage | 30 | Unusual gas consumption patterns |

### Protective Factors
| Factor | Weight | Cap | Description |
|--------|---------|-----|-------------|
| Transaction Volume | 0.5 | -100 | Total transaction count |
| Account Age | 0.1 | -100 | Days since first transaction |
| DeFi Engagement | 2.0 | -150 | Compound protocol interactions |
| Contract Diversity | 5.0 | -100 | Unique contract interactions |
| Value Volume | 1.0 | -200 | Total ETH transaction value |

## Sample Results
Based on analysis of 100 wallets:
- **Average Risk Score**: 731.5
- **High Risk (700+)**: 84% of wallets
- **Medium Risk (300-699)**: 15% of wallets  
- **Low Risk (0-299)**: 1% of wallets

## Monitored Contracts
The system tracks interactions with key Compound protocol addresses:
- Comptroller V2: `0x3d9819210a31b4961b30ef54be2aed79b9c9cd3b`
- cUSDC: `0x39aa39c021dfbae8fac545936693ac917d5e7563`
- cDAI: `0x5d3a536e4d6dbd6114cc1ead35777bab948e3643`
- cETH: `0x4ddc2d193948926d02f9b1fe9e1daa0718270ed5`
- cUSDT: `0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9`
- cWBTC: `0xc11b1268c1a384e55c48c2391d8d480264a3a7f4`
- Compound V3 USDC: `0xc3d688b66703497daa19211eedff47f25384cdc3`
- Compound V3 ETH: `0xa17581a9e3356d9a858b789d68b4d866e593ae94`

## Output Format
The main output file `wallet_risk_scores.csv` contains:
```csv
wallet_id,score
0x1234...,532
0x5678...,789
```

## Technical Details
- **API**: Etherscan REST API with rate limiting (200ms delays)
- **Processing Time**: ~20 minutes for 100 wallets
- **Success Rate**: 100% data retrieval and processing
- **Memory Usage**: Minimal footprint with streaming processing

## Use Cases
- **DeFi Protocol Risk Assessment**: Evaluate user risk profiles for lending/borrowing
- **Compliance & AML**: Identify potentially suspicious wallet activity
- **Portfolio Management**: Risk-adjusted DeFi participation limits
- **Research**: Blockchain behavior pattern analysis

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

