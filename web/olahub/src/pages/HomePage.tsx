"use client"

import { useState, useEffect } from "react"
import { Typography, Card, Row, Col, Statistic, Tabs, List, Tag, Spin, Button } from "antd"
import {
  DownloadOutlined,
  StarOutlined,
  FireOutlined,
  AppstoreOutlined,
  DatabaseOutlined,
  UserOutlined,
} from "@ant-design/icons"
import { Link } from "react-router-dom"
import { useTranslation } from "react-i18next"
import { api } from "../utils/api"

const { Title, Paragraph } = Typography
const { TabPane } = Tabs

interface Model {
  id: string
  name: string
  author: string
  downloads: number
  stars: number
  tags: string[]
  description: string
}

interface Dataset {
  id: string
  name: string
  author: string
  downloads: number
  stars: number
  tags: string[]
  description: string
}

const HomePage = () => {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalModels: 0,
    totalDatasets: 0,
    totalUsers: 0,
    totalDownloads: 0,
  })
  const [trendingModels, setTrendingModels] = useState<Model[]>([])
  const [trendingDatasets, setTrendingDatasets] = useState<Dataset[]>([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        // 在实际应用中，这些会是单独的API调用
        const [statsRes, modelsRes, datasetsRes] = await Promise.all([
          api.get("/api/stats"),
          api.get("/api/models/trending"),
          api.get("/api/datasets/trending"),
        ])


        // 三个的data都不是undefined
        if (statsRes.data != undefined && modelsRes.data != undefined && datasetsRes.data != undefined) {
          console.log("Stats:", statsRes.data)
          console.log("Trending Models:", modelsRes.data)
          console.log("Trending Datasets:", datasetsRes.data)
        } else {
          setStats({
            totalModels: 0,
            totalDatasets: 0,
            totalUsers: 0,
            totalDownloads: 0,
          })
          setTrendingModels([])
          setTrendingDatasets([])
        }
      } catch (error) {
        console.error("Error fetching homepage data:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <div className="bg-gradient-to-r from-blue-700 to-blue-900 text-white p-8 rounded-lg mb-8">
        <Title level={1} className="text-white mb-4">
          {t("home.welcome")}
        </Title>
        <Paragraph className="text-white text-lg mb-6">{t("home.welcomeDesc")}</Paragraph>
        <div className="flex space-x-4">
          <Button type="primary" size="large" className="bg-white text-blue-700 hover:bg-gray-100">
            <Link to="/models">{t("home.browseModels")}</Link>
          </Button>
          <Button ghost size="large">
            <Link to="/datasets" className="text-white">
              {t("home.browseDatasets")}
            </Link>
          </Button>
        </div>
      </div>

      <Row gutter={24} className="mb-8">
        <Col xs={24} sm={12} md={6}>
          <Card hoverable className="shadow-sm">
            <Statistic
              title={t("home.totalModels")}
              value={stats.totalModels}
              prefix={<AppstoreOutlined className="text-blue-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable className="shadow-sm">
            <Statistic
              title={t("home.totalDatasets")}
              value={stats.totalDatasets}
              prefix={<DatabaseOutlined className="text-green-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable className="shadow-sm">
            <Statistic
              title={t("home.totalUsers")}
              value={stats.totalUsers}
              prefix={<UserOutlined className="text-purple-600" />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable className="shadow-sm">
            <Statistic
              title={t("home.totalDownloads")}
              value={stats.totalDownloads}
              prefix={<DownloadOutlined className="text-orange-600" />}
            />
          </Card>
        </Col>
      </Row>

      <Tabs defaultActiveKey="models" className="mb-8">
        <TabPane
          tab={
            <span>
              <FireOutlined className="text-red-500" /> {t("home.trendingModels")}
            </span>
          }
          key="models"
        >
          <List
            grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 3, xl: 4, xxl: 4 }}
            dataSource={trendingModels}
            renderItem={(model) => (
              <List.Item>
                <Card
                  hoverable
                  className="h-full"
                  title={
                    <Link to={`/models/${model.id}`} className="text-blue-600 hover:text-blue-800">
                      {model.name}
                    </Link>
                  }
                  extra={<StarOutlined className="text-yellow-500" />}
                >
                  <div className="mb-2">
                    <Link to={`/profile/${model.author}`} className="text-gray-600">
                      @{model.author}
                    </Link>
                  </div>
                  <Paragraph ellipsis={{ rows: 2 }} className="text-gray-700 mb-3">
                    {model.description}
                  </Paragraph>
                  <div className="flex justify-between items-center">
                    <div>
                      {model.tags.slice(0, 2).map((tag) => (
                        <Tag key={tag} color="blue" className="mr-1">
                          {tag}
                        </Tag>
                      ))}
                      {model.tags.length > 2 && <Tag>+{model.tags.length - 2}</Tag>}
                    </div>
                    <div className="flex items-center text-gray-500">
                      <DownloadOutlined className="mr-1" /> {model.downloads.toLocaleString()}
                    </div>
                  </div>
                </Card>
              </List.Item>
            )}
          />
          <div className="text-center mt-4">
            <Button type="primary">
              <Link to="/models">{t("home.viewMoreModels")}</Link>
            </Button>
          </div>
        </TabPane>

        <TabPane
          tab={
            <span>
              <FireOutlined className="text-red-500" /> {t("home.trendingDatasets")}
            </span>
          }
          key="datasets"
        >
          <List
            grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 3, xl: 4, xxl: 4 }}
            dataSource={trendingDatasets}
            renderItem={(dataset) => (
              <List.Item>
                <Card
                  hoverable
                  className="h-full"
                  title={
                    <Link to={`/datasets/${dataset.id}`} className="text-green-600 hover:text-green-800">
                      {dataset.name}
                    </Link>
                  }
                  extra={<StarOutlined className="text-yellow-500" />}
                >
                  <div className="mb-2">
                    <Link to={`/profile/${dataset.author}`} className="text-gray-600">
                      @{dataset.author}
                    </Link>
                  </div>
                  <Paragraph ellipsis={{ rows: 2 }} className="text-gray-700 mb-3">
                    {dataset.description}
                  </Paragraph>
                  <div className="flex justify-between items-center">
                    <div>
                      {dataset.tags.slice(0, 2).map((tag) => (
                        <Tag key={tag} color="green" className="mr-1">
                          {tag}
                        </Tag>
                      ))}
                      {dataset.tags.length > 2 && <Tag>+{dataset.tags.length - 2}</Tag>}
                    </div>
                    <div className="flex items-center text-gray-500">
                      <DownloadOutlined className="mr-1" /> {dataset.downloads.toLocaleString()}
                    </div>
                  </div>
                </Card>
              </List.Item>
            )}
          />
          <div className="text-center mt-4">
            <Button type="primary" className="bg-green-600 border-green-600 hover:bg-green-700 hover:border-green-700">
              <Link to="/datasets">{t("home.viewMoreDatasets")}</Link>
            </Button>
          </div>
        </TabPane>
      </Tabs>
    </div>
  )
}

export default HomePage
