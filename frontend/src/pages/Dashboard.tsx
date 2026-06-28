import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Upload, Film, ArrowRight, Loader2 } from 'lucide-react';
import { Video, videosApi } from '../api';

export const Dashboard = () => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const fetchVideos = async () => {
    try {
      const data = await videosApi.getVideos();
      setVideos(data);
    } catch (err) {
      console.error('Failed to fetch videos:', err);
      setError('Failed to load videos.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVideos();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError('');

    try {
      await videosApi.uploadVideo(file.name, file);
      await fetchVideos();
    } catch (err) {
      console.error('Upload failed:', err);
      setError('Failed to upload video.');
    } finally {
      setUploading(false);
      if (e.target) {
        e.target.value = '';
      }
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header & Upload */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-surface-400">Manage your videos and generate AI clips.</p>
        </div>

        <div className="relative">
          <input 
            type="file" 
            accept="video/mp4,video/x-m4v,video/*"
            onChange={handleFileUpload}
            disabled={uploading}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
          />
          <button className="btn-primary flex items-center gap-2" disabled={uploading}>
            {uploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Upload className="w-5 h-5" />}
            {uploading ? 'Uploading...' : 'Upload Video'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4 text-red-200">
          {error}
        </div>
      )}

      {/* Videos Grid */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
        </div>
      ) : videos.length === 0 ? (
        <div className="glass-card flex flex-col items-center justify-center h-64 text-center p-6">
          <div className="bg-surface-800 p-4 rounded-2xl mb-4">
            <Film className="w-8 h-8 text-surface-400" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">No videos yet</h3>
          <p className="text-surface-400 max-w-sm">Upload your first video to start generating viral clips with AI.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map(video => (
            <Link 
              key={video.id} 
              to={`/videos/${video.id}`}
              className="glass-card p-5 group hover:border-brand-500/50 transition-colors"
            >
              <div className="aspect-video bg-surface-900 rounded-lg flex items-center justify-center mb-4 overflow-hidden relative">
                <Film className="w-10 h-10 text-surface-600 group-hover:text-brand-500 transition-colors" />
                {/* Visual overlay gradient */}
                <div className="absolute inset-0 bg-gradient-to-t from-surface-950/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <h3 className="font-semibold text-white truncate mb-1">{video.title}</h3>
              <div className="flex justify-between items-center mt-4">
                <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-surface-700 text-surface-300">
                  {video.status}
                </span>
                <span className="text-brand-400 group-hover:text-brand-300 flex items-center gap-1 text-sm font-medium transition-colors">
                  Open <ArrowRight className="w-4 h-4" />
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};
