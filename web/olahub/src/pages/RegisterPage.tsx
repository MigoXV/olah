"use client"

import { useState } from "react"
import { Form, Input, Button, Card, Typography, Divider, message } from "antd"
import { UserOutlined, LockOutlined, MailOutlined, GithubOutlined, GoogleOutlined } from "@ant-design/icons"
import { Link, useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"
import { useAuth } from "../contexts/AuthContext"

const { Title, Text } = Typography

const RegisterPage = () => {
  const { t } = useTranslation()
  const { register } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  const onFinish = async (values: { username: string; email: string; password: string; confirm: string }) => {
    if (values.password !== values.confirm) {
      message.error(t("auth.passwordMismatch"))
      return
    }

    try {
      setLoading(true)
      await register(values.username, values.email, values.password)
      message.success(t("auth.registerSuccess"))
      navigate("/")
    } catch (error) {
      console.error("Registration error:", error)
      message.error(t("auth.registerFailed"))
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
          <Title level={2}>{t("auth.registerTitle")}</Title>
          <Text type="secondary">{t("auth.registerSubtitle")}</Text>
        </div>

        <Form name="register" onFinish={onFinish} layout="vertical" size="large">
          <Form.Item
            name="username"
            rules={[
              { required: true, message: t("auth.usernameRequired") },
              { min: 3, message: t("auth.usernameMinLength") },
              { pattern: /^[a-zA-Z0-9_-]+$/, message: t("auth.usernamePattern") },
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder={t("auth.username")} />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: t("auth.emailRequired") },
              { type: "email", message: t("auth.emailInvalid") },
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder={t("auth.email")} />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: t("auth.passwordRequired") },
              { min: 8, message: t("auth.passwordMinLength") },
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder={t("auth.password")} />
          </Form.Item>

          <Form.Item
            name="confirm"
            dependencies={["password"]}
            rules={[
              { required: true, message: t("auth.confirmPasswordRequired") },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue("password") === value) {
                    return Promise.resolve()
                  }
                  return Promise.reject(new Error(t("auth.passwordMismatch")))
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder={t("auth.confirmPassword")} />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" className="w-full" loading={loading}>
              {t("auth.registerTitle")}
            </Button>
          </Form.Item>

          <div className="text-center mb-4">
            <Text type="secondary">{t("auth.hasAccount")} </Text>
            <Link to="/login" className="text-blue-600 hover:text-blue-800">
              {t("auth.loginNow")}
            </Link>
          </div>

          <Divider plain>{t("auth.orRegisterWith")}</Divider>

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

export default RegisterPage
