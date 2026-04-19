from dune_client.client import DuneClient
from dune_client.query import QueryBase
from dune_client.types import QueryParameter
import pandas as pd
import time
import os

# ================= 配置区 =================
# 1. 你的 API Key (注意保密！)
MY_API_KEY = "aha4BDVqhznEdhGwWbwrFLoU5AxRKpuj"

# 2. 你的查询 ID (Query ID)
# 注意：这个 Query ID 需要替换为你自己创建的查询
QUERY_ID = 6279782  # 请替换为你的有效 Query ID 
# ========================================

def get_dune_data():
    print("🚀 正在连接 Dune Analytics...")
    
    # 初始化客户端
    dune = DuneClient(MY_API_KEY)
    
    try:
        # 定义查询对象
        query = QueryBase(query_id=QUERY_ID)
        
        print("⏳ 正在请求最新数据 (这会消耗 Credits)...")
        
        # run_query_dataframe 是官方库提供的神器
        # 它会自动：提交查询 -> 等待计算 -> 下载结果 -> 转成 Pandas 表格
        # performance='medium' 是免费版默认速度
        df = dune.run_query_dataframe(query, performance='medium')
        
        print("✅ 数据获取成功！")
        
        # --- 重命名列为中文 ---
        column_mapping = {
            'token_mint': '代币地址',
            'pool_count': '池子数量',
            'program_count': '程序数量',
            'volume_24h': '24h交易量',
            'dex_names': 'DEX名称'
        }
        df.rename(columns=column_mapping, inplace=True)
        
        # --- 简单清洗与展示 ---
        print(f"\n📊 扫描到的多池代币数量: {len(df)} 个")
        
        # 看看前 5 条数据
        print("\n前 5 名热门代币:")
        print("数据列名:", df.columns.tolist()) 
        
        # 打印关键信息
        if '代币地址' in df.columns:
            print(df[['代币地址', '池子数量', 'DEX名称']].head(5).to_string(index=False))
        else:
            print(df.head(5))

        # --- 保存到本地 ---
        # 保存到程序文件的目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, f"Solana目标代币数据_{int(time.time())}.csv")
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 文件已自动保存为: {filename}")
        print("🎉 现在你可以直接读取这个文件去套利了！")
        
        return df
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        print("提示：如果是 404，可能是 Query ID 填错了；如果是 402，说明积分用完了。")
        return None

if __name__ == "__main__":
    # 直接运行获取数据
    print("📋 开始获取 Dune Analytics 数据...")
    get_dune_data()