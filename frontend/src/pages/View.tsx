import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Container, 
  Paper, 
  Title, 
  Group, 
  Button, 
  Box, 
  Image,
  Stack,
  LoadingOverlay,
  Text,
  Slider,
  ActionIcon,
  Tooltip
} from '@mantine/core';
import { 
  IconArrowLeft, 
  IconDownload, 
  IconEdit, 
  IconZoomIn, 
  IconZoomOut, 
  IconZoomReset,
  IconMaximize 
} from '@tabler/icons-react';
import { getImage, processImage } from '../services/api';

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

export function View() {
  const { imageId } = useParams<{ imageId: string }>();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [translatedImageUrl, setTranslatedImageUrl] = useState<string | null>(null);
  const [isNavigating, setIsNavigating] = useState(false);
  
  // Zoom functionality
  const [zoomLevel, setZoomLevel] = useState(100);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const imageContainerRef = useRef<HTMLDivElement>(null);

  // Ensure zoom level is always a multiple of 5
  const normalizeZoomLevel = (value: number) => {
    return Math.round(value / 5) * 5;
  };

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

  useEffect(() => {
    if (imageId) {
      fetchTranslatedImage();
    }
  }, [imageId]);

  const fetchTranslatedImage = async () => {
    if (!imageId) return;

    setIsLoading(true);
    try {
      const translatedResp = await getImage('translated', `${imageId}_translated.png`);
      setTranslatedImageUrl(translatedResp.data);
    } catch (error) {
      console.error('Error fetching translated image:', error);
    } finally {
      setIsLoading(false);
    }
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

  const handleDownload = () => {
    if (!translatedImageUrl) return;
    
    const link = document.createElement('a');
    link.href = translatedImageUrl;
    link.download = `translated_manga_${imageId}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleEdit = async () => {
    if (!imageId) return;
    
    try {
      setIsNavigating(true);
      // Fetch all the necessary data for the editor
      const processedData = await processImage(imageId);
      
      // Navigate to the editor with the data
      navigate(`/editor/${imageId}`, { state: processedData });
    } catch (error) {
      console.error('Error getting data for editor:', error);
      // Fallback to simple navigation without state
      navigate(`/editor/${imageId}`);
    } finally {
      setIsNavigating(false);
    }
  };

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
          
          <Group>
            <Button 
              leftSection={<IconEdit size={16} />}
              onClick={handleEdit}
              loading={isNavigating}
              disabled={isNavigating}
              color="indigo"
            >
              Edit Translations
            </Button>
            
            <Button 
              leftSection={<IconDownload size={16} />}
              onClick={handleDownload}
              disabled={!translatedImageUrl || isNavigating}
              color="indigo"
            >
              Download Translated Image
            </Button>
          </Group>
        </Group>

        <Title order={2}>Translated Manga</Title>

        <Paper shadow="sm" radius="md" p="md" withBorder className="relative dark:border-gray-700">
          <Group justify="flex-end" mb="xs" className="flex items-center gap-2">
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
            <LoadingOverlay visible={isLoading || isNavigating} />
            
            {translatedImageUrl && (
              <div className="active-panel">
                <div className="zoomed-container" style={{ 
                  width: '100%',
                  height: '100%'
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
          </Box>
        </Paper>
      </Stack>
    </Container>
  );
} 