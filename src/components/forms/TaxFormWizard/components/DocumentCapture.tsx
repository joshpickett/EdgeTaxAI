import React, { useState, useRef } from 'react';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';

interface DocumentCaptureProps {
  onCapture: (file: File) => Promise<void>;
  onError: (error: string) => void;
  acceptedTypes?: string[];
  maxSize?: number;
}

export const DocumentCapture: React.FC<DocumentCaptureProps> = ({
  onCapture,
  onError,
  acceptedTypes = ['image/jpeg', 'image/png', 'application/pdf'],
  maxSize = 10 * 1024 * 1024 // 10MB
}) => {
  const [isCapturing, setIsCapturing] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!acceptedTypes.includes(file.type)) {
      onError('Invalid file type');
      return;
    }

    if (file.size > maxSize) {
      onError('File size too large');
      return;
    }

    try {
      const preview = await generatePreview(file);
      setPreview(preview);
      await onCapture(file);
    } catch (error) {
      onError('Error processing file');
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCapturing(true);
      }
    } catch (error) {
      onError('Error accessing camera');
    }
  };

  const captureImage = async () => {
    if (!videoRef.current) return;

    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    
    if (!ctx) return;
    
    ctx.drawImage(videoRef.current, 0, 0);
    
    canvas.toBlob(async (blob) => {
      if (!blob) return;
      
      const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
      setPreview(URL.createObjectURL(blob));
      await onCapture(file);
      stopCamera();
    }, 'image/jpeg');
  };

  const stopCamera = () => {
    const stream = videoRef.current?.srcObject as MediaStream;
    stream?.getTracks().forEach(track => track.stop());
    setIsCapturing(false);
  };

  const generatePreview = (file: File): Promise<string> => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result as string);
      reader.readAsDataURL(file);
    });
  };

  return (
    <div style={formSectionStyles.container}>
      <div style={formFieldStyles.group}>
        <div style={formFieldStyles.row}>
          <button
            onClick={() => fileInputRef.current?.click()}
            style={formFieldStyles.button.primary}
          >
            Upload Document
          </button>
          <button
            onClick={startCamera}
            style={formFieldStyles.button.secondary}
          >
            Use Camera
          </button>
        </div>

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept={acceptedTypes.join(',')}
          style={{ display: 'none' }}
        />

        {isCapturing && (
          <div style={formFieldStyles.container}>
            <video
              ref={videoRef}
              autoPlay
              style={{ width: '100%', maxWidth: '500px' }}
            />
            <button
              onClick={captureImage}
              style={formFieldStyles.button.primary}
            >
              Capture
            </button>
            <button
              onClick={stopCamera}
              style={formFieldStyles.button.secondary}
            >
              Cancel
            </button>
          </div>
        )}

        {preview && (
          <div style={formFieldStyles.container}>
            <img
              src={preview}
              alt="Document preview"
              style={{ width: '100%', maxWidth: '500px' }}
            />
          </div>
        )}
      </div>
    </div>
  );
};
