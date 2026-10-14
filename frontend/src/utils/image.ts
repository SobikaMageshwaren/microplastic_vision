const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export function getImageUrl(path?: string | null): string {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  let cleanPath = path.replace(/\\/g, '/');
  if (cleanPath.includes('/data/outputs/')) {
    cleanPath = '/data/outputs/' + cleanPath.split('/data/outputs/')[1];
  } else if (cleanPath.includes('data/outputs/')) {
    cleanPath = '/data/outputs/' + cleanPath.split('data/outputs/')[1];
  } else if (cleanPath.includes('/dataset/')) {
    cleanPath = '/dataset/' + cleanPath.split('/dataset/')[1];
  } else if (cleanPath.includes('dataset/')) {
    cleanPath = '/dataset/' + cleanPath.split('dataset/')[1];
  }
  if (!cleanPath.startsWith('/')) {
    cleanPath = `/${cleanPath}`;
  }
  return `${API_BASE_URL}${cleanPath}`;
}
