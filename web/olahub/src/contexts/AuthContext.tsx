"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { message } from "antd"
import { useTranslation } from "react-i18next"
import { api } from "../utils/api"

interface User {
  id: string
  username: string
  email: string
  avatar?: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const { t } = useTranslation()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("token")
        if (token) {
          const response = await api.get("/auth/me")
          setUser(response.data)
        }
      } catch (error) {
        localStorage.removeItem("token")
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      setLoading(true)
      const response = await api.post("/auth/login", { email, password })
      localStorage.setItem("token", response.data.token)
      setUser(response.data.user)
      message.success(t("auth.loginSuccess"))
    } catch (error) {
      message.error(t("auth.loginFailed"))
      throw error
    } finally {
      setLoading(false)
    }
  }

  const register = async (username: string, email: string, password: string) => {
    try {
      setLoading(true)
      const response = await api.post("/auth/register", { username, email, password })
      localStorage.setItem("token", response.data.token)
      setUser(response.data.user)
      message.success(t("auth.registerSuccess"))
    } catch (error) {
      message.error(t("auth.registerFailed"))
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem("token")
    setUser(null)
    message.success(t("auth.logoutSuccess"))
  }

  return <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>
}
