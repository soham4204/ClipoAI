import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ChevronLeft, Play, Wand2, Scissors, Loader2, CheckCircle2, AlertCircle, Download } from 'lucide-react';
import { Video, Clip, Job, videosApi, pipelineApi } from '../api';

export const VideoDetail = () => {
  const { id } = useParams<{ id: string }>();
  const [video, setVideo] = useState<Video | null>(null);
  const [clips, setClips] = useState<Clip[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchData = async () => {
    if (!id) return;
    try {
      const [videoData, clipsData, jobsData] = await Promise.all([
        videosApi.getVideo(id),
        videosApi.getVideoClips(id),
        videosApi.getVideoJobs(id)
      ]);
      setVideo(videoData);
      setClips(clipsData);
      setJobs(jobsData);
    } catch (err) {
      console.error(err);
      setError('Failed to load video data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Poll every 5 seconds if there are running jobs
    const interval = setInterval(() => {
      fetchData();
    }, 5000);
    return () => clearInterval(interval);
  }, [id]);

  const handleTranscribe = async () => {
    if (!id) return;
    try {
      await pipelineApi.transcribe(id);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start transcription');
    }
  };

  const handleAnalyze = async () => {
    if (!id) return;
    try {
      await pipelineApi.analyze(id);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start analysis');
    }
  };

  const handleGenerate = async (clipId: string) => {
    try {
      await pipelineApi.generateClip(clipId);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start generation');
    }
  };

  if (loading && !video) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
      </div>
    );
  }

  if (error || !video) {
    return (
      <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4 text-red-200">
        {error || 'Video not found.'}
      </div>
    );
  }

  const getJobStatus = (type: string) => {
    const job = jobs.find(j => j.type === type);
    return job?.status;
  };

  const isTranscribing = getJobStatus('transcription') === 'running' || getJobStatus('transcription') === 'queued';
  const isAnalyzing = getJobStatus('analysis') === 'running' || getJobStatus('analysis') === 'queued';

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-center gap-4">
        <Link to="/" className="p-2 bg-surface-800 rounded-xl hover:bg-surface-700 transition-colors">
          <ChevronLeft className="w-5 h-5 text-surface-300" />
        </Link>
        <h1 className="text-2xl font-bold text-white truncate">{video.title}</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Actions & Status */}
        <div className="lg:col-span-1 space-y-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-white border-b border-surface-700 pb-4">AI Pipeline</h2>
            
            {/* Step 1: Transcribe */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-surface-200 font-medium flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-surface-700 flex items-center justify-center text-xs">1</span>
                  Transcription
                </span>
                {getJobStatus('transcription') === 'completed' && <CheckCircle2 className="w-5 h-5 text-green-500" />}
                {getJobStatus('transcription') === 'failed' && <AlertCircle className="w-5 h-5 text-red-500" />}
              </div>
              <button 
                onClick={handleTranscribe}
                disabled={isTranscribing || getJobStatus('transcription') === 'completed'}
                className="w-full btn-secondary py-2 flex justify-center items-center gap-2 text-sm"
              >
                {isTranscribing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                {isTranscribing ? 'Processing...' : getJobStatus('transcription') === 'completed' ? 'Completed' : 'Start Transcription'}
              </button>
            </div>

            {/* Step 2: Analyze */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-surface-200 font-medium flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-surface-700 flex items-center justify-center text-xs">2</span>
                  Viral Analysis
                </span>
                {getJobStatus('analysis') === 'completed' && <CheckCircle2 className="w-5 h-5 text-green-500" />}
                {getJobStatus('analysis') === 'failed' && <AlertCircle className="w-5 h-5 text-red-500" />}
              </div>
              <button 
                onClick={handleAnalyze}
                disabled={isAnalyzing || getJobStatus('analysis') === 'completed' || getJobStatus('transcription') !== 'completed'}
                className="w-full btn-secondary py-2 flex justify-center items-center gap-2 text-sm"
              >
                {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                {isAnalyzing ? 'Analyzing...' : getJobStatus('analysis') === 'completed' ? 'Completed' : 'Find Viral Clips'}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Clips */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Scissors className="w-5 h-5 text-brand-500" /> Generated Clips
          </h2>

          {clips.length === 0 ? (
            <div className="glass-card flex flex-col items-center justify-center h-64 text-center p-6 border-dashed border-surface-600">
              <Wand2 className="w-10 h-10 text-surface-500 mb-4 opacity-50" />
              <p className="text-surface-400">Run the Viral Analysis to generate clips.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {clips.map(clip => (
                <div key={clip.id} className="glass-card overflow-hidden group">
                  <div className="aspect-[9/16] bg-surface-900 relative">
                    {/* Placeholder for vertical video thumbnail */}
                    {clip.storage_path ? (
                      <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                        <span className="text-green-400 font-medium">Ready</span>
                      </div>
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center text-surface-500 flex-col gap-2">
                        {clip.status === 'processing' ? (
                          <>
                            <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
                            <span className="text-sm">Editing video...</span>
                          </>
                        ) : (
                          <>
                            <Scissors className="w-8 h-8 opacity-50" />
                            <span className="text-sm">Not generated yet</span>
                          </>
                        )}
                      </div>
                    )}
                    
                    {/* Viral Score Badge */}
                    <div className="absolute top-3 right-3 bg-brand-600 text-white text-xs font-bold px-2 py-1 rounded-lg shadow-lg">
                      Score: {clip.viral_score}
                    </div>
                  </div>
                  
                  <div className="p-4 bg-surface-800/80 backdrop-blur-md">
                    <h3 className="font-semibold text-white text-sm line-clamp-2 mb-2">{clip.title}</h3>
                    <p className="text-xs text-surface-400 mb-4">
                      {clip.start_time_sec}s - {clip.end_time_sec}s
                    </p>
                    
                    {clip.storage_path ? (
                      <a 
                        href={`http://localhost:9000/${clip.storage_path}`} 
                        download
                        target="_blank"
                        rel="noreferrer"
                        className="w-full btn-primary py-2 flex justify-center items-center gap-2 text-sm"
                      >
                        <Download className="w-4 h-4" /> Download Clip
                      </a>
                    ) : (
                      <button 
                        onClick={() => handleGenerate(clip.id)}
                        disabled={clip.status === 'processing'}
                        className="w-full btn-secondary py-2 flex justify-center items-center gap-2 text-sm bg-surface-700"
                      >
                        {clip.status === 'processing' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Scissors className="w-4 h-4" />}
                        {clip.status === 'processing' ? 'Generating...' : 'Generate Video'}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
