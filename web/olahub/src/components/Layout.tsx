"use client"

import { useState } from "react"
import { Outlet, Link, useNavigate } from "react-router-dom"
import { Layout as AntLayout, Menu, Button, Avatar, Dropdown, Badge, theme } from "antd"
import {
  HomeOutlined,
  DatabaseOutlined,
  AppstoreOutlined,
  UserOutlined,
  LogoutOutlined,
  BellOutlined,
} from "@ant-design/icons"
import { useTranslation } from "react-i18next"
import { useAuth } from "../contexts/AuthContext"
import LanguageSwitcher from "./LanguageSwitcher"

const { Header, Content, Footer } = AntLayout

const Layout = () => {
  const { t } = useTranslation()
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const { token } = theme.useToken()



  const userMenu = (
    <Menu>
      <Menu.Item key="profile" icon={<UserOutlined />}>
        <Link to={`/profile/${user?.username}`}>{t("common.profile")}</Link>
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={logout}>
        {t("common.logout")}
      </Menu.Item>
    </Menu>
  )

  return (
    <AntLayout className="min-h-screen">
      <Header
        className="px-6 md:px-12 lg:px-16 flex items-center justify-between"
        style={{ background: "#3c4a5a", padding: "0 24px" }}
      >
        <div className="flex items-center">
          <Link to="/" className="flex items-center mr-8">
            <span className="text-xl font-bold text-white" style={{ fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif" }}>Olah</span>
          </Link>
          <Menu
            mode="horizontal"
            className="border-0 bg-transparent"
            defaultSelectedKeys={["home"]}
            style={{ background: "transparent", color: "white", fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif" }}
            theme="dark"
            selectedStyle={{ color: "#a0d8f7" }}
          >
            <Menu.Item key="home" icon={<HomeOutlined />}>
              <Link to="/">{t("common.home")}</Link>
            </Menu.Item>
            <Menu.Item key="models" icon={<AppstoreOutlined />}>
              <Link to="/models">{t("common.models")}</Link>
            </Menu.Item>
            <Menu.Item key="datasets" icon={<DatabaseOutlined />}>
              <Link to="/datasets">{t("common.datasets")}</Link>
            </Menu.Item>
          </Menu>
        </div>

        <div className="flex items-center">


          <LanguageSwitcher />

          {user ? (
            <div className="flex items-center">
              <Badge count={3} className="mr-4">
                <Button type="text" icon={<BellOutlined />} className="flex items-center justify-center text-white" />
              </Badge>
              <Dropdown overlay={userMenu} trigger={["click"]}>
                <div className="flex items-center cursor-pointer">
                  <Avatar src={user.avatar || undefined} icon={<UserOutlined />} />
                  <span className="ml-2 text-white">{user.username}</span>
                </div>
              </Dropdown>
            </div>
          ) : (
            <div className="flex items-center">
              <Button type="link" className="text-white" onClick={() => navigate("/login")}>
                {t("common.login")}
              </Button>
              <Button type="primary" onClick={() => navigate("/register")}>
                {t("common.register")}
              </Button>
            </div>
          )}
        </div>
      </Header>

      <Content className="p-6 md:px-12 lg:px-16 bg-gray-50">
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <Outlet />
        </div>
      </Content>

      <Footer className="text-center bg-white">HF Mirror ©{new Date().getFullYear()} - Hugging Face Mirror</Footer>
    </AntLayout>
  )
}

export default Layout
