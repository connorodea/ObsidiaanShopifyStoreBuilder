'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Page, 
  Layout, 
  Card, 
  TextField, 
  Button, 
  Stack, 
  Heading, 
  Text,
  Banner,
  Badge,
  Grid,
  Icon,
  Frame,
  TopBar
} from '@shopify/polaris'
import { 
  StarIcon, 
  ClockIcon, 
  ShieldCheckIcon,
  SparklesIcon 
} from 'lucide-react'

export default function HomePage() {
  const [productUrl, setProductUrl] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const router = useRouter()

  const handleGenerateStore = async () => {
    if (!productUrl) return

    setIsGenerating(true)
    try {
      // API call would go here
      await new Promise(resolve => setTimeout(resolve, 2000)) // Demo delay
      router.push('/dashboard')
    } catch (error) {
      console.error('Failed to generate store:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const topBarMarkup = (
    <TopBar
      showNavigationToggle={false}
      userMenu={
        <div className="p-4">
          <Text variant="bodyMd" as="p">Welcome to StoreForge AI</Text>
        </div>
      }
    />
  )

  return (
    <Frame topBar={topBarMarkup}>
      <Page>
        {/* Hero Section */}
        <div className="sf-hero text-white py-20">
          <div className="sf-container text-center">
            <div className="max-w-4xl mx-auto">
              <Heading element="h1" className="text-5xl font-bold mb-6 text-white">
                Build Shopify Stores in Minutes with AI
              </Heading>
              <Text variant="headingLg" as="p" className="text-xl mb-8 opacity-90">
                Transform any product URL into a complete, ready-to-launch Shopify store. 
                AI-powered content generation, enhanced images, and professional themes.
              </Text>
              
              <div className="max-w-2xl mx-auto">
                <Stack spacing="tight">
                  <TextField
                    label=""
                    placeholder="Paste any product URL (AliExpress, Amazon, eBay, etc.)"
                    value={productUrl}
                    onChange={setProductUrl}
                    autoComplete="off"
                    connectedRight={
                      <Button 
                        primary 
                        loading={isGenerating}
                        onClick={handleGenerateStore}
                        disabled={!productUrl}
                      >
                        Generate Store
                      </Button>
                    }
                  />
                </Stack>
                
                <div className="mt-4">
                  <Text variant="bodySm" as="p" className="opacity-75">
                    ✨ Free trial - Generate your first store for free
                  </Text>
                </div>
              </div>
            </div>
          </div>
        </div>

        <Layout>
          <Layout.Section>
            {/* Features Section */}
            <div className="py-16">
              <div className="sf-container">
                <div className="text-center mb-12">
                  <Heading element="h2">Why Choose StoreForge AI?</Heading>
                  <Text variant="bodyLg" as="p" color="subdued" className="mt-4">
                    The most advanced AI-powered Shopify store builder
                  </Text>
                </div>

                <Grid>
                  <Grid.Cell columnSpan={{xs: 6, sm: 3, md: 3, lg: 4, xl: 4}}>
                    <Card sectioned>
                      <Stack spacing="tight">
                        <div className="flex items-center space-x-2">
                          <ClockIcon className="w-6 h-6 text-blue-600" />
                          <Heading element="h3">2-Minute Setup</Heading>
                        </div>
                        <Text variant="bodyMd" as="p">
                          Complete store generation in under 2 minutes. From product URL to 
                          ready-to-launch store faster than any competitor.
                        </Text>
                      </Stack>
                    </Card>
                  </Grid.Cell>

                  <Grid.Cell columnSpan={{xs: 6, sm: 3, md: 3, lg: 4, xl: 4}}>
                    <Card sectioned>
                      <Stack spacing="tight">
                        <div className="flex items-center space-x-2">
                          <SparklesIcon className="w-6 h-6 text-purple-600" />
                          <Heading element="h3">GPT-5 Powered</Heading>
                        </div>
                        <Text variant="bodyMd" as="p">
                          Advanced AI content generation using the latest GPT-5 model. 
                          Superior product descriptions, SEO copy, and page content.
                        </Text>
                      </Stack>
                    </Card>
                  </Grid.Cell>

                  <Grid.Cell columnSpan={{xs: 6, sm: 3, md: 3, lg: 4, xl: 4}}>
                    <Card sectioned>
                      <Stack spacing="tight">
                        <div className="flex items-center space-x-2">
                          <ShieldCheckIcon className="w-6 h-6 text-green-600" />
                          <Heading element="h3">Professional Quality</Heading>
                        </div>
                        <Text variant="bodyMd" as="p">
                          Leonardo AI image enhancement, professional themes, and 
                          conversion-optimized layouts. Ready for high-volume sales.
                        </Text>
                      </Stack>
                    </Card>
                  </Grid.Cell>
                </Grid>
              </div>
            </div>

            {/* Comparison Section */}
            <div className="bg-gray-50 py-16">
              <div className="sf-container">
                <div className="text-center mb-12">
                  <Heading element="h2">StoreForge AI vs Competitors</Heading>
                </div>

                <Card sectioned>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-3 px-4">Feature</th>
                          <th className="text-center py-3 px-4">
                            <Badge status="success">StoreForge AI</Badge>
                          </th>
                          <th className="text-center py-3 px-4">DropshipT</th>
                          <th className="text-center py-3 px-4">Other Apps</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="border-b">
                          <td className="py-3 px-4">AI Model</td>
                          <td className="text-center py-3 px-4">✅ GPT-5</td>
                          <td className="text-center py-3 px-4">❌ GPT-3.5</td>
                          <td className="text-center py-3 px-4">❌ Basic AI</td>
                        </tr>
                        <tr className="border-b">
                          <td className="py-3 px-4">Image Enhancement</td>
                          <td className="text-center py-3 px-4">✅ Leonardo AI</td>
                          <td className="text-center py-3 px-4">❌ Basic</td>
                          <td className="text-center py-3 px-4">❌ None</td>
                        </tr>
                        <tr className="border-b">
                          <td className="py-3 px-4">Generation Speed</td>
                          <td className="text-center py-3 px-4">✅ 2 minutes</td>
                          <td className="text-center py-3 px-4">❌ 5+ minutes</td>
                          <td className="text-center py-3 px-4">❌ 10+ minutes</td>
                        </tr>
                        <tr className="border-b">
                          <td className="py-3 px-4">Free Trial</td>
                          <td className="text-center py-3 px-4">✅ 1 store</td>
                          <td className="text-center py-3 px-4">❌ Preview only</td>
                          <td className="text-center py-3 px-4">❌ No free tier</td>
                        </tr>
                        <tr>
                          <td className="py-3 px-4">CSV Import</td>
                          <td className="text-center py-3 px-4">✅ Yes</td>
                          <td className="text-center py-3 px-4">❌ No</td>
                          <td className="text-center py-3 px-4">❌ Limited</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </Card>
              </div>
            </div>

            {/* Pricing Section */}
            <div className="py-16">
              <div className="sf-container">
                <div className="text-center mb-12">
                  <Heading element="h2">Simple, Transparent Pricing</Heading>
                  <Text variant="bodyLg" as="p" color="subdued" className="mt-4">
                    Choose the plan that fits your business needs
                  </Text>
                </div>

                <Grid>
                  <Grid.Cell columnSpan={{xs: 6, sm: 2, md: 2, lg: 4, xl: 4}}>
                    <Card sectioned>
                      <Stack spacing="loose">
                        <div>
                          <Heading element="h3">Free</Heading>
                          <Text variant="headingXl" as="p" className="mt-2">$0</Text>
                          <Text variant="bodySm" as="p" color="subdued">per month</Text>
                        </div>
                        <Stack spacing="extraTight">
                          <Text variant="bodyMd" as="p">✅ 1 store generation</Text>
                          <Text variant="bodyMd" as="p">✅ AI content generation</Text>
                          <Text variant="bodyMd" as="p">✅ Image enhancement</Text>
                          <Text variant="bodyMd" as="p">✅ Basic themes</Text>
                        </Stack>
                        <Button>Get Started Free</Button>
                      </Stack>
                    </Card>
                  </Grid.Cell>

                  <Grid.Cell columnSpan={{xs: 6, sm: 2, md: 2, lg: 4, xl: 4}}>
                    <Card sectioned>
                      <Stack spacing="loose">
                        <div>
                          <Badge status="info">Most Popular</Badge>
                          <Heading element="h3" className="mt-2">Pro</Heading>
                          <Text variant="headingXl" as="p" className="mt-2">$39</Text>
                          <Text variant="bodySm" as="p" color="subdued">per month</Text>
                        </div>
                        <Stack spacing="extraTight">
                          <Text variant="bodyMd" as="p">✅ 10 stores per month</Text>
                          <Text variant="bodyMd" as="p">✅ Premium AI models</Text>
                          <Text variant="bodyMd" as="p">✅ Advanced image enhancement</Text>
                          <Text variant="bodyMd" as="p">✅ Premium themes</Text>
                          <Text variant="bodyMd" as="p">✅ CSV bulk import</Text>
                          <Text variant="bodyMd" as="p">✅ Priority support</Text>
                        </Stack>
                        <Button primary>Start Pro Trial</Button>
                      </Stack>
                    </Card>
                  </Grid.Cell>

                  <Grid.Cell columnSpan={{xs: 6, sm: 2, md: 2, lg: 4, xl: 4}}>
                    <Card sectioned>
                      <Stack spacing="loose">
                        <div>
                          <Heading element="h3">Agency</Heading>
                          <Text variant="headingXl" as="p" className="mt-2">$99</Text>
                          <Text variant="bodySm" as="p" color="subdued">per month</Text>
                        </div>
                        <Stack spacing="extraTight">
                          <Text variant="bodyMd" as="p">✅ Unlimited stores</Text>
                          <Text variant="bodyMd" as="p">✅ White-label options</Text>
                          <Text variant="bodyMd" as="p">✅ Custom branding</Text>
                          <Text variant="bodyMd" as="p">✅ API access</Text>
                          <Text variant="bodyMd" as="p">✅ Dedicated support</Text>
                          <Text variant="bodyMd" as="p">✅ Team collaboration</Text>
                        </Stack>
                        <Button>Contact Sales</Button>
                      </Stack>
                    </Card>
                  </Grid.Cell>
                </Grid>
              </div>
            </div>

            {/* CTA Section */}
            <div className="sf-hero text-white py-16">
              <div className="sf-container text-center">
                <Heading element="h2" className="text-white mb-4">
                  Ready to Build Your First Store?
                </Heading>
                <Text variant="bodyLg" as="p" className="mb-8 opacity-90">
                  Join thousands of entrepreneurs who have built successful stores with StoreForge AI
                </Text>
                <Button size="large" onClick={() => document.querySelector('input')?.focus()}>
                  Get Started Free
                </Button>
              </div>
            </div>
          </Layout.Section>
        </Layout>
      </Page>
    </Frame>
  )
}