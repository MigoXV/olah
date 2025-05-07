import i18n from "i18next"
import { initReactI18next } from "react-i18next"
import LanguageDetector from "i18next-browser-languagedetector"
import Backend from "i18next-http-backend"

import enTranslation from "./locales/en/translation.json"
import zhTranslation from "./locales/zh/translation.json"

// 资源对象，包含所有翻译
const resources = {
  en: {
    translation: enTranslation,
  },
  zh: {
    translation: zhTranslation,
  },
}

i18n
  // 加载翻译文件的后端
  .use(Backend)
  // 检测用户语言
  .use(LanguageDetector)
  // 将 i18n 实例传递给 react-i18next
  .use(initReactI18next)
  // 初始化 i18next
  .init({
    resources,
    fallbackLng: "zh", // 默认语言
    debug: process.env.NODE_ENV === "development",
    interpolation: {
      escapeValue: false, // 不转义 React 已经处理了
    },
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
    },
  })

export default i18n
