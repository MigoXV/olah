"use client"

import { useState, useEffect } from "react"
import { Typography, Input, Select, Card, List, Tag, Pagination, Spin, Empty, Button, Checkbox, Divider } from "antd"
import { SearchOutlined, FilterOutlined, DownloadOutlined, StarOutlined } from "@ant-design/icons"
import { Link } from "react-router-dom"
import { api } from "../utils/api"

const { Title, Paragraph } = Typography
const { Search } = Input
const { Option } = Select
const { CheckboxGroup } = Checkbox

interface Dataset {
  id: string
  name: string
  author: string
  downloads: number
  stars: number
  tags: string[]
  description: string
  lastUpdated: string
  size: string
  license: string
  sampleCount: number
}

const taskOptions = [
  "文本分类",
  "命名实体识别",
  "问答系统",
  "机器翻译",
  "情感分析",
  "图像分类",
  "目标检测",
  "语音识别",
  "语音合成",
]

const languageOptions = [
  "中文",
  "英文",
  "多语言",
  "日语",
  "韩语",
  "法语",
  "德语",
  "俄语",
  "西班牙语",
  "葡萄牙语",
  "阿拉伯语",
]

const DatasetsPage = () => {
  const [loading, setLoading] = useState(true)
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(12)
  const [searchQuery, setSearchQuery] = useState("")
  const [sortBy, setSortBy] = useState("downloads")
  const [selectedTasks, setSelectedTasks] = useState<string[]>([])
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>([])
  const [filterVisible, setFilterVisible] = useState(false)

  useEffect(() => {
    fetchDatasets()
  }, [page, pageSize, searchQuery, sortBy, selectedTasks, selectedLanguages])

  const fetchDatasets = async () => {
    try {
      setLoading(true)
      const params = {
        page,
        limit: pageSize,
        q: searchQuery,
        sort: sortBy,
        tasks: selectedTasks.join(","),
        languages: selectedLanguages.join(","),
      }

      const response = await api.get("/datasets", { params })
      if (response.data.datasets && response.data.datasets.length > 0) {
        setDatasets(response.data.datasets)
        setTotal(response.data.total)
      } else {
        setDatasets([])
        setTotal(0)
      }
    } catch (error) {
      console.error("Error fetching datasets:", error)
      setDatasets([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (value: string) => {
    setSearchQuery(value)
    setPage(1)
  }

  const handleSortChange = (value: string) => {
    setSortBy(value)
    setPage(1)
  }

  const handleTaskChange = (checkedValues: string[]) => {
    setSelectedTasks(checkedValues)
    setPage(1)
  }

  const handleLanguageChange = (checkedValues: string[]) => {
    setSelectedLanguages(checkedValues)
    setPage(1)
  }

  const toggleFilters = () => {
    setFilterVisible(!filterVisible)
  }

  const clearFilters = () => {
    setSelectedTasks([])
    setSelectedLanguages([])
    setSortBy("downloads")
    setSearchQuery("")
    setPage(1)
  }

  return (
    <div>
      <div className="mb-6">
        <Title level={2}>数据集库</Title>
        <Paragraph className="text-gray-600">浏览和下载各种 AI 数据集，加速您的模型训练</Paragraph>
      </div>

      <div className="flex flex-wrap items-center mb-6 gap-4">
        <Search
          placeholder="搜索数据集名称、描述或作者"
          allowClear
          enterButton={<SearchOutlined />}
          size="large"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onSearch={handleSearch}
          className="flex-1 min-w-[300px]"
        />

        <Select placeholder="排序方式" style={{ width: 150 }} value={sortBy} onChange={handleSortChange} size="large">
          <Option value="downloads">下载量</Option>
          <Option value="stars">收藏数</Option>
          <Option value="newest">最新发布</Option>
          <Option value="oldest">最早发布</Option>
          <Option value="samples">样本数量</Option>
        </Select>

        <Button
          type={filterVisible ? "primary" : "default"}
          icon={<FilterOutlined />}
          onClick={toggleFilters}
          size="large"
        >
          筛选
        </Button>
      </div>

      {filterVisible && (
        <Card className="mb-6">
          <div className="flex justify-between mb-4">
            <Title level={4}>筛选条件</Title>
            <Button type="link" onClick={clearFilters}>
              清除所有筛选
            </Button>
          </div>

          <div className="mb-4">
            <Title level={5}>任务类型</Title>
            <CheckboxGroup
              options={taskOptions}
              value={selectedTasks}
              onChange={handleTaskChange}
              className="flex flex-wrap gap-x-8 gap-y-2"
            />
          </div>

          <Divider />

          <div>
            <Title level={5}>语言</Title>
            <CheckboxGroup
              options={languageOptions}
              value={selectedLanguages}
              onChange={handleLanguageChange}
              className="flex flex-wrap gap-x-8 gap-y-2"
            />
          </div>
        </Card>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <Spin size="large" />
        </div>
      ) : datasets.length > 0 ? (
        <>
          <List
            grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 3, xl: 4, xxl: 4 }}
            dataSource={datasets}
            renderItem={(dataset) => (
              <List.Item>
                <Card hoverable className="h-full flex flex-col">
                  <div className="flex-1">
                    <Link
                      to={`/datasets/${dataset.id}`}
                      className="text-lg font-medium text-blue-600 hover:text-blue-800"
                    >
                      {dataset.name}
                    </Link>
                    <div className="mb-2 text-sm">
                      <Link to={`/profile/${dataset.author}`} className="text-gray-600">
                        @{dataset.author}
                      </Link>
                    </div>
                    <Paragraph ellipsis={{ rows: 3 }} className="text-gray-700 mb-3">
                      {dataset.description}
                    </Paragraph>
                  </div>

                  <div>
                    <div className="mb-3">
                      {dataset.tags.slice(0, 3).map((tag) => (
                        <Tag key={tag} color="green" className="mr-1 mb-1">
                          {tag}
                        </Tag>
                      ))}
                      {dataset.tags.length > 3 && <Tag>+{dataset.tags.length - 3}</Tag>}
                    </div>

                    <div className="flex justify-between text-sm text-gray-500">
                      <div>
                        <span className="mr-3">
                          <DownloadOutlined className="mr-1" />
                          {dataset.downloads.toLocaleString()}
                        </span>
                        <span>
                          <StarOutlined className="mr-1" />
                          {dataset.stars.toLocaleString()}
                        </span>
                      </div>
                      <div>
                        {dataset.sampleCount.toLocaleString()} 样本 · {dataset.size}
                      </div>
                    </div>
                  </div>
                </Card>
              </List.Item>
            )}
          />

          <div className="flex justify-center mt-8">
            <Pagination
              current={page}
              pageSize={pageSize}
              total={total}
              onChange={(p, ps) => {
                setPage(p)
                setPageSize(ps)
              }}
              showSizeChanger
              showQuickJumper
              showTotal={(total) => `共 ${total} 个数据集`}
            />
          </div>
        </>
      ) : (
        <Empty description="没有找到符合条件的数据集" image={Empty.PRESENTED_IMAGE_SIMPLE} className="py-12" />
      )}
    </div>
  )
}

export default DatasetsPage
