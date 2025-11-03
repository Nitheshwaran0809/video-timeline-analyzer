import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Clock, Download, Search, Filter, FileText } from 'lucide-react';
import axios from 'axios';

const Timeline = () => {
  const { sessionId } = useParams();
  const [timelineData, setTimelineData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [filteredSegments, setFilteredSegments] = useState([]);

  const fetchTimelineData = async () => {
    try {
      const response = await axios.get(`/results/${sessionId}`);
      setTimelineData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching timeline data:', error);
      setError('Failed to load timeline data');
      setLoading(false);
    }
  };

  const filterSegments = () => {
    if (!timelineData) return;

    let filtered = timelineData.timeline_segments;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(segment =>
        segment.transcript.toLowerCase().includes(searchTerm.toLowerCase()) ||
        segment.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
        segment.key_topics.some(topic => 
          topic.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Filter by selected topics
    if (selectedTopics.length > 0) {
      filtered = filtered.filter(segment =>
        segment.key_topics.some(topic => selectedTopics.includes(topic))
      );
    }

    setFilteredSegments(filtered);
  };

  useEffect(() => {
    fetchTimelineData();
  }, [sessionId]);

  useEffect(() => {
    if (timelineData) {
      filterSegments();
    }
  }, [timelineData, searchTerm, selectedTopics]);

  const getAllTopics = () => {
    if (!timelineData) return [];
    
    const allTopics = new Set();
    timelineData.timeline_segments.forEach(segment => {
      segment.key_topics.forEach(topic => allTopics.add(topic));
    });
    
    return Array.from(allTopics);
  };

  const toggleTopic = (topic) => {
    setSelectedTopics(prev =>
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    );
  };

  const exportToPDF = async () => {
    try {
      const response = await axios.post(`/export/pdf/${sessionId}`);
      const downloadUrl = response.data.download_url;
      window.open(downloadUrl, '_blank');
    } catch (error) {
      console.error('Error exporting PDF:', error);
      alert('Failed to export PDF');
    }
  };


  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 text-lg font-medium">{error}</div>
        <button 
          onClick={() => window.location.href = '/'}
          className="mt-4 btn-primary text-white px-6 py-2 rounded-lg font-medium"
        >
          Go Back Home
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Enhanced Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-8 mb-8 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-3">
              📹 Video Timeline Analysis
            </h1>
            <div className="flex items-center space-x-6 text-blue-100">
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-2" />
                <span className="font-medium">{timelineData?.metadata.video_filename}</span>
              </div>
              <div className="flex items-center">
                <FileText className="w-4 h-4 mr-2" />
                <span>{timelineData?.metadata.total_segments} segments</span>
              </div>
              <div className="flex items-center">
                <span className="text-sm bg-white/20 px-3 py-1 rounded-full">
                  ✨ AI-Powered Analysis
                </span>
              </div>
            </div>
          </div>
          <div className="flex space-x-3">
            <button 
              onClick={exportToPDF}
              className="bg-white/20 hover:bg-white/30 backdrop-blur-sm text-white px-6 py-3 rounded-lg font-medium flex items-center transition-all duration-200 hover:scale-105"
            >
              <Download className="w-4 h-4 mr-2" />
              Export PDF
            </button>
            <button 
              onClick={() => window.location.href = '/'}
              className="bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white px-6 py-3 rounded-lg font-medium transition-all duration-200"
            >
              New Analysis
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search transcripts, summaries, or topics..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          {/* Topic Filter */}
          <div className="lg:w-80">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <select
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onChange={(e) => e.target.value && toggleTopic(e.target.value)}
                value=""
              >
                <option value="">Filter by topic...</option>
                {getAllTopics().map(topic => (
                  <option key={topic} value={topic}>{topic}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Selected Topics */}
        {selectedTopics.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {selectedTopics.map(topic => (
              <span
                key={topic}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 cursor-pointer"
                onClick={() => toggleTopic(topic)}
              >
                {topic}
                <span className="ml-1 text-blue-600">×</span>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Enhanced Timeline */}
      <div className="space-y-8">
        {filteredSegments.map((segment, index) => (
          <div 
            key={segment.id} 
            className="timeline-card bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden slide-up"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className="flex flex-col lg:flex-row">
              {/* Screenshot Section */}
              <div className="lg:w-96 flex-shrink-0 relative">
                <div className="relative group">
                  <img
                    src={segment.screenshot_path}
                    alt={`Screenshot at ${segment.formatted_time_range}`}
                    className="w-full h-64 lg:h-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div className="absolute top-4 left-4">
                    <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                      #{index + 1}
                    </span>
                  </div>
                  <div className="absolute bottom-4 left-4 right-4">
                    <div className="flex items-center justify-between text-white">
                      <div className="flex items-center bg-black/30 backdrop-blur-sm px-3 py-1 rounded-full">
                        <Clock className="w-4 h-4 mr-2" />
                        <span className="font-medium">{segment.formatted_time_range}</span>
                      </div>
                      <div className="bg-green-500/80 backdrop-blur-sm px-3 py-1 rounded-full text-sm">
                        {Math.round(segment.confidence_score)}% confidence
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Content Section */}
              <div className="flex-1 p-8">
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-2xl font-bold text-gray-900">
                      Screen Analysis #{index + 1}
                    </h3>
                    <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                      {segment.duration?.toFixed(1)}s duration
                    </span>
                  </div>
                  
                  {segment.summary && segment.summary !== "No discussion - Visual only" && 
                   !segment.summary.includes("[Audio detected") ? (
                    <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg mb-6">
                      <h4 className="font-semibold text-blue-900 mb-2">💡 Discussion Summary</h4>
                      <p className="text-blue-800 leading-relaxed">
                        {segment.summary}
                      </p>
                    </div>
                  ) : segment.summary && segment.summary.includes("[Audio detected") ? (
                    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg mb-6">
                      <h4 className="font-semibold text-yellow-900 mb-2">🔊 Audio Processing</h4>
                      <p className="text-yellow-800">
                        Audio detected - processing with speech recognition...
                      </p>
                    </div>
                  ) : (
                    <div className="bg-gray-50 border-l-4 border-gray-300 p-4 rounded-r-lg mb-6">
                      <h4 className="font-semibold text-gray-700 mb-2">👁️ Visual Content Only</h4>
                      <p className="text-gray-600">
                        Screen content detected without accompanying discussion.
                      </p>
                    </div>
                  )}
                </div>

                {/* Topics */}
                {segment.key_topics && segment.key_topics.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                      🏷️ Key Topics
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {segment.key_topics.map(topic => (
                        <span
                          key={topic}
                          className="inline-flex items-center px-3 py-1 bg-gradient-to-r from-purple-100 to-blue-100 text-purple-800 text-sm rounded-full font-medium hover:from-purple-200 hover:to-blue-200 transition-colors duration-200"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Transcript */}
                <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl p-6 border border-gray-200">
                  <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                    <FileText className="w-4 h-4 mr-2 text-blue-600" />
                    📝 Transcript
                  </h4>
                  {segment.transcript && segment.transcript.trim() && 
                   !segment.transcript.includes("[Audio detected - transcript not available") ? (
                    <blockquote className="text-gray-700 italic border-l-4 border-blue-400 pl-4 leading-relaxed">
                      "{segment.transcript}"
                    </blockquote>
                  ) : segment.transcript && segment.transcript.includes("[Audio detected") ? (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <p className="text-yellow-800 text-sm flex items-center">
                        <span className="mr-2">🔊</span>
                        Audio detected but transcript requires speech recognition service (Groq API key needed)
                      </p>
                    </div>
                  ) : (
                    <p className="text-gray-500 italic">
                      No audio detected for this segment.
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredSegments.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">
            No segments match your current filters.
          </div>
          <button
            onClick={() => {
              setSearchTerm('');
              setSelectedTopics([]);
            }}
            className="mt-4 text-blue-600 hover:text-blue-800 font-medium"
          >
            Clear all filters
          </button>
        </div>
      )}
    </div>
  );
};

export default Timeline;
