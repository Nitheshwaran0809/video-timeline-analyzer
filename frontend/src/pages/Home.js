import React from 'react';
import { Eye, Mic, FileText, Brain, Presentation, PlayCircle, Monitor, GraduationCap } from 'lucide-react';
import VideoUpload from '../components/VideoUpload';

const Home = () => {
  const handleUploadComplete = (sessionId, status) => {
    console.log('Upload completed:', sessionId, status);
  };

  return (
    <div>
      {/* Enhanced Hero Section */}
      <div className="relative overflow-hidden gradient-bg rounded-3xl p-12 mb-12 text-white">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative max-w-5xl mx-auto text-center">
          <div className="mb-6">
            <span className="inline-block bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium mb-4">
              🚀 AI-Powered Video Analysis
            </span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
            Intelligent Video<br />
            <span className="bg-gradient-to-r from-yellow-300 to-pink-300 bg-clip-text text-transparent">
              Timeline Analysis
            </span>
          </h1>
          <p className="text-xl md:text-2xl mb-8 opacity-90 max-w-3xl mx-auto leading-relaxed">
            Transform your videos into searchable, intelligent timelines. Automatically detect screen changes and correlate them with discussions.
          </p>
          <div className="grid md:grid-cols-3 gap-6 max-w-2xl mx-auto">
            <div className="flex items-center justify-center bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <Eye className="w-6 h-6 mr-3" />
              <span className="font-medium">Smart Detection</span>
            </div>
            <div className="flex items-center justify-center bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <Mic className="w-6 h-6 mr-3" />
              <span className="font-medium">Speech Analysis</span>
            </div>
            <div className="flex items-center justify-center bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <FileText className="w-6 h-6 mr-3" />
              <span className="font-medium">PDF Reports</span>
            </div>
          </div>
        </div>
        {/* Decorative elements */}
        <div className="absolute top-10 left-10 w-20 h-20 bg-white/10 rounded-full blur-xl"></div>
        <div className="absolute bottom-10 right-10 w-32 h-32 bg-white/10 rounded-full blur-xl"></div>
      </div>

      {/* Upload Section */}
      <VideoUpload onUploadComplete={handleUploadComplete} />

      {/* Features Section */}
      <div className="grid md:grid-cols-3 gap-8 mb-8">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <Eye className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Smart Screen Detection
          </h3>
          <p className="text-gray-600">
            Advanced computer vision algorithms detect meaningful screen changes, filtering out minor cursor movements and typing.
          </p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
            <Mic className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Accurate Transcription
          </h3>
          <p className="text-gray-600">
            Powered by Groq's Whisper API for high-quality speech-to-text conversion with precise timestamps.
          </p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
            <Brain className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Content Correlation
          </h3>
          <p className="text-gray-600">
            Intelligently maps visual content to verbal discussion, creating meaningful timeline segments with summaries.
          </p>
        </div>
      </div>

      {/* Use Cases */}
      <div className="bg-white rounded-xl shadow-sm p-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
          Perfect for Various Use Cases
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Presentation className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="font-medium text-gray-900 mb-1">Meetings</h3>
            <p className="text-sm text-gray-600">Track presentation slides and discussions</p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <PlayCircle className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="font-medium text-gray-900 mb-1">Tutorials</h3>
            <p className="text-sm text-gray-600">Map instructions to visual demonstrations</p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Monitor className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="font-medium text-gray-900 mb-1">Demos</h3>
            <p className="text-sm text-gray-600">Analyze product demonstrations</p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <GraduationCap className="w-8 h-8 text-orange-600" />
            </div>
            <h3 className="font-medium text-gray-900 mb-1">Training</h3>
            <p className="text-sm text-gray-600">Create searchable training materials</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
