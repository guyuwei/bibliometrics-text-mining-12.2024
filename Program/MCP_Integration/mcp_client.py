"""
MCP (Model Context Protocol) Integration Module
用于集成MCP服务器功能到文献计量分析系统中
"""

import json
import os
import subprocess
import asyncio
from typing import Dict, List, Optional, Any
import streamlit as st

class MCPClient:
    """MCP客户端，用于与MCP服务器通信"""
    
    def __init__(self, config_path: str = None):
        """
        初始化MCP客户端
        
        Args:
            config_path: MCP配置文件路径
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "mcp_config.json"
        )
        self.servers = {}
        self.load_config()
    
    def load_config(self):
        """加载MCP配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.servers = config.get('mcpServers', {})
                    st.success(f"✅ MCP配置加载成功，发现 {len(self.servers)} 个服务器")
            else:
                st.warning("⚠️ MCP配置文件不存在")
        except Exception as e:
            st.error(f"❌ MCP配置加载失败: {str(e)}")
    
    def get_available_servers(self) -> List[str]:
        """获取可用的MCP服务器列表"""
        return list(self.servers.keys())
    
    def check_server_status(self, server_name: str) -> bool:
        """检查MCP服务器状态"""
        try:
            if server_name not in self.servers:
                return False
            
            server_config = self.servers[server_name]
            command = server_config.get('command', '')
            
            # 简单的命令检查
            if command == 'zotero-mcp':
                # 检查Zotero MCP是否可用
                return self._check_zotero_mcp()
            elif command == 'npx':
                # 检查NPX是否可用
                return self._check_npx()
            
            return True
        except Exception as e:
            st.error(f"❌ 检查服务器 {server_name} 状态失败: {str(e)}")
            return False
    
    def _check_zotero_mcp(self) -> bool:
        """检查Zotero MCP是否可用"""
        try:
            result = subprocess.run(['zotero-mcp', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_npx(self) -> bool:
        """检查NPX是否可用"""
        try:
            result = subprocess.run(['npx', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def search_literature(self, query: str, server: str = "brave-search") -> Dict[str, Any]:
        """
        搜索文献
        
        Args:
            query: 搜索查询
            server: 使用的MCP服务器
            
        Returns:
            搜索结果
        """
        try:
            if server not in self.servers:
                return {"error": f"服务器 {server} 不存在"}
            
            # 这里应该实现实际的MCP通信
            # 目前返回模拟数据
            return {
                "query": query,
                "results": [
                    {
                        "title": f"相关文献: {query}",
                        "authors": "作者1, 作者2",
                        "journal": "示例期刊",
                        "year": "2024",
                        "abstract": f"这是关于 {query} 的文献摘要...",
                        "url": "https://example.com"
                    }
                ],
                "total": 1
            }
        except Exception as e:
            return {"error": f"搜索失败: {str(e)}"}
    
    def get_zotero_references(self, collection: str = None) -> List[Dict[str, Any]]:
        """
        从Zotero获取参考文献
        
        Args:
            collection: Zotero集合名称
            
        Returns:
            参考文献列表
        """
        try:
            if not self.check_server_status("zotero"):
                return []
            
            # 这里应该实现实际的Zotero MCP通信
            # 目前返回模拟数据
            return [
                {
                    "title": "示例文献标题",
                    "authors": "作者1, 作者2",
                    "journal": "示例期刊",
                    "year": "2024",
                    "doi": "10.1000/example",
                    "url": "https://example.com"
                }
            ]
        except Exception as e:
            st.error(f"❌ 获取Zotero参考文献失败: {str(e)}")
            return []
    
    def save_to_memory(self, key: str, data: Any) -> bool:
        """
        保存数据到MCP内存服务器
        
        Args:
            key: 数据键
            data: 数据内容
            
        Returns:
            是否保存成功
        """
        try:
            if not self.check_server_status("memory"):
                return False
            
            # 这里应该实现实际的MCP内存服务器通信
            # 目前使用session_state作为替代
            st.session_state[f"mcp_memory_{key}"] = data
            return True
        except Exception as e:
            st.error(f"❌ 保存到内存失败: {str(e)}")
            return False
    
    def load_from_memory(self, key: str) -> Any:
        """
        从MCP内存服务器加载数据
        
        Args:
            key: 数据键
            
        Returns:
            数据内容
        """
        try:
            if not self.check_server_status("memory"):
                return None
            
            # 这里应该实现实际的MCP内存服务器通信
            # 目前使用session_state作为替代
            return st.session_state.get(f"mcp_memory_{key}")
        except Exception as e:
            st.error(f"❌ 从内存加载失败: {str(e)}")
            return None

def create_mcp_integration_page():
    """创建MCP集成页面"""
    st.markdown("## 🔗 MCP (Model Context Protocol) 集成")
    
    # 初始化MCP客户端
    mcp_client = MCPClient()
    
    # 显示可用服务器
    st.markdown("### 📡 可用MCP服务器")
    available_servers = mcp_client.get_available_servers()
    
    if available_servers:
        for server in available_servers:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{server}**")
            with col2:
                status = mcp_client.check_server_status(server)
                if status:
                    st.success("✅ 在线")
                else:
                    st.error("❌ 离线")
            with col3:
                if st.button(f"测试 {server}", key=f"test_{server}"):
                    if mcp_client.check_server_status(server):
                        st.success(f"✅ {server} 服务器运行正常")
                    else:
                        st.error(f"❌ {server} 服务器无法连接")
    else:
        st.warning("⚠️ 未发现可用的MCP服务器")
    
    # 文献搜索功能
    st.markdown("### 🔍 文献搜索")
    search_query = st.text_input("输入搜索查询", placeholder="例如: bibliometric analysis")
    
    if st.button("搜索文献", type="primary"):
        if search_query:
            with st.spinner("正在搜索文献..."):
                results = mcp_client.search_literature(search_query)
                if "error" in results:
                    st.error(f"❌ {results['error']}")
                else:
                    st.success(f"✅ 找到 {results['total']} 个结果")
                    for result in results['results']:
                        with st.expander(f"📄 {result['title']}"):
                            st.write(f"**作者**: {result['authors']}")
                            st.write(f"**期刊**: {result['journal']}")
                            st.write(f"**年份**: {result['year']}")
                            st.write(f"**摘要**: {result['abstract']}")
                            st.write(f"**链接**: {result['url']}")
    
    # Zotero集成
    st.markdown("### 📚 Zotero集成")
    if st.button("获取Zotero参考文献"):
        with st.spinner("正在从Zotero获取参考文献..."):
            references = mcp_client.get_zotero_references()
            if references:
                st.success(f"✅ 获取到 {len(references)} 个参考文献")
                for ref in references:
                    with st.expander(f"📖 {ref['title']}"):
                        st.write(f"**作者**: {ref['authors']}")
                        st.write(f"**期刊**: {ref['journal']}")
                        st.write(f"**年份**: {ref['year']}")
                        st.write(f"**DOI**: {ref['doi']}")
            else:
                st.warning("⚠️ 未找到参考文献或Zotero服务器不可用")
    
    # 内存管理
    st.markdown("### 💾 内存管理")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 保存数据")
        save_key = st.text_input("数据键", placeholder="例如: analysis_results")
        save_data = st.text_area("数据内容", placeholder="输入要保存的数据...")
        if st.button("保存到内存"):
            if save_key and save_data:
                if mcp_client.save_to_memory(save_key, save_data):
                    st.success("✅ 数据保存成功")
                else:
                    st.error("❌ 数据保存失败")
    
    with col2:
        st.markdown("#### 加载数据")
        load_key = st.text_input("数据键", placeholder="例如: analysis_results", key="load_key")
        if st.button("从内存加载"):
            if load_key:
                data = mcp_client.load_from_memory(load_key)
                if data:
                    st.success("✅ 数据加载成功")
                    st.text_area("数据内容", value=str(data), height=100, key="loaded_data")
                else:
                    st.warning("⚠️ 未找到指定键的数据")

if __name__ == "__main__":
    create_mcp_integration_page()





