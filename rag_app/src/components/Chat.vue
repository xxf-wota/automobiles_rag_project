<template>
    <!-- 聊天框 -->
    <div style="border: 1px solid #000; width: 800px; height: 700px; margin: 0 auto; position: relative; display: flex; flex-direction: column;">
        <!-- 消息列表区域 -->
        <div style="flex: 1; overflow-y: auto; padding: 10px; display: flex; flex-direction: column;">
            <!-- 如果没有消息，显示提示 -->
            <div v-if="messages.length === 0" style="text-align: center; color: #999; margin-top: 200px;">
                开始对话吧！
            </div>

            <!-- 遍历显示所有消息 -->
            <div v-for="(msg, index) in messages" :key="index"
                 :style="{
                     maxWidth: '70%',
                     padding: '10px 15px',
                     marginBottom: '10px',
                     borderRadius: '10px',
                     wordWrap: 'break-word',
                     alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                     backgroundColor: msg.role === 'user' ? '#95ec69' : '#f0f0f0',
                     border: msg.role === 'user' ? '1px solid #7ecf5a' : '1px solid #ddd'
                 }">
                {{ msg.content }}
            </div>
        </div>

        <!-- 底部输入框和发送按钮 -->
        <div style="border-top: 1px solid #ddd; padding: 10px; display: flex; gap: 10px; background: #fff;">
            <input
                type="text"
                placeholder="请输入问题"
                :disabled="isChat"
                v-model="question"
                @keyup.enter="chat"
                style="flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; outline: none;"
                :style="{ background: isChat ? '#f5f5f5' : '#fff' }"
            >
            <button
                type="button"
                @click="chat"
                :disabled="isChat"
                style="padding: 8px 20px; background: #409eff; color: #fff; border: none; border-radius: 4px; cursor: pointer;"
                :style="{ background: isChat ? '#a0cfff' : '#409eff', cursor: isChat ? 'not-allowed' : 'pointer' }"
            >
                {{ isChat ? '生成中...' : '发送' }}
            </button>
        </div>
    </div>
</template>

<script setup>
import {ref, onUnmounted} from "vue";
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";
import {getToken, removeToken} from "../utils/auth";

// 定义聊天状态，false表示没有聊天，可以输入问题
let isChat = ref(false)
// 定义用户问题
let question = ref("")
// 用于接收服务器返回的回答
let messages = ref([])
// 路由对象，登录过期时跳转登录页
let router = useRouter()
// 保存当前请求的 AbortController，用于中止流式请求
let abortController = null

// chat函数，发送问题，并更新聊天状态
// 使用 fetch + ReadableStream 实现 SSE，可以在请求头中携带 JWT
// EventSource 无法添加自定义请求头，所以改用 fetch
async function chat() {
    isChat.value = true
    let myQuestion = question.value.trim() // 去掉首尾空格
    question.value = "" // 清空输入框

    // 判断是否输入了数据
    if (myQuestion.length === 0) {
        ElMessage.error("请输入问题！")
        isChat.value = false
        return
    }

    // 访问服务器 --- 需要把问题myQuestion发送给服务器
    messages.value.push({role: "user", content: myQuestion})
    messages.value.push({role: "assistant", content: "正在生成回复"})

    // 中止上一次未完成的请求
    if (abortController) {
        abortController.abort()
    }
    abortController = new AbortController()

    // 拼接请求地址
    let urlSearchParams = new URLSearchParams({
        question: myQuestion
    })
    let url = "http://localhost:8000/chat/chat?" + urlSearchParams.toString()

    // 定义拼接结果的变量
    let s = ""

    try {
        // 1. 使用 fetch 发起请求，请求头携带 JWT 令牌
        let response = await fetch(url, {
            headers: {
                "Authorization": "Bearer " + getToken()
            },
            signal: abortController.signal // 用于中止流式请求
        })

        // 2. token 无效或过期，后端返回 401
        if (response.status === 401) {
            removeToken() // 删除过期的 token
            ElMessage.error("登录已过期，请重新登录")
            router.push("/")
            isChat.value = false
            return
        }

        // 3. 其它错误状态码
        if (!response.ok) {
            ElMessage.error("连接服务器失败")
            isChat.value = false
            return
        }

        // 4. 获取响应体流，并流式解码（避免中文等多字节字符被截断导致乱码）
        let reader = response.body.getReader()
        let decoder = new TextDecoder("utf-8")
        // SSE 数据缓冲区
        let buffer = ""

        // 5. 循环读取流数据
        while (true) {
            let {done, value} = await reader.read()
            if (done) break // 连接正常关闭

            // 将本次读取的数据解码并追加到缓冲区
            buffer += decoder.decode(value, {stream: true})

            // 6. 按 SSE 分隔符 \n\n 拆分成完整事件
            let index
            // 当搜索到的 \n\n 是缓冲区中的最后一个字符时，说明是最后一个事件，跳出循环
            while ((index = buffer.indexOf("\n\n")) !== -1) {
                // 提取当前事件文本，从开始0下标到搜索到的 \n\n 下标
                let eventText = buffer.slice(0, index)
                // 从搜索到的 \n\n 下标开始，截取剩余数据
                buffer = buffer.slice(index + 2)

                // 只处理以 data: 开头的行
                let dataLine = eventText
                    .replace(/\r\n/g, "\n") // 兼容 CRLF 换行（回车换行）
                    .split("\n") // 按行拆分事件文本
                    .find(line => line.startsWith("data:")) // 查找以 data: 开头的行
                if (!dataLine) continue // 如果没有 data: 开头的行，跳过

                // slice(5) 从第6个字符开始截取，去掉 "data:" 前缀
                // trim() 去掉首尾空格
                let payload = dataLine.slice(5).trim()
                if (!payload) continue // 如果 payload 为空，跳过

                // 解析 JSON 字符串
                // 后端传过来的时候是"data: {json.dumps({'content': chunk})}\n\n"
                // 解析后是{"content": chunk}
                let parsed
                try {
                    parsed = JSON.parse(payload)
                } catch (e) {
                    console.error("解析SSE数据失败", e)
                    continue
                }
                // 从解析后的 JSON 中提取 content 字段
                let content = parsed.content

                // 7. 处理结束标识 [DONE]
                if (content === "[DONE]") {
                    isChat.value = false // 聊天结束可以输入问题了
                    return
                }

                // 拼接并更新最后一条 assistant 消息的内容
                s += content
                messages.value[messages.value.length - 1].content = s
            }
        }

        isChat.value = false // 流正常结束
    } catch (error) {
        // 8. 处理错误：网络断开、连接中断等（主动 abort 触发的错误不需要提示）
        if (error.name !== "AbortError") {
            ElMessage.error("连接服务器失败")
            console.log("发生错误", error)
        }
        isChat.value = false // 聊天结束可以输入问题了
    }
}

// 挂载函数
// 加载页面后自动执行的代码
// 组件卸载时中止未完成的请求，防止内存泄漏
onUnmounted(() => {
    if (abortController) {
        abortController.abort()
    }
})

</script>

<style scoped>
/* 滚动条美化 */
div::-webkit-scrollbar {
    width: 6px;
}
div::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 3px;
}
div::-webkit-scrollbar-thumb:hover {
    background: #999;
}
</style>