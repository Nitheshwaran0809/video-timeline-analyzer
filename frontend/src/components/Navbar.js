import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Link to="/">
                <h1 className="text-xl font-bold text-gray-900">
                  <span className="text-blue-600">Video</span> Timeline Analyzer
                </h1>
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Link 
              to="/" 
              className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              Home
            </Link>
            <button 
              className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
              onClick={() => alert('About section coming soon!')}
            >
              About
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
