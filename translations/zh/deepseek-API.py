"""
DeepSeek API 持续对话脚本
支持多轮对话，保持上下文
"""

import os
from openai import OpenAI

# 初始化客户端
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

# 对话历史
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant"}
]

def chat_with_deepseek(user_input, stream=False):
    """
    与 DeepSeek 对话
    
    Args:
        user_input: 用户输入
        stream: 是否使用流式输出
        
    Returns:
        str: 助手回复
        
    """
    # 添加用户消息到历史
    conversation_history.append({"role": "user", "content": user_input})
    
    try:
        if stream:
            # 流式输出
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=conversation_history,
                stream=True
            )
            
            print("DeepSeek: ", end="", flush=True)
            full_response = ""
            try:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        print(content, end="", flush=True)
                        full_response += content
                print()  # 换行
                
                # 添加助手回复到历史
                if full_response:
                    conversation_history.append({"role": "assistant", "content": full_response})
                return full_response
            except KeyboardInterrupt:
                print("\n\n⏹️  输出已中断")
                # 如果有部分回复，可以选择是否添加到历史
                if full_response:
                    conversation_history.append({"role": "assistant", "content": full_response})
                return full_response
        else:
            # 非流式输出
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=conversation_history,
                stream=False
            )
            
            assistant_reply = response.choices[0].message.content
            print(f"DeepSeek: {assistant_reply}")
            
            # 添加助手回复到历史
            conversation_history.append({"role": "assistant", "content": assistant_reply})
            return assistant_reply
            
    except KeyboardInterrupt:
        print("\n\n⏹️  请求已中断")
        # 如果出错，移除刚添加的用户消息
        if conversation_history and conversation_history[-1]["role"] == "user":
            conversation_history.pop()
        raise  # 重新抛出，让主循环处理
    except Exception as e:
        print(f"❌ 错误: {e}")
        # 如果出错，移除刚添加的用户消息
        if conversation_history and conversation_history[-1]["role"] == "user":
            conversation_history.pop()
        return None

def main():
    """主函数：持续对话循环"""
    print("=" * 60)
    print("DeepSeek 对话助手")
    print("输入 'quit' 或 'exit' 退出对话")
    print("输入 'clear' 清空对话历史")
    print("输入 'stream' 切换流式输出模式")
    print("按 Ctrl+C 可中断输出")
    print("=" * 60)
    print()
    
    stream_mode = False
    
    while True:
        try:
            # 获取用户输入
            user_input = input("你: ").strip()
            
            # 处理特殊命令
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break
            
            if user_input.lower() == 'clear':
                # 清空历史（保留系统消息）
                conversation_history.clear()
                conversation_history.append({"role": "system", "content": "You are a helpful assistant"})
                print("✅ 对话历史已清空")
                continue
            
            if user_input.lower() == 'stream':
                stream_mode = not stream_mode
                print(f"✅ 流式输出模式: {'开启' if stream_mode else '关闭'}")
                continue
            
            # 发送对话请求
            chat_with_deepseek(user_input, stream=stream_mode)
            print()  # 空行分隔
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            continue

if __name__ == "__main__":
    main()