"use client"

import { useState, useEffect } from "react"
import { useParams } from "react-router-dom"
import { Typography, Tabs, Card, Avatar, Button, Statistic, List, Tag, Spin, Empty, Divider, message } from "antd"
import {
  UserOutlined,
  MailOutlined,
  GithubOutlined,
  GlobalOutlined,
  StarOutlined,
  DownloadOutlined,
  AppstoreOutlined,
  DatabaseOutlined,
} from "@ant-design/icons"
import { Link } from "react-router-dom"
import { api } from "../utils/api"
import { useAuth } from "../contexts/AuthContext"

const { Title, Paragraph, Text } = Typography
const { TabPane } = Tabs

interface UserProfile {
  username: string
  name: string
  avatar?: string
  bio: string
  email?: string
  website?: string
  github?: string
  joinDate: string
  followers: number
  following: number
  isFollowing: boolean
  isCurrentUser: boolean
  stats: {
    models: number
    datasets: number
    downloads: number
    stars: number
  }
}

interface Model {
  id: string
  name: string
  description: string
  tags: string[]
  downloads: number
  stars: number
}

interface Dataset {
  id: string
  name: string
  description: string
  tags: string[]
  downloads: number
  stars: number
  sampleCount: number
}

const UserProfilePage = () => {
  const { username } = useParams<{ username: string }>()
  const { user } = useAuth()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [models, setModels] = useState<Model[]>([])
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [loading, setLoading] = useState(true)
  const [isFollowing, setIsFollowing] = useState(false)
  const [followerCount, setFollowerCount] = useState(0)

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        setLoading(true)
        const [profileRes, modelsRes, datasetsRes] = await Promise.all([
          api.get(`/users/${username}`),
          api.get(`/users/${username}/models`),
          api.get(`/users/${username}/datasets`),
        ])

        setProfile(profileRes.data)
        setModels(modelsRes.data)
        setDatasets(datasetsRes.data)
        setIsFollowing(profileRes.data.isFollowing)
        setFollowerCount(profileRes.data.followers)
      } catch (error) {
        console.error("Error fetching user profile:", error)
        message.error("获取用户资料失败")
      } finally {
        setLoading(false)
      }
    }

    if (username) {
      fetchUserProfile()
    }
  }, [username])

  const handleFollowToggle = async () => {
    if (!user) {
      message.warning("请先登录")
      return
    }

    try {
      if (isFollowing) {
        await api.delete(`/users/${username}/follow`)
        setIsFollowing(false)
        setFollowerCount((prev) => prev - 1)
        message.success(`已取消关注 ${username}`)
      } else {
        await api.post(`/users/${username}/follow`)
        setIsFollowing(true)
        setFollowerCount((prev) => prev + 1)
        message.success(`已关注 ${username}`)
      }
    } catch (error) {
      console.error("Error toggling follow:", error)
      message.error("操作失败，请稍后再试")
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spin size="large" />
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <Title level={3}>用户不存在</Title>
        <Button type="primary" className="mt-4">
          <Link to="/">返回首页</Link>
        </Button>
      </div>
    )
  }

  return (
    <div>
      <div className="flex flex-col md:flex-row gap-6 mb-8">
        <div className="md:w-1/4">
          <Card className="text-center">
            <Avatar src={profile.avatar} icon={<UserOutlined />} size={100} className="mb-4" />
            <Title level={3}>{profile.name || profile.username}</Title>
            <Text type="secondary" className="block mb-4">
              @{profile.username}
            </Text>

            {!profile.isCurrentUser && (
              <Button type={isFollowing ? "default" : "primary"} onClick={handleFollowToggle} className="mb-4 w-full">
                {isFollowing ? "已关注" : "关注"}
              </Button>
            )}

            <Paragraph className="text-gray-700 mb-4">{profile.bio || "这个用户很懒，还没有填写个人简介"}</Paragraph>

            <div className="flex justify-center space-x-8 mb-4">
              <div className="text-center">
                <div className="text-lg font-bold">{followerCount}</div>
                <div className="text-gray-500">粉丝</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold">{profile.following}</div>
                <div className="text-gray-500">关注</div>
              </div>
            </div>

            <Divider />

            <div className="text-left">
              <div className="flex items-center mb-2">
                <MailOutlined className="mr-2 text-gray-500" />
                {profile.email ? (
                  <a href={`mailto:${profile.email}`} className="text-gray-700">
                    {profile.email}
                  </a>
                ) : (
                  <Text type="secondary">未提供邮箱</Text>
                )}
              </div>

              <div className="flex items-center mb-2">
                <GlobalOutlined className="mr-2 text-gray-500" />
                {profile.website ? (
                  <a href={profile.website} target="_blank" rel="noopener noreferrer" className="text-gray-700">
                    {profile.website.replace(/^https?:\/\//, "")}
                  </a>
                ) : (
                  <Text type="secondary">未提供网站</Text>
                )}
              </div>

              <div className="flex items-center mb-2">
                <GithubOutlined className="mr-2 text-gray-500" />
                {profile.github ? (
                  <a
                    href={`https://github.com/${profile.github}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-700"
                  >
                    {profile.github}
                  </a>
                ) : (
                  <Text type="secondary">未提供 GitHub</Text>
                )}
              </div>

              <div className="flex items-center">
                <UserOutlined className="mr-2 text-gray-500" />
                <Text className="text-gray-700">加入于 {new Date(profile.joinDate).toLocaleDateString("zh-CN")}</Text>
              </div>
            </div>
          </Card>
        </div>

        <div className="md:w-3/4">
          <Card className="mb-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Statistic title="模型数量" value={profile.stats.models} prefix={<AppstoreOutlined />} />
              <Statistic title="数据集数量" value={profile.stats.datasets} prefix={<DatabaseOutlined />} />
              <Statistic title="总下载量" value={profile.stats.downloads} prefix={<DownloadOutlined />} />
              <Statistic title="总收藏数" value={profile.stats.stars} prefix={<StarOutlined />} />
            </div>
          </Card>

          <Card>
            <Tabs defaultActiveKey="models">
              <TabPane
                tab={
                  <span>
                    <AppstoreOutlined /> 模型 ({profile.stats.models})
                  </span>
                }
                key="models"
              >
                {models.length > 0 ? (
                  <List
                    itemLayout="vertical"
                    dataSource={models}
                    renderItem={(model) => (
                      <List.Item
                        key={model.id}
                        extra={
                          <div className="text-right">
                            <div className="flex items-center justify-end mb-2">
                              <DownloadOutlined className="mr-1" />
                              <span>{model.downloads.toLocaleString()}</span>
                            </div>
                            <div className="flex items-center justify-end">
                              <StarOutlined className="mr-1" />
                              <span>{model.stars.toLocaleString()}</span>
                            </div>
                          </div>
                        }
                      >
                        <List.Item.Meta
                          title={
                            <Link
                              to={`/models/${model.id}`}
                              className="text-lg font-medium text-blue-600 hover:text-blue-800"
                            >
                              {model.name}
                            </Link>
                          }
                          description={
                            <div>
                              {model.tags.map((tag) => (
                                <Tag key={tag} color="blue" className="mr-1 mb-1">
                                  {tag}
                                </Tag>
                              ))}
                            </div>
                          }
                        />
                        <Paragraph ellipsis={{ rows: 2 }} className="text-gray-700">
                          {model.description}
                        </Paragraph>
                      </List.Item>
                    )}
                  />
                ) : (
                  <Empty description="暂无模型" />
                )}
              </TabPane>

              <TabPane
                tab={
                  <span>
                    <DatabaseOutlined /> 数据集 ({profile.stats.datasets})
                  </span>
                }
                key="datasets"
              >
                {datasets.length > 0 ? (
                  <List
                    itemLayout="vertical"
                    dataSource={datasets}
                    renderItem={(dataset) => (
                      <List.Item
                        key={dataset.id}
                        extra={
                          <div className="text-right">
                            <div className="flex items-center justify-end mb-2">
                              <DownloadOutlined className="mr-1" />
                              <span>{dataset.downloads.toLocaleString()}</span>
                            </div>
                            <div className="flex items-center justify-end">
                              <StarOutlined className="mr-1" />
                              <span>{dataset.stars.toLocaleString()}</span>
                            </div>
                          </div>
                        }
                      >
                        <List.Item.Meta
                          title={
                            <Link
                              to={`/datasets/${dataset.id}`}
                              className="text-lg font-medium text-blue-600 hover:text-blue-800"
                            >
                              {dataset.name}
                            </Link>
                          }
                          description={
                            <div>
                              {dataset.tags.map((tag) => (
                                <Tag key={tag} color="green" className="mr-1 mb-1">
                                  {tag}
                                </Tag>
                              ))}
                            </div>
                          }
                        />
                        <Paragraph ellipsis={{ rows: 2 }} className="text-gray-700">
                          {dataset.description}
                        </Paragraph>
                        <div className="text-gray-500">{dataset.sampleCount.toLocaleString()} 样本</div>
                      </List.Item>
                    )}
                  />
                ) : (
                  <Empty description="暂无数据集" />
                )}
              </TabPane>
            </Tabs>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default UserProfilePage
