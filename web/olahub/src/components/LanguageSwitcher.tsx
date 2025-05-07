"use client"

import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Dropdown, Button } from "antd"
import { GlobalOutlined } from "@ant-design/icons"
import type { MenuProps } from "antd"

const LanguageSwitcher = () => {
  const { i18n } = useTranslation()
  const [visible, setVisible] = useState(false)

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng)
    setVisible(false)
  }

  const items: MenuProps["items"] = [
    {
      key: "zh",
      label: "中文",
      onClick: () => changeLanguage("zh"),
    },
    {
      key: "en",
      label: "English",
      onClick: () => changeLanguage("en"),
    },
  ]

  return (
    <Dropdown
      menu={{ items }}
      placement="bottomRight"
      open={visible}
      onOpenChange={(flag) => setVisible(flag)}
      trigger={["click"]}
    >
      <Button type="text" icon={<GlobalOutlined />} className="flex items-center text-white">
        {i18n.language === "zh" ? "中文" : "English"}
      </Button>
    </Dropdown>
  )
}

export default LanguageSwitcher
