'use client'

import { useState, useEffect } from 'react'
import { 
  Page, 
  Layout, 
  Card, 
  DataTable, 
  Button, 
  Stack, 
  Heading, 
  Text,
  Badge,
  Modal,
  TextField,
  Select,
  ProgressBar,
  Frame,
  Navigation,
  TopBar,
  Icon,
  Thumbnail,
  ButtonGroup
} from '@shopify/polaris'
import { 
  PlusIcon, 
  ExternalLinkIcon,
  SettingsIcon,
  ChartBarIcon,
  StoreIcon
} from 'lucide-react'

interface Store {
  id: number
  name: string
  status: 'generating' | 'completed' | 'published' | 'error'
  progress: number
  createdAt: string
  sourceUrl: string
  shopifyUrl?: string
  thumbnail?: string
}

export default function DashboardPage() {
  const [stores, setStores] = useState<Store[]>([])
  const [showNewStoreModal, setShowNewStoreModal] = useState(false)
  const [newStoreData, setNewStoreData] = useState({
    productUrl: '',
    storeName: '',
    themeStyle: 'modern'
  })
  const [isGenerating, setIsGenerating] = useState(false)

  // Mock data for demonstration
  useEffect(() => {
    setStores([
      {
        id: 1,
        name: 'Premium Wireless Headphones Store',
        status: 'published',
        progress: 100,
        createdAt: '2024-01-15',
        sourceUrl: 'https://aliexpress.com/item/wireless-headphones',
        shopifyUrl: 'https://premium-audio-store.myshopify.com',
        thumbnail: '/api/placeholder/150/150'
      },
      {
        id: 2,
        name: 'Smart Fitness Tracker Shop',
        status: 'generating',
        progress: 65,
        createdAt: '2024-01-16',
        sourceUrl: 'https://amazon.com/fitness-tracker',
      },
      {
        id: 3,
        name: 'Luxury Watch Collection',
        status: 'completed',
        progress: 100,
        createdAt: '2024-01-14',
        sourceUrl: 'https://ebay.com/luxury-watch',
      }
    ])
  }, [])

  const handleCreateStore = async () => {
    setIsGenerating(true)
    try {
      // API call would go here
      const newStore: Store = {
        id: Date.now(),
        name: newStoreData.storeName,
        status: 'generating',
        progress: 0,
        createdAt: new Date().toISOString().split('T')[0],
        sourceUrl: newStoreData.productUrl
      }
      
      setStores(prev => [newStore, ...prev])
      setShowNewStoreModal(false)
      setNewStoreData({ productUrl: '', storeName: '', themeStyle: 'modern' })
      
      // Simulate progress updates
      simulateProgress(newStore.id)
    } catch (error) {
      console.error('Failed to create store:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const simulateProgress = (storeId: number) => {
    const intervals = [
      { progress: 20, delay: 2000, message: 'Scraping product data...' },
      { progress: 50, delay: 4000, message: 'Generating AI content...' },
      { progress: 80, delay: 6000, message: 'Enhancing images...' },
      { progress: 100, delay: 8000, message: 'Store completed!' }
    ]

    intervals.forEach(({ progress, delay }) => {
      setTimeout(() => {
        setStores(prev => prev.map(store => 
          store.id === storeId 
            ? { ...store, progress, status: progress === 100 ? 'completed' : 'generating' }
            : store
        ))
      }, delay)
    })
  }

  const getStatusBadge = (status: Store['status']) => {
    switch (status) {
      case 'generating':
        return <Badge status="attention">Generating</Badge>
      case 'completed':
        return <Badge status="success">Completed</Badge>
      case 'published':
        return <Badge status="info">Published</Badge>
      case 'error':
        return <Badge status="critical">Error</Badge>
      default:
        return <Badge>Unknown</Badge>
    }
  }

  const tableRows = stores.map(store => [
    <Stack spacing="tight" key={store.id}>
      {store.thumbnail && (
        <Thumbnail
          source={store.thumbnail}
          alt={store.name}
          size="small"
        />
      )}
      <div>
        <Text variant="bodyMd" fontWeight="bold" as="p">{store.name}</Text>
        <Text variant="bodySm" color="subdued" as="p">
          Created {new Date(store.createdAt).toLocaleDateString()}
        </Text>
      </div>
    </Stack>,
    getStatusBadge(store.status),
    store.status === 'generating' ? (
      <div style={{ width: '120px' }}>
        <ProgressBar progress={store.progress} size="small" />
        <Text variant="bodySm" color="subdued" as="p">{store.progress}%</Text>
      </div>
    ) : (
      <Text variant="bodyMd" as="p">—</Text>
    ),
    <ButtonGroup>
      <Button size="slim" outline>Preview</Button>
      {store.status === 'completed' && (
        <Button size="slim" primary>Publish</Button>
      )}
      {store.shopifyUrl && (
        <Button 
          size="slim" 
          external 
          url={store.shopifyUrl}
          icon={ExternalLinkIcon}
        >
          View Store
        </Button>
      )}
    </ButtonGroup>
  ])

  const navigationMarkup = (
    <Navigation location="/">
      <Navigation.Section
        items={[
          {
            url: '/dashboard',
            label: 'Dashboard',
            icon: ChartBarIcon,
            selected: true,
          },
          {
            url: '/stores',
            label: 'My Stores',
            icon: StoreIcon,
          },
          {
            url: '/settings',
            label: 'Settings',
            icon: SettingsIcon,
          },
        ]}
      />
    </Navigation>
  )

  const topBarMarkup = (
    <TopBar
      showNavigationToggle
      userMenu={
        <div className="p-4">
          <Stack spacing="tight">
            <Text variant="bodyMd" fontWeight="bold" as="p">StoreForge Account</Text>
            <Text variant="bodySm" color="subdued" as="p">Pro Plan • 7/10 stores used</Text>
          </Stack>
        </div>
      }
    />
  )

  return (
    <Frame navigation={navigationMarkup} topBar={topBarMarkup}>
      <Page
        title="Dashboard"
        primaryAction={{
          content: 'New Store',
          icon: PlusIcon,
          onAction: () => setShowNewStoreModal(true)
        }}
      >
        <Layout>
          <Layout.Section>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <Card sectioned>
                <Stack spacing="tight">
                  <Text variant="bodyMd" color="subdued" as="p">Stores Created</Text>
                  <Text variant="headingLg" as="p">12</Text>
                  <Text variant="bodySm" color="success" as="p">+3 this month</Text>
                </Stack>
              </Card>
              
              <Card sectioned>
                <Stack spacing="tight">
                  <Text variant="bodyMd" color="subdued" as="p">Published Stores</Text>
                  <Text variant="headingLg" as="p">8</Text>
                  <Text variant="bodySm" color="success" as="p">+2 this month</Text>
                </Stack>
              </Card>
              
              <Card sectioned>
                <Stack spacing="tight">
                  <Text variant="bodyMd" color="subdued" as="p">Monthly Limit</Text>
                  <Text variant="headingLg" as="p">7/10</Text>
                  <Text variant="bodySm" color="subdued" as="p">3 remaining</Text>
                </Stack>
              </Card>
              
              <Card sectioned>
                <Stack spacing="tight">
                  <Text variant="bodyMd" color="subdued" as="p">Success Rate</Text>
                  <Text variant="headingLg" as="p">94%</Text>
                  <Text variant="bodySm" color="success" as="p">Above average</Text>
                </Stack>
              </Card>
            </div>

            {/* Stores Table */}
            <Card>
              <div className="p-6 border-b border-gray-200">
                <Stack distribution="equalSpacing" alignment="center">
                  <Heading element="h2">Recent Stores</Heading>
                  <Button 
                    primary 
                    icon={PlusIcon}
                    onClick={() => setShowNewStoreModal(true)}
                  >
                    Create Store
                  </Button>
                </Stack>
              </div>
              
              <DataTable
                columnContentTypes={['text', 'text', 'text', 'text']}
                headings={['Store', 'Status', 'Progress', 'Actions']}
                rows={tableRows}
              />
            </Card>
          </Layout.Section>

          <Layout.Section secondary>
            {/* Quick Actions */}
            <Card title="Quick Actions" sectioned>
              <Stack spacing="loose">
                <Button 
                  fullWidth 
                  primary 
                  icon={PlusIcon}
                  onClick={() => setShowNewStoreModal(true)}
                >
                  Create New Store
                </Button>
                <Button fullWidth outline>
                  Import from CSV
                </Button>
                <Button fullWidth outline>
                  View Analytics
                </Button>
              </Stack>
            </Card>

            {/* Plan Usage */}
            <Card title="Plan Usage" sectioned>
              <Stack spacing="loose">
                <div>
                  <Text variant="bodyMd" as="p">Stores this month</Text>
                  <ProgressBar progress={70} />
                  <Text variant="bodySm" color="subdued" as="p">7 of 10 used</Text>
                </div>
                <Button outline fullWidth>
                  Upgrade Plan
                </Button>
              </Stack>
            </Card>

            {/* Recent Activity */}
            <Card title="Recent Activity" sectioned>
              <Stack spacing="loose">
                <Stack spacing="tight">
                  <Text variant="bodyMd" fontWeight="bold" as="p">Store Published</Text>
                  <Text variant="bodySm" color="subdued" as="p">
                    Premium Wireless Headphones Store went live
                  </Text>
                  <Text variant="bodySm" color="subdued" as="p">2 hours ago</Text>
                </Stack>
                
                <Stack spacing="tight">
                  <Text variant="bodyMd" fontWeight="bold" as="p">Store Generated</Text>
                  <Text variant="bodySm" color="subdued" as="p">
                    Smart Fitness Tracker Shop completed generation
                  </Text>
                  <Text variant="bodySm" color="subdued" as="p">1 day ago</Text>
                </Stack>
              </Stack>
            </Card>
          </Layout.Section>
        </Layout>

        {/* New Store Modal */}
        <Modal
          open={showNewStoreModal}
          onClose={() => setShowNewStoreModal(false)}
          title="Create New Store"
          primaryAction={{
            content: 'Generate Store',
            onAction: handleCreateStore,
            loading: isGenerating,
            disabled: !newStoreData.productUrl || !newStoreData.storeName
          }}
          secondaryActions={[
            {
              content: 'Cancel',
              onAction: () => setShowNewStoreModal(false)
            }
          ]}
        >
          <Modal.Section>
            <Stack spacing="loose">
              <TextField
                label="Product URL"
                placeholder="https://aliexpress.com/item/..."
                value={newStoreData.productUrl}
                onChange={(value) => setNewStoreData(prev => ({ ...prev, productUrl: value }))}
                helpText="Paste any product URL from AliExpress, Amazon, eBay, etc."
              />
              
              <TextField
                label="Store Name"
                placeholder="My Awesome Store"
                value={newStoreData.storeName}
                onChange={(value) => setNewStoreData(prev => ({ ...prev, storeName: value }))}
                helpText="Choose a name for your store"
              />
              
              <Select
                label="Theme Style"
                options={[
                  { label: 'Modern', value: 'modern' },
                  { label: 'Luxury', value: 'luxury' },
                  { label: 'Minimal', value: 'minimal' }
                ]}
                value={newStoreData.themeStyle}
                onChange={(value) => setNewStoreData(prev => ({ ...prev, themeStyle: value }))}
              />
            </Stack>
          </Modal.Section>
        </Modal>
      </Page>
    </Frame>
  )
}