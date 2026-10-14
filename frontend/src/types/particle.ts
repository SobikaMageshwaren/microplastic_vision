export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Centroid {
  x: number;
  y: number;
}

export interface ParticleFeatures {
  particle_id: string;
  analysis_id: string;
  bbox: BoundingBox;
  centroid: Centroid;
  area: number;
  perimeter: number;
  width: number;
  height: number;
  aspect_ratio: number;
  circularity: number;
  eccentricity: number;
  solidity: number;
  extent: number;
  compactness: number;
  convex_hull_area: number;
  skeleton_length: number;
  mean_thickness: number;
  pixel_size_um?: number | null;
  area_um2?: number | null;
  perimeter_um?: number | null;
  width_um?: number | null;
  height_um?: number | null;
  skeleton_length_um?: number | null;
  mean_thickness_um?: number | null;
  mean_intensity: number;
  std_intensity: number;
  min_intensity: number;
  max_intensity: number;
  glcm_contrast?: number | null;
  glcm_energy?: number | null;
  glcm_homogeneity?: number | null;
  glcm_correlation?: number | null;
  crop_path?: string | null;
}
