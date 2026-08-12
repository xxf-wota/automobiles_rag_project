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
