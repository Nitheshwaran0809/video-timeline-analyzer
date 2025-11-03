import React, { useState, useRef } from 'react';
import { UploadCloud, CheckCircle } from 'lucide-react';
import axios from 'axios';

const VideoUpload = ({ onUploadComplete }) => {
  const [uploadState, setUploadState] = useState('idle'); // idle, uploading, processing, completed, error
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processProgress, setProcessProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const processingInterval = useRef(null);

  const handleFileSelect = (file) => {
    // Validate file
    const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo'];
    if (!validTypes.includes(file.type)) {
      alert('Please select a valid video file (MP4, AVI, MOV, MKV)');
      return;
    }

    if (file.size > 500 * 1024 * 1024) { // 500MB limit
      alert('File size must be less than 500MB');
      return;
    }

    uploadFile(file);
  };

  const uploadFile = async (file) => {
    setUploadState('uploading');
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        },
      });

      setSessionId(response.data.session_id);
      setUploadState('processing');
      setStatusMessage('Starting analysis...');
      startProcessingMonitor(response.data.session_id);

    } catch (error) {
      console.error('Upload error:', error);
      setUploadState('error');
      setStatusMessage('Upload failed. Please try again.');
    }
  };

  const startProcessingMonitor = (sessionId) => {
    processingInterval.current = setInterval(async () => {
      try {
        const response = await axios.get(`/status/${sessionId}`);
        const status = response.data;

        setProcessProgress(status.progress);
        setStatusMessage(status.message);

        if (status.status === 'completed') {
          clearInterval(processingInterval.current);
          setUploadState('completed');
          if (onUploadComplete) {
            onUploadComplete(sessionId, status);
          }
        } else if (status.status === 'error') {
          clearInterval(processingInterval.current);
          setUploadState('error');
          setStatusMessage('Processing failed: ' + status.message);
        }

      } catch (error) {
        console.error('Status check error:', error);
      }
    }, 2000);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const resetUpload = () => {
    setUploadState('idle');
    setUploadProgress(0);
    setProcessProgress(0);
    setStatusMessage('');
    setSessionId(null);
    if (processingInterval.current) {
      clearInterval(processingInterval.current);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 mb-12 border border-gray-100">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">
            🎬 Upload Your Video
          </h2>
          <p className="text-gray-600 text-lg">
            Drop your video file below and let AI analyze it for you
          </p>
        </div>
        
        {uploadState === 'idle' && (
          <div 
            className={`upload-zone rounded-lg p-8 text-center mb-6 cursor-pointer ${
              isDragOver ? 'dragover' : ''
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <UploadCloud className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Drop your video file here
            </h3>
            <p className="text-gray-500 mb-4">
              or click to browse files
            </p>
            <p className="text-sm text-gray-400">
              Supports MP4, AVI, MOV, MKV (Max 500MB)
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".mp4,.avi,.mov,.mkv"
              className="hidden"
              onChange={handleFileInputChange}
            />
            <button className="btn-primary text-white px-6 py-2 rounded-lg font-medium mt-4">
              Browse Files
            </button>
          </div>
        )}

        {uploadState === 'uploading' && (
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4">
              <div className="animate-spin w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full"></div>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Uploading...
            </h3>
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div 
                className="progress-bar h-2 rounded-full transition-all duration-300" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600">
              {uploadProgress < 100 ? `Uploading... ${uploadProgress}%` : 'Upload complete!'}
            </p>
          </div>
        )}

        {uploadState === 'processing' && (
          <div className="bg-blue-50 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="animate-spin w-6 h-6 border-2 border-blue-200 border-t-blue-600 rounded-full mr-3"></div>
              <h3 className="text-lg font-medium text-blue-900">
                Processing Video
              </h3>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-3 mb-3">
              <div 
                className="bg-blue-600 h-3 rounded-full transition-all duration-500" 
                style={{ width: `${processProgress}%` }}
              ></div>
            </div>
            <p className="text-blue-700 text-sm">
              {statusMessage}
            </p>
          </div>
        )}

        {uploadState === 'completed' && (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-8 border border-green-200 bounce-in">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="relative">
                  <CheckCircle className="w-12 h-12 text-green-600 mr-4" />
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-ping"></div>
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-green-900 mb-2">
                    🎉 Analysis Complete!
                  </h3>
                  <p className="text-green-700 text-lg">
                    {statusMessage}
                  </p>
                  <p className="text-green-600 text-sm mt-1">
                    Your intelligent timeline is ready to explore
                  </p>
                </div>
              </div>
              <div className="flex flex-col space-y-3">
                <button 
                  onClick={() => window.location.href = `/timeline/${sessionId}`}
                  className="btn-primary text-white px-8 py-3 rounded-xl font-semibold flex items-center hover:scale-105 transition-transform duration-200"
                >
                  <span className="mr-2">🚀</span>
                  View Timeline
                </button>
                <button 
                  onClick={resetUpload}
                  className="text-gray-600 hover:text-gray-800 text-sm font-medium"
                >
                  Analyze Another Video
                </button>
              </div>
            </div>
          </div>
        )}

        {uploadState === 'error' && (
          <div className="bg-red-50 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-red-900">
                  Error
                </h3>
                <p className="text-red-700 text-sm">
                  {statusMessage}
                </p>
              </div>
              <button 
                onClick={resetUpload}
                className="bg-red-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-red-700"
              >
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoUpload;
