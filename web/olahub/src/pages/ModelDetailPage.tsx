"use client"

import { useState, useEffect } from "react"
import { useParams, Link } from "react-router-dom"
import {
  Typography,
  Button,
  Tabs,
  Card,
  Tag,
  Statistic,
  Descriptions,
  message,
  Spin,
  Breadcrumb,
  Tooltip,
  Modal,
} from "antd"
import {
  DownloadOutlined,
  StarOutlined,
  StarFilled,
  EyeOutlined,
  ShareAltOutlined,
  FileTextOutlined,
  HistoryOutlined,
  QuestionCircleOutlined,
  CopyOutlined,
} from "@ant-design/icons"
import ReactMarkdown from "react-markdown"
import { api } from "../utils/api"
import { useAuth } from "../contexts/AuthContext"

const { Title, Paragraph, Text } = Typography
const { TabPane } = Tabs

interface ModelDetail {
  id: string
  name: string
  author: string
  authorAvatar?: string
  description: string
  longDescription: string
  tags: string[]
  downloads: number
  stars: number
  views: number
  isStarred: boolean
  lastUpdated: string
  createdAt: string
  size: string
  license: string
  framework: string
  task: string
  language: string[]
  files: {
    name: string
    size: string
    type: string
    url: string
  }[]
  versions: {
    version: string
    date: string
    description: string
  }[]
  usageCode: {
    python: string
    javascript?: string
  }
}

