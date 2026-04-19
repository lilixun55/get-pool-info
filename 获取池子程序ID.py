#!/usr/bin/env python3

import requests
import json
import sys
from typing import Optional, Dict, Tuple

# DEX程序ID映射
DEX_PROGRAM_IDS = {
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium AMM",
    "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM",
    "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CLMM",
    "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo": "Meteora DLMM",
    "cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG": "Meteora DAMM V2",
    "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB": "Meteora Pool",
    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
    "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "PumpSwap"
}

def get_dex_name(program_id: str) -> str:
    """根据程序ID识别DEX名称"""
    return DEX_PROGRAM_IDS.get(program_id, "未知DEX")

def get_account_info(address: str, rpc_url: str = "https://api.mainnet-beta.solana.com") -> Optional[Dict]:
    """获取账户详细信息"""
    
    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [
            address,
            {
                "encoding": "jsonParsed",
                "commitment": "confirmed"
            }
        ]
    }
    
    try:
        response = requests.post(rpc_url, json=request_data)
        response.raise_for_status()
        
        result = response.json()
        
        if "error" in result:
            print(f"RPC错误: {result['error']}")
            return None
        
        return result["result"]["value"]
        
    except Exception as e:
        print(f"查询失败: {e}")
        return None

def main():
    rpc_url = "https://api.mainnet-beta.solana.com"
    
    print("Solana池子程序ID查询工具")
    print("输入池子地址查询程序ID，输入 'quit' 或 'exit' 退出")
    print("-" * 50)
    
    while True:
        try:
            address = input("\n请输入池子地址: ").strip()
            
            if address.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break
            
            if not address:
                print("请输入有效的地址")
                continue
            
            print(f"查询地址: {address}")
            
            # 获取账户信息
            account_info = get_account_info(address, rpc_url)
            
            if not account_info:
                print("查询失败：账户不存在或网络错误")
                continue
            
            # 获取程序ID
            program_id = account_info.get("owner")
            
            if not program_id:
                print("无法获取程序ID")
                continue
            
            # 获取DEX名称
            dex_name = get_dex_name(program_id)
            
            print(f"程序ID: {program_id}")
            print(f"DEX类型: {dex_name}")
  
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
