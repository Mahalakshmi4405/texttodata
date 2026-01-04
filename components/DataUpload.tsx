// Data Upload Component

'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileCheck, AlertCircle, Loader2 } from 'lucide-react';
import { dataAPI } from '@/lib/api';
import { useAppStore } from '@/lib/store';

interface DataUploadProps {
    sessionId: number;
    onUploadComplete: (profile: any) => void;
}

export default function DataUpload({ sessionId, onUploadComplete }: DataUploadProps) {
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [message, setMessage] = useState('');
    const { setDataProfile } = useAppStore();

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        if (acceptedFiles.length === 0) return;

        const file = acceptedFiles[0];
        setUploading(true);
        setUploadStatus('idle');
        setMessage('');

        try {
            const response = await dataAPI.upload(sessionId, file);

            setUploadStatus('success');
            setMessage(`Successfully uploaded ${file.name} with ${response.row_count} rows`);

            if (response.profile) {
                setDataProfile(response.profile);
                onUploadComplete(response.profile);
            }
        } catch (error: any) {
            setUploadStatus('error');
            setMessage(error.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
        }
    }, [sessionId, setDataProfile, onUploadComplete]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv'],
            'application/vnd.ms-excel': ['.xls'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
            'application/json': ['.json'],
            'application/sql': ['.sql'],
            'application/x-parquet': ['.parquet'],
        },
        maxFiles: 1,
        disabled: uploading,
    });

    return (
        <div className="w-full">
            <div
                {...getRootProps()}
                className={`
          relative overflow-hidden rounded-xl border-2 border-dashed p-12 
          transition-all duration-300 cursor-pointer
          ${isDragActive
                        ? 'border-primary-400 bg-primary-500/10'
                        : 'border-dark-700 hover:border-primary-500 bg-dark-800/30'
                    }
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
            >
                <input {...getInputProps()} />

                <div className="flex flex-col items-center justify-center text-center">
                    {uploading ? (
                        <Loader2 className="w-12 h-12 text-primary-400 animate-spin mb-4" />
                    ) : uploadStatus === 'success' ? (
                        <FileCheck className="w-12 h-12 text-green-400 mb-4" />
                    ) : uploadStatus === 'error' ? (
                        <AlertCircle className="w-12 h-12 text-red-400 mb-4" />
                    ) : (
                        <Upload className="w-12 h-12 text-dark-400 mb-4" />
                    )}

                    <h3 className="text-xl font-semibold text-white mb-2">
                        {uploading ? 'Uploading & Analyzing...' : 'Upload Your Data'}
                    </h3>

                    <p className="text-dark-400 mb-4">
                        {isDragActive
                            ? 'Drop the file here...'
                            : 'Drag & drop a file here, or click to select'}
                    </p>

                    <div className="flex flex-wrap gap-2 justify-center">
                        {['CSV', 'Excel', 'JSON', 'SQL', 'Parquet'].map((format) => (
                            <span
                                key={format}
                                className="px-3 py-1 text-xs rounded-full bg-dark-700 text-dark-300"
                            >
                                {format}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Animated background gradient */}
                <div className="absolute inset-0 -z-10 opacity-20">
                    <div className="absolute inset-0 bg-gradient-to-r from-primary-500 via-purple-500 to-pink-500 blur-3xl animate-pulse-slow"></div>
                </div>
            </div>

            {message && (
                <div
                    className={`
            mt-4 p-4 rounded-lg border animate-slide-up
            ${uploadStatus === 'success'
                            ? 'bg-green-500/10 border-green-500/30 text-green-400'
                            : 'bg-red-500/10 border-red-500/30 text-red-400'
                        }
          `}
                >
                    {message}
                </div>
            )}
        </div>
    );
}
