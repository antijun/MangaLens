import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Container, 
  Title, 
  Text, 
  Group, 
  Button, 
  Box, 
  Image,
  Stack,
  LoadingOverlay,
  Paper,
  Flex,
  ThemeIcon,
  List,
  Card,
  Center,
  ActionIcon
} from '@mantine/core';
import { Dropzone, FileWithPath } from '@mantine/dropzone';
import { 
  IconUpload, 
  IconPhoto, 
  IconX, 
  IconLanguage, 
  IconWand, 
  IconEdit, 
  IconDownload,
  IconZoomOut,
  IconZoomIn,
  IconZoomReset
} from '@tabler/icons-react';
import { uploadImage, processImage } from '../services/api';

export function Home() {
  const [file, setFile] = useState<FileWithPath | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const navigate = useNavigate();

  // Preview image zoom functionality
  const [zoomLevel, setZoomLevel] = useState(100);
  const previewContainerRef = useRef<HTMLDivElement>(null);

  // Ensure zoom level is always a multiple of 5
  const normalizeZoomLevel = (value: number) => {
    return Math.round(value / 5) * 5;
  };

  // Center the image when zoom level changes
  useEffect(() => {
    if (previewContainerRef.current && zoomLevel !== 100) {
      // Center the scrollable area
      const container = previewContainerRef.current;
      if (container) {
        // Set timeout to ensure the DOM has updated with the new zoom level
        setTimeout(() => {
          const scrollWidth = container.scrollWidth;
          const scrollHeight = container.scrollHeight;
          const clientWidth = container.clientWidth;
          const clientHeight = container.clientHeight;
          
          container.scrollLeft = (scrollWidth - clientWidth) / 2;
          container.scrollTop = (scrollHeight - clientHeight) / 2;
        }, 100); // Increased timeout to ensure DOM updates
      }
    }
  }, [zoomLevel]);

  // Zoom handlers
  const handleZoomIn = () => {
    setZoomLevel(prev => normalizeZoomLevel(Math.min(prev + 10, 200)));
  };

  const handleZoomOut = () => {
    setZoomLevel(prev => normalizeZoomLevel(Math.max(prev - 10, 50)));
  };

  const handleZoomReset = () => {
    setZoomLevel(100);
  };

  const handleDrop = (files: FileWithPath[]) => {
    setFile(files[0]);
    setPreview(URL.createObjectURL(files[0]));
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      setIsUploading(true);
      const response = await uploadImage(file);
      setIsUploading(false);
      
      setIsProcessing(true);
      const processedData = await processImage(response.image_id);
      setIsProcessing(false);
      
      // Check if the backend provided a redirect URL, otherwise use the default editor path
      if (processedData.redirect_url) {
        navigate(processedData.redirect_url, { state: processedData });
      } else {
        navigate(`/editor/${response.image_id}`, { state: processedData });
      }
    } catch (error) {
      console.error('Error uploading/processing image:', error);
      setIsUploading(false);
      setIsProcessing(false);
    }
  };

  return (
    <Container size="lg" py="xl">
      <Flex direction={{ base: 'column', md: 'row' }} gap="xl" align="center" mb="xl">
        <Box style={{ flex: 1 }}>
          <Title order={1} size="h1" fw={900} className="gradient-text" mb="md">
            MangaLens
          </Title>
          <Text size="xl" c="dimmed" mb="xl">
            Instantly translate manga panels with AI-powered text detection and translation.
          </Text>

          <Paper withBorder p="md" radius="md" mb="lg" className="dark:bg-gray-800 dark:border-gray-700">
            <List spacing="sm" size="md" center icon={
              <ThemeIcon color="indigo" size={24} radius="xl">
                <IconLanguage size={16} />
              </ThemeIcon>
            }>
              <List.Item>Automatic text detection in manga panels</List.Item>
              <List.Item>AI-powered translation to your preferred language</List.Item>
              <List.Item>Edit translations and customize text placement</List.Item>
              <List.Item>Download and share your translated manga</List.Item>
            </List>
          </Paper>
        </Box>

        <Card withBorder shadow="sm" padding="lg" radius="md" w={{ base: '100%', md: '55%' }} className="dark:border-gray-700">
          <Card.Section withBorder inheritPadding py="xs" className="dark:border-gray-700">
            <Text fw={500} size="lg">Upload your manga panel</Text>
          </Card.Section>

          <Dropzone
            onDrop={handleDrop}
            maxSize={5 * 1024 * 1024}
            accept={{
              'image/png': ['.png'],
              'image/jpeg': ['.jpg', '.jpeg']
            }}
            multiple={false}
            my="md"
            h={200}
            className="dark:border-gray-700 dark:bg-gray-800"
          >
            <Group justify="center" gap="xl" style={{ minHeight: 180, pointerEvents: 'none' }}>
              <Dropzone.Accept>
                <IconUpload size={50} stroke={1.5} color="var(--mantine-color-indigo-6)" />
              </Dropzone.Accept>
              <Dropzone.Reject>
                <IconX size={50} stroke={1.5} color="var(--mantine-color-red-6)" />
              </Dropzone.Reject>
              <Dropzone.Idle>
                <IconPhoto size={50} stroke={1.5} />
              </Dropzone.Idle>

              <Stack gap="xs" style={{ maxWidth: '80%' }}>
                <Text size="xl" inline ta="center">
                  Drag a manga image here or click to select
                </Text>
                <Text size="sm" c="dimmed" ta="center">
                  Support for JPG and PNG images, max 5MB
                </Text>
              </Stack>
            </Group>
          </Dropzone>

          {preview && (
            <Box pos="relative" mb="md" mt="md">
              <LoadingOverlay visible={isUploading || isProcessing} />
              <Box 
                ref={previewContainerRef}
                className="image-viewer dark:bg-gray-800" 
                style={{ height: '400px' }}
              >
                <div className="active-panel">
                  <div className="zoomed-container" style={{ 
                    width: zoomLevel > 100 ? `${zoomLevel}%` : '100%',
                    height: zoomLevel > 100 ? `${zoomLevel}%` : '100%'
                  }}>
                    <img
                      src={preview}
                      alt="Preview"
                      style={{ 
                        transform: `scale(${zoomLevel / 100})`,
                        transition: 'transform 0.2s ease',
                        maxWidth: '100%',
                        maxHeight: '100%'
                      }}
                    />
                  </div>
                </div>
              </Box>
              <Group justify="center" mt="xs">
                <ActionIcon onClick={handleZoomOut} size="lg" color="indigo" variant="light">
                  <IconZoomOut size={20} />
                </ActionIcon>
                <Text>{zoomLevel}%</Text>
                <ActionIcon onClick={handleZoomIn} size="lg" color="indigo" variant="light">
                  <IconZoomIn size={20} />
                </ActionIcon>
                <ActionIcon onClick={handleZoomReset} size="lg" color="gray" variant="light">
                  <IconZoomReset size={20} />
                </ActionIcon>
              </Group>
            </Box>
          )}

          <Group justify="center" mt="md">
            <Button 
              onClick={handleUpload} 
              disabled={!file || isUploading || isProcessing}
              loading={isUploading || isProcessing}
              size="lg"
              leftSection={!isUploading && !isProcessing ? <IconWand size={18} /> : null}
              fullWidth
              color="indigo"
            >
              {isUploading 
                ? 'Uploading...' 
                : isProcessing 
                  ? 'Processing...' 
                  : 'Translate Now'
              }
            </Button>
          </Group>
        </Card>
      </Flex>

      <Flex gap="md" wrap="wrap" mt={60}>
        <Card withBorder shadow="sm" padding="lg" radius="md" w={{ base: '100%', sm: 'calc(33.333% - 14px)' }} className="feature-card dark:border-gray-700">
          <Center mb="md">
            <ThemeIcon size={48} radius="md" color="indigo">
              <IconLanguage size={24} />
            </ThemeIcon>
          </Center>
          <Text fw={700} ta="center" size="lg">AI Translation</Text>
          <Text c="dimmed" size="sm" ta="center">
            Powerful AI detects and translates text from your manga panels automatically
          </Text>
        </Card>

        <Card withBorder shadow="sm" padding="lg" radius="md" w={{ base: '100%', sm: 'calc(33.333% - 14px)' }} className="feature-card dark:border-gray-700">
          <Center mb="md">
            <ThemeIcon size={48} radius="md" color="indigo">
              <IconEdit size={24} />
            </ThemeIcon>
          </Center>
          <Text fw={700} ta="center" size="lg">Custom Editing</Text>
          <Text c="dimmed" size="sm" ta="center">
            Edit any translation to perfect the wording and match the original context
          </Text>
        </Card>

        <Card withBorder shadow="sm" padding="lg" radius="md" w={{ base: '100%', sm: 'calc(33.333% - 14px)' }} className="feature-card dark:border-gray-700">
          <Center mb="md">
            <ThemeIcon size={48} radius="md" color="indigo">
              <IconDownload size={24} />
            </ThemeIcon>
          </Center>
          <Text fw={700} ta="center" size="lg">Quick Export</Text>
          <Text c="dimmed" size="sm" ta="center">
            Download your translated manga panels in high quality for sharing
          </Text>
        </Card>
      </Flex>
    </Container>
  );
} 