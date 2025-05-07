import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { ConfigProvider } from "antd"
import zhCN from "antd/lib/locale/zh_CN"
import Layout from "./components/Layout"
import HomePage from "./pages/HomePage"
import LoginPage from "./pages/LoginPage"
import RegisterPage from "./pages/RegisterPage"
import UserProfilePage from "./pages/UserProfilePage"
import ModelsPage from "./pages/ModelsPage"
import ModelDetailPage from "./pages/ModelDetailPage"
import DatasetsPage from "./pages/DatasetsPage"
import DatasetDetailPage from "./pages/DatasetDetailPage"
import { AuthProvider } from "./contexts/AuthContext"
import ProtectedRoute from "./components/ProtectedRoute"

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route path="login" element={<LoginPage />} />
              <Route path="register" element={<RegisterPage />} />
              <Route path="models" element={<ModelsPage />} />
              <Route path="models/:id" element={<ModelDetailPage />} />
              <Route path="datasets" element={<DatasetsPage />} />
              <Route path="datasets/:id" element={<DatasetDetailPage />} />
              <Route
                path="profile/:username"
                element={
                  <ProtectedRoute>
                    <UserProfilePage />
                  </ProtectedRoute>
                }
              />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </ConfigProvider>
  )
}

export default App
