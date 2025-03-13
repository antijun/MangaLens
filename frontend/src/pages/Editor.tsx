import { useState, useEffect, useRef } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { 
  Container, 
  Grid, 
  Paper, 
  Title, 
  Text, 
  Group, 
  Button, 
  Box, 
  Image,
  Stack,
  LoadingOverlay,
  Tabs,
  TextInput,
  ScrollArea,
  Slider,
  ActionIcon,
  Tooltip
} from '@mantine/core';
import { 
  IconPhoto, 
  IconEdit, 
  IconArrowLeft, 
  IconDownload, 
  IconZoomIn, 
  IconZoomOut, 
  IconZoomReset,
  IconMaximize
} from '@tabler/icons-react';
import { getImage, updateTranslations } from '../services/api';

interface Translation {
  id: number;
  original_text: string;
  translated_text: string;
  bbox: [number, number, number, number];
}

interface ProcessedData {
  image_id: string;
  original_image: string;
  inpainted_image: string;
  text_only_image: string;
  boxed_image: string;
  translated_image: string;
  translations: Translation[];
}

export function Editor() {
  const { imageId } = useParams<{ imageId: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState<ProcessedData | null>(location.state as ProcessedData);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<string | null>('translated');
  const [editedTranslations, setEditedTranslations] = useState<Translation[]>([]);
  const [translatedImageUrl, setTranslatedImageUrl] = useState<string | null>(null);
  const [originalImageUrl, setOriginalImageUrl] = useState<string | null>(null);
  const [inpaintedImageUrl, setInpaintedImageUrl] = useState<string | null>(null);
  const [textOnlyImageUrl, setTextOnlyImageUrl] = useState<string | null>(null);
  const [boxedImageUrl, setBoxedImageUrl] = useState<string | null>(null);
  
  // Zoom functionality
  const [zoomLevel, setZoomLevel] = useState(100);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const imageContainerRef = useRef<HTMLDivElement>(null);

  // Ensure zoom level is always a multiple of 5
  const normalizeZoomLevel = (value: number) => {
    return Math.round(value / 5) * 5;
  };

  const fetchImages = async () => {
    // This functionality would require additional backend endpoints to retrieve past translations
    // For now, we just redirect to the home page if there's no data
    navigate('/');
  };

  const fetchImageUrls = async () => {
    if (!data) return;

    setIsLoading(true);
    try {
      const [translatedResp, originalResp, inpaintedResp, textOnlyResp] = await Promise.all([
        getImage('translated', data.translated_image.split('/').pop() || ''),
        getImage('uploads', data.original_image.split('/').pop() || ''),
        getImage('inpainted', data.inpainted_image.split('/').pop() || ''),
        getImage('text_only', data.text_only_image.split('/').pop() || '')
      ]);
      
      setTranslatedImageUrl(translatedResp.data);
      setOriginalImageUrl(originalResp.data);
      setInpaintedImageUrl(inpaintedResp.data);
      setTextOnlyImageUrl(textOnlyResp.data);
    } catch (error) {
      console.error('Error fetching images:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!data && imageId) {
      fetchImages();
    } else if (data) {
      setEditedTranslations(data.translations);
      fetchImageUrls();
    }
  }, [data, imageId]);

  // Center the image when zoom level changes
  useEffect(() => {
    if (imageContainerRef.current && zoomLevel !== 100) {
      // Center the scrollable area
      const container = imageContainerRef.current;
      if (container) {
        // Set timeout to ensure the DOM has updated with the new zoom level
        setTimeout(() => {
          const scrollWidth = container.scrollWidth;
          const scrollHeight = container.scrollHeight;
          const clientWidth = container.clientWidth;
          const clientHeight = container.clientHeight;
          
          container.scrollLeft = (scrollWidth - clientWidth) / 2;
          container.scrollTop = (scrollHeight - clientHeight) / 2;
        }, 50);
      }
    }
  }, [zoomLevel]);

  const handleTranslationChange = (id: number, value: string) => {
    setEditedTranslations(prev => 
      prev.map(t => t.id === id ? { ...t, translated_text: value } : t)
    );
  };

  const handleSaveTranslations = async () => {
    if (!imageId) return;
    
    setIsSaving(true);
    try {
      // Only send the translations that have been modified
      const translationsToUpdate = editedTranslations.map(t => ({
        id: t.id,
        translated_text: t.translated_text
      }));
      
      const response = await updateTranslations(imageId, translationsToUpdate);
      
      // Update the translated image
      const updatedTranslatedImage = await getImage('translated', response.translated_image.split('/').pop() || '');
      setTranslatedImageUrl(updatedTranslatedImage.data);
      
      // Switch to the translated image tab
      setActiveTab('translated');
    } catch (error) {
      console.error('Error saving translations:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDownload = () => {
    if (!translatedImageUrl) return;
    
    const link = document.createElement('a');
    link.href = translatedImageUrl;
    link.download = `translated_manga_${imageId}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Zoom handlers
  const handleZoomIn = () => {
    setZoomLevel(prev => {
      const newZoom = normalizeZoomLevel(Math.min(prev + 10, 200));
      return newZoom;
    });
  };

  const handleZoomOut = () => {
    setZoomLevel(prev => {
      const newZoom = normalizeZoomLevel(Math.max(prev - 10, 50));
      return newZoom;
    });
  };

  const handleZoomReset = () => {
    setZoomLevel(100);
  };

  // Fullscreen toggle
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      const container = imageContainerRef.current;
      if (container) {
        container.requestFullscreen().catch(err => {
          console.error(`Error attempting to enable fullscreen: ${err.message}`);
        });
      }
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  // Handle fullscreen change event
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  // Handle escape key to exit fullscreen
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isFullscreen) {
        document.exitFullscreen();
        setIsFullscreen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isFullscreen]);

  if (!data || isLoading) {
    return (
      <Container size="xl" py="xl">
        <LoadingOverlay visible={true} />
        <Box style={{ height: '80vh' }} />
      </Container>
    );
  }

  return (
    <Container size="xl" py="xl">
      <Stack gap="xl">
        <Group justify="apart">
          <Button 
            leftSection={<IconArrowLeft size={16} />} 
            variant="subtle" 
            onClick={() => navigate('/')}
          >
            Back to Home
          </Button>
          
          <Button 
            leftSection={<IconDownload size={16} />}
            onClick={handleDownload}
            disabled={!translatedImageUrl}
          >
            Download Translated Image
          </Button>
        </Group>

        <Title order={2}>Manga Translation Editor</Title>

        <Grid>
          <Grid.Col span={7}>
            <Paper shadow="sm" radius="md" p="md" withBorder className="relative dark:border-gray-700">
              <Tabs value={activeTab} onChange={setActiveTab}>
                <Tabs.List>
                  <Tabs.Tab value="translated" leftSection={<IconPhoto size={14} />}>
                    Translated
                  </Tabs.Tab>
                  <Tabs.Tab value="original" leftSection={<IconPhoto size={14} />}>
                    Original
                  </Tabs.Tab>
                  <Tabs.Tab value="inpainted" leftSection={<IconPhoto size={14} />}>
                    Inpainted
                  </Tabs.Tab>
                  <Tabs.Tab value="textOnly" leftSection={<IconPhoto size={14} />}>
                    Text Only
                  </Tabs.Tab>
                </Tabs.List>

                <Group justify="flex-end" mt="xs" mb="xs" className="flex items-center gap-2">
                  <Text size="sm" c="dimmed" className="mr-2">Zoom: {zoomLevel}%</Text>
                  <Slider
                    value={zoomLevel}
                    onChange={(value) => setZoomLevel(normalizeZoomLevel(value))}
                    min={50}
                    max={200}
                    step={5}
                    label={null}
                    w={100}
                    className="mx-2"
                  />
                  <Tooltip label="Zoom out">
                    <ActionIcon onClick={handleZoomOut} variant="subtle" disabled={zoomLevel <= 50}>
                      <IconZoomOut size={18} />
                    </ActionIcon>
                  </Tooltip>
                  <Tooltip label="Reset zoom">
                    <ActionIcon onClick={handleZoomReset} variant="subtle" disabled={zoomLevel === 100}>
                      <IconZoomReset size={18} />
                    </ActionIcon>
                  </Tooltip>
                  <Tooltip label="Zoom in">
                    <ActionIcon onClick={handleZoomIn} variant="subtle" disabled={zoomLevel >= 200}>
                      <IconZoomIn size={18} />
                    </ActionIcon>
                  </Tooltip>
                  <Tooltip label={isFullscreen ? "Exit fullscreen" : "Fullscreen"}>
                    <ActionIcon onClick={toggleFullscreen} variant="subtle">
                      <IconMaximize size={18} />
                    </ActionIcon>
                  </Tooltip>
                </Group>

                <Box 
                  pos="relative" 
                  mt="md" 
                  ref={imageContainerRef} 
                  className="image-viewer dark:bg-gray-800" 
                  style={{ height: '700px' }}
                >
                  <LoadingOverlay visible={isSaving} />
                  
                  <Tabs.Panel value="translated" className="h-full">
                    {translatedImageUrl && (
                      <div className="active-panel">
                        <div className="zoomed-container" style={{ 
                          width: zoomLevel > 100 ? `${zoomLevel}%` : '100%',
                          height: zoomLevel > 100 ? `${zoomLevel}%` : '100%'
                        }}>
                          <img
                            src={translatedImageUrl}
                            alt="Translated manga"
                            style={{ 
                              transform: `scale(${zoomLevel / 100})`,
                              transition: 'transform 0.2s ease',
                              maxWidth: '100%',
                              maxHeight: '100%'
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </Tabs.Panel>
                  
                  <Tabs.Panel value="original" className="h-full">
                    {originalImageUrl && (
                      <div className="active-panel">
                        <div className="zoomed-container" style={{ 
                          width: zoomLevel > 100 ? `${zoomLevel}%` : '100%',
                          height: zoomLevel > 100 ? `${zoomLevel}%` : '100%'
                        }}>
                          <img
                            src={originalImageUrl}
                            alt="Original manga"
                            style={{ 
                              transform: `scale(${zoomLevel / 100})`,
                              transition: 'transform 0.2s ease',
                              maxWidth: '100%',
                              maxHeight: '100%'
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </Tabs.Panel>
                  
                  <Tabs.Panel value="inpainted" className="h-full">
                    {inpaintedImageUrl && (
                      <div className="active-panel">
                        <div className="zoomed-container" style={{ 
                          width: zoomLevel > 100 ? `${zoomLevel}%` : '100%',
                          height: zoomLevel > 100 ? `${zoomLevel}%` : '100%'
                        }}>
                          <img
                            src={inpaintedImageUrl}
                            alt="Inpainted manga"
                            style={{ 
                              transform: `scale(${zoomLevel / 100})`,
                              transition: 'transform 0.2s ease',
                              maxWidth: '100%',
                              maxHeight: '100%'
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </Tabs.Panel>
                  
                  <Tabs.Panel value="textOnly" className="h-full">
                    {textOnlyImageUrl && (
                      <div className="active-panel">
                        <div className="zoomed-container" style={{ 
                          width: zoomLevel > 100 ? `${zoomLevel}%` : '100%',
                          height: zoomLevel > 100 ? `${zoomLevel}%` : '100%'
                        }}>
                          <img
                            src={textOnlyImageUrl}
                            alt="Text only"
                            style={{ 
                              transform: `scale(${zoomLevel / 100})`,
                              transition: 'transform 0.2s ease',
                              maxWidth: '100%',
                              maxHeight: '100%'
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </Tabs.Panel>
                </Box>
              </Tabs>
            </Paper>
          </Grid.Col>
          
          <Grid.Col span={5}>
            <Paper shadow="sm" radius="md" p="md" withBorder className="dark:border-gray-700">
              <Group justify="apart" mb="md">
                <Title order={3}>Translations</Title>
                <Button 
                  leftSection={<IconEdit size={16} />}
                  onClick={handleSaveTranslations}
                  loading={isSaving}
                  color="indigo"
                >
                  Save & Apply
                </Button>
              </Group>
              
              <ScrollArea h={550} className="dark:scrollbar-dark">
                <Stack gap="md">
                  {editedTranslations.map((translation) => (
                    <Paper key={translation.id} p="xs" withBorder className="dark:border-gray-700 dark:bg-gray-800">
                      <Text size="sm" fw={500} mb={4}>
                        Original:
                      </Text>
                      <Text size="sm" mb="xs" c="dimmed">
                        {translation.original_text || "(No text detected)"}
                      </Text>
                      
                      <Text size="sm" fw={500} mb={4}>
                        Translation:
                      </Text>
                      <TextInput
                        value={translation.translated_text}
                        onChange={(e) => handleTranslationChange(translation.id, e.target.value)}
                        placeholder="Enter translation"
                        className="dark:input-dark"
                      />
                    </Paper>
                  ))}
                  
                  {editedTranslations.length === 0 && (
                    <Text c="dimmed" ta="center">
                      No text was detected in this image
                    </Text>
                  )}
                </Stack>
              </ScrollArea>
            </Paper>
          </Grid.Col>
        </Grid>
      </Stack>
    </Container>
  );
} 