const ModelDetailPage = () => {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const [model, setModel] = useState<ModelDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [isStarred, setIsStarred] = useState(false)
  const [starCount, setStarCount] = useState(0)
  const [downloadModalVisible, setDownloadModalVisible] = useState(false)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [downloadProgress, setDownloadProgress] = useState(0)
  const [downloadingFile, setDownloadingFile] = useState(false)

  useEffect(() => {
    const fetchModelDetail = async () => {
      try {
        setLoading(true)
        const response = await api.get(`/models/${id}`)
        setModel(response.data)
        setIsStarred(response.data.isStarred)
        setStarCount(response.data.stars)

        // 记录查看次数
        if (id) {
          await api.post(`/models/${id}/view`)
        }
      } catch (error) {
        console.error("Error fetching model details:", error)
        message.error("获取模型详情失败")
      } finally {
        setLoading(false)
      }
    }

    if (id) {
      fetchModelDetail()
    }
  }, [id])

  const handleStarToggle = async () => {
    if (!user) {
      message.warning("请先登录")
      return
    }

    try {
      if (isStarred) {
        await api.delete(`/models/${id}/star`)
        setIsStarred(false)
        setStarCount((prev) => prev - 1)
        message.success("已取消收藏")
      } else {
        await api.post(`/models/${id}/star`)
        setIsStarred(true)
        setStarCount((prev) => prev + 1)
        message.success("已收藏")
      }
    } catch (error) {
      console.error("Error toggling star:", error)
      message.error("操作失败，请稍后再试")
    }
  }

  const showDownloadModal = () => {
    setDownloadModalVisible(true)
  }

  const handleDownload = async (fileUrl: string, fileName: string) => {
    setSelectedFile(fileName)
    setDownloadingFile(true)
    setDownloadProgress(0)

    try {
      // 模拟下载进度
      const interval = setInterval(() => {
        setDownloadProgress((prev) => {
          if (prev >= 95) {
            clearInterval(interval)
            return 95
          }
          return prev + Math.floor(Math.random() * 10)
        })
      }, 300)

      // 实际下载逻辑
      await api.post(`/models/${id}/download`, { fileName })

      // 完成下载
      clearInterval(interval)
      setDownloadProgress(100)

      setTimeout(() => {
        message.success(`${fileName} 下载完成`)
        setDownloadingFile(false)
        setDownloadModalVisible(false)
        setSelectedFile(null)
        setDownloadProgress(0)
      }, 500)
    } catch (error) {
      console.error("Error downloading file:", error)
      message.error("下载失败，请稍后再试")
      setDownloadingFile(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard
      .writeText(text)
      .then(() => message.success("已复制到剪贴板"))
      .catch(() => message.error("复制失败"))
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spin size="large" />
      </div>
    )
  }

  if (!model) {
    return (
      <div className="text-center py-12">
        <Title level={3}>模型不存在或已被删除</Title>
        <Button type="primary" className="mt-4">
          <Link to="/models">返回模型库</Link>
        </Button>
      </div>
    )
  }

  return (
    <div>
      <Breadcrumb className="mb-4">
        <Breadcrumb.Item>
          <Link to="/">首页</Link>
        </Breadcrumb.Item>
        <Breadcrumb.Item>
          <Link to="/models">模型库</Link>
        </Breadcrumb.Item>
        <Breadcrumb.Item>{model.name}</Breadcrumb.Item>
      </Breadcrumb>

      <div className="flex flex-col md:flex-row justify-between mb-6 gap-4">
        <div>
          <Title level={2} className="mb-2">
            {model.name}
          </Title>
          <div className="flex items-center mb-4">
            <Link to={`/profile/${model.author}`} className="flex items-center mr-4">
              <img
                src={model.authorAvatar || "/placeholder.svg?height=24&width=24"}
                alt={model.author}
                className="w-6 h-6 rounded-full mr-2"
              />
              <Text className="text-gray-600">@{model.author}</Text>
            </Link>
            <Text className="text-gray-500">
              <HistoryOutlined className="mr-1" />
              更新于 {new Date(model.lastUpdated).toLocaleDateString("zh-CN")}
            </Text>
          </div>
          <div className="mb-4">
            {model.tags.map((tag) => (
              <Tag key={tag} color="blue" className="mr-2 mb-2">
                {tag}
              </Tag>
            ))}
          </div>
          <Paragraph className="text-gray-700">{model.description}</Paragraph>
        </div>

        <div className="flex flex-col gap-4">
          <Button
            type="primary"
            size="large"
            icon={<DownloadOutlined />}
            onClick={showDownloadModal}
            className="min-w-[180px]"
          >
            下载模型
          </Button>

          <Button
            size="large"
            icon={isStarred ? <StarFilled className="text-yellow-500" /> : <StarOutlined />}
            onClick={handleStarToggle}
          >
            {isStarred ? "已收藏" : "收藏"}
          </Button>

          <Button
            size="large"
            icon={<ShareAltOutlined />}
            onClick={() => {
              copyToClipboard(window.location.href)
              message.success("链接已复制到剪贴板")
            }}
          >
            分享
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <Card>
          <Statistic title="下载量" value={model.downloads} prefix={<DownloadOutlined />} />
        </Card>
        <Card>
          <Statistic title="收藏数" value={starCount} prefix={<StarOutlined />} />
        </Card>
        <Card>
          <Statistic title="浏览量" value={model.views} prefix={<EyeOutlined />} />
        </Card>
        <Card>
          <Statistic
            title="文件大小"
            value={model.size}
            prefix={<FileTextOutlined />}
            valueStyle={{ fontSize: "1.2rem" }}
          />
        </Card>
      </div>

      <Tabs defaultActiveKey="overview" className="mb-8">
        <TabPane tab="概览" key="overview">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2">
              <Card title="模型描述" className="mb-6">
                <div className="prose max-w-none">
                  <ReactMarkdown>{model.longDescription}</ReactMarkdown>
                </div>
              </Card>

              <Card title="使用方法" className="mb-6">
                <Tabs defaultActiveKey="python">
                  <TabPane tab="Python" key="python">
                    <div className="relative">
                      <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
                        <code>{model.usageCode.python}</code>
                      </pre>
                      <Button
                        icon={<CopyOutlined />}
                        className="absolute top-2 right-2"
                        onClick={() => copyToClipboard(model.usageCode.python)}
                      />
                    </div>
                  </TabPane>
                  {model.usageCode.javascript && (
                    <TabPane tab="JavaScript" key="javascript">
                      <div className="relative">
                        <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
                          <code>{model.usageCode.javascript}</code>
                        </pre>
                        <Button
                          icon={<CopyOutlined />}
                          className="absolute top-2 right-2"
                          onClick={() => copyToClipboard(model.usageCode.javascript)}
                        />
                      </div>
                    </TabPane>
                  )}
                </Tabs>
              </Card>
            </div>

            <div>
              <Card title="模型信息" className="mb-6">
                <Descriptions column={1} bordered size="small">
                  <Descriptions.Item label="任务类型">{model.task}</Descriptions.Item>
                  <Descriptions.Item label="框架">{model.framework}</Descriptions.Item>
                  <Descriptions.Item label="语言">
                    {model.language.map((lang) => (
                      <Tag key={lang} className="mr-1">
                        {lang}
                      </Tag>
                    ))}
                  </Descriptions.Item>
                  <Descriptions.Item label="许可证">
                    <Tooltip title="点击查看许可证详情">
                      <Link to={`/licenses/${model.license}`} className="flex items-center">
                        {model.license} <QuestionCircleOutlined className="ml-1" />
                      </Link>
                    </Tooltip>
                  </Descriptions.Item>
                  <Descriptions.Item label="创建时间">
                    {new Date(model.createdAt).toLocaleDateString("zh-CN")}
                  </Descriptions.Item>
                  <Descriptions.Item label="最后更新">
                    {new Date(model.lastUpdated).toLocaleDateString("zh-CN")}
                  </Descriptions.Item>
                </Descriptions>
              </Card>

              <Card title="文件列表" className="mb-6">
                <ul className="divide-y">
                  {model.files.map((file) => (
                    <li key={file.name} className="py-2">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center">
                          <FileTextOutlined className="mr-2 text-gray-500" />
                          <Text ellipsis className="max-w-[150px]">
                            {file.name}
                          </Text>
                        </div>
                        <Text className="text-gray-500">{file.size}</Text>
                      </div>
                    </li>
                  ))}
                </ul>
              </Card>
            </div>
          </div>
        </TabPane>

        <TabPane tab="版本历史" key="versions">
          <Card>
            <ul className="divide-y">
              {model.versions.map((version, index) => (
                <li key={index} className="py-4">
                  <div className="flex items-start">
                    <div className="flex-shrink-0 mr-4">
                      <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <Text className="text-blue-600 font-medium">{version.version}</Text>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center mb-1">
                        <Text strong>{`版本 ${version.version}`}</Text>
                        <Text type="secondary" className="ml-2">
                          {new Date(version.date).toLocaleDateString("zh-CN")}
                        </Text>
                      </div>
                      <Paragraph className="text-gray-700">{version.description}</Paragraph>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </Card>
        </TabPane>
      </Tabs>

      <Modal
        title="下载模型文件"
        open={downloadModalVisible}
        onCancel={() => {
          if (!downloadingFile) {
            setDownloadModalVisible(false)
          }
        }}
        footer={null}
      >
        <div className="py-2">
          <Paragraph>请选择要下载的文件:</Paragraph>
          <ul className="divide-y">
            {model.files.map((file) => (
              <li key={file.name} className="py-3">
                <div className="flex justify-between items-center">
                  <div className="flex items-center">
                    <FileTextOutlined className="mr-2 text-gray-500" />
                    <div>
                      <Text strong>{file.name}</Text>
                      <div>
                        <Text type="secondary">
                          {file.size} · {file.type}
                        </Text>
                      </div>
                    </div>
                  </div>
                  <Button
                    type="primary"
                    icon={<DownloadOutlined />}
                    loading={downloadingFile && selectedFile === file.name}
                    onClick={() => handleDownload(file.url, file.name)}
                  >
                    下载
                  </Button>
                </div>
                {downloadingFile && selectedFile === file.name && (
                  <div className="mt-2">
                    <div className="bg-gray-200 rounded-full h-2 mt-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${downloadProgress}%` }}></div>
                    </div>
                    <div className="text-right mt-1">
                      <Text type="secondary">{downloadProgress}%</Text>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      </Modal>
    </div>
  )
}

export default ModelDetailPage
