// 本地存储中保存 token 的键名
const TOKEN_KEY = "access_token"

// 保存 token
export function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
}

// 获取 token
export function getToken() {
    return localStorage.getItem(TOKEN_KEY)
}

// 删除 token
export function removeToken() {
    localStorage.removeItem(TOKEN_KEY)
}

//获取JWT中的username字段
export function getUsername() {
    const token = getToken()
    if (!token) {
        return null
    }
    try {
        // [0] 解析 header 部分
        // [1] 解析 payload 部分
        // [2] 解析 signature 部分
        const decoded = JSON.parse(atob(token.split(".")[1]))
        // console.log(decoded.username)
        return decoded.username

    } catch (error) {
        return null
    }
}

// 获取JWT中的email字段
export function getEmail() {
    const token = getToken()
    if (!token) {
        return null
    }
    try {
        // [0] 解析 header 部分
        // [1] 解析 payload 部分
        // [2] 解析 signature 部分
        const decoded = JSON.parse(atob(token.split(".")[1]))
        // console.log(decoded.email)
        return decoded.email
    } catch (error) {
        return null
    }
}

// 获取JWT中的user_id字段
export function getUserId() {
    const token = getToken()
    if (!token) {
        return null
    }
    try {
        // [0] 解析 header 部分
        // [1] 解析 payload 部分
        // [2] 解析 signature 部分
        const decoded = JSON.parse(atob(token.split(".")[1]))
        // console.log(decoded.user_id)
        return decoded.user_id
    } catch (error) {
        return null
    }
}

// 获取JWT中的role字段
export function getRole() {
    const token = getToken()
    if (!token) {
        return null
    }
    try {
        // [0] 解析 header 部分
        // [1] 解析 payload 部分
        // [2] 解析 signature 部分
        const decoded = JSON.parse(atob(token.split(".")[1]))
        // console.log(decoded.role)
        return decoded.role
    } catch (error) {
        return null
    }
}

// 获取JWT中的status字段
export function getStatus() {
    const token = getToken()
    if (!token) {
        return null
    }
    try {
        // [0] 解析 header 部分
        // [1] 解析 payload 部分
        // [2] 解析 signature 部分
        const decoded = JSON.parse(atob(token.split(".")[1]))
        // console.log(decoded.status)
        return decoded.status
    } catch (error) {
        return null
    }
}





