const SESSION_KEY = "session_id"
const USER_KEY = "user_info"

// data 为后端登录/注册接口返回的 data 对象，
// 其中包含 session_id 以及 user_id/email/username/role/status 等用户信息
export function setSession(data) {
    if (!data || !data.session_id) {
        return
    }
    sessionStorage.setItem(SESSION_KEY, data.session_id)
    sessionStorage.setItem(USER_KEY, JSON.stringify({
        user_id: data.user_id,
        email: data.email,
        username: data.username,
        role: data.role,
        status: data.status,
    }))
}

export function getSession() {
    return sessionStorage.getItem(SESSION_KEY)
}

export function removeSession() {
    sessionStorage.removeItem(SESSION_KEY)
    sessionStorage.removeItem(USER_KEY)
}

// 读取存储的用户信息对象
// session_id 是 UUID，无法像 JWT 那样解码出用户信息，
// 所以登录时把用户信息一并存入 sessionStorage，这里直接读取
function getUserInfo() {
    const raw = sessionStorage.getItem(USER_KEY)
    if (!raw) {
        return null
    }
    try {
        return JSON.parse(raw)
    } catch (error) {
        return null
    }
}

// 获取用户名
export function getUsername() {
    const info = getUserInfo()
    return info ? info.username : null
}

// 获取邮箱
export function getEmail() {
    const info = getUserInfo()
    return info ? info.email : null
}

// 获取用户ID
export function getUserId() {
    const info = getUserInfo()
    return info ? info.user_id : null
}

// 获取用户角色
export function getRole() {
    const info = getUserInfo()
    return info ? info.role : null
}

// 获取用户封禁状态
export function getStatus() {
    const info = getUserInfo()
    return info ? info.status : null
}
