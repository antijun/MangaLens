import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

export const uploadImage = async (file: File) => {
  const formData = new FormData();
  formData.append('image', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const processImage = async (imageId: string) => {
  const response = await api.post(`/process/${imageId}`);
  return response.data;
};

export const updateTranslations = async (imageId: string, translations: Array<{id: number, translated_text: string}>) => {
  const response = await api.patch(`/translations/${imageId}`, { translations });
  return response.data;
};

export const getImage = async (imageType: string, filename: string) => {
  try {
    const response = await api.get(`/images/${imageType}/${filename}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching image (${imageType}/${filename}):`, error);
    // Return a placeholder data URL for failed images
    return { data: 'https://placehold.co/600x400?text=Image+Not+Found' };
  }
};

export default api; 