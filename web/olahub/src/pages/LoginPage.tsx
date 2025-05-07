"use client"

import { useState } from "react"
import { Form, Input, Button, Checkbox, Card, Typography, Divider, message } from "antd"
import { UserOutlined, LockOutlined, GithubOutlined, GoogleOutlined } from "@ant-design/icons"
import { Link, useNavigate, useLocation } from "react-router-dom"
import { useTranslation } from "react-i18next"
import { useAuth } from "../contexts/AuthContext"

const { Title, Text } = Typography

interface LocationState {
  from?: {
    pathname: string
  }
}

const LoginPage = () => {
  const { t } = useTranslation()
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [loading, setLoading] = useState(false)

  const locationState = location.state as LocationState
  const from = locationState?.from?.pathname || "/"

  const onFinish = async (values: { email: string; password: string; remember: boolean }) => {
    try {
      setLoading(true)
      await login(values.email, values.password)
      message.success(t("auth.loginSuccess"))
      navigate(from, { replace: true })
    } catch (error) {
      console.error("Login error:", error)
      message.error(t("auth.loginFailed"))
      setLoading(false)
    }
  }

  const handleSocialLogin = (provider: string) => {
    message.info(t("auth.socialLoginDev", { provider }))
  }

  return (
    <div className="flex justify-center items-center min-h-[calc(100vh-200px)]">
      <Card className="w-full max-w-md shadow-md">
        <div className="text-center mb-6">
          <Title level={2}>{t("auth.loginTitle")}</Title>
          <Text type="secondary">{t("auth.loginSubtitle")}</Text>
        </div>

        <Form name="login" initialValues={{ remember: true }} onFinish={onFinish} layout="vertical" size="large">
          <Form.Item
            name="email"
            rules={[
              { required: true, message: t("auth.emailRequired") },
              { type: "email", message: t("auth.emailInvalid") },
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder={t("auth.email")} />
          </Form.Item>

          <Form.Item name="password" rules={[{ required: true, message: t("auth.passwordRequired") }]}>
            <Input.Password prefix={<LockOutlined />} placeholder={t("auth.password")} />
          </Form.Item>

          <Form.Item>
            <div className="flex justify-between">
              <Form.Item name="remember" valuePropName="checked" noStyle>
                <Checkbox>{t("auth.rememberMe")}</Checkbox>
              </Form.Item>
              <Link to="/forgot-password" className="text-blue-600 hover:text-blue-800">
                {t("auth.forgotPassword")}
              </Link>
            </div>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" className="w-full" loading={loading}>
              {t("auth.loginTitle")}
            </Button>
          </Form.Item>

          <div className="text-center mb-4">
            <Text type="secondary">{t("auth.noAccount")} </Text>
            <Link to="/register" className="text-blue-600 hover:text-blue-800">
              {t("auth.registerNow")}
            </Link>
          </div>

          <Divider plain>{t("auth.orLoginWith")}</Divider>

          <div className="flex justify-center space-x-4">
            <Button icon={<GithubOutlined />} size="large" onClick={() => handleSocialLogin("GitHub")}>
              GitHub
            </Button>
            <Button icon={<GoogleOutlined />} size="large" onClick={() => handleSocialLogin("Google")}>
              Google
            </Button>
          </div>
        </Form>
      </Card>
    </div>
  )
}

export default LoginPage